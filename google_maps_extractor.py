#!/usr/bin/env python3
"""
Google Maps Image Extractor

A tool to automatically extract and download ALL images from a Google Maps
place listing. It opens the place page, clicks into the photo gallery, scrolls
through the lazily-loaded grid until every photo is loaded, then downloads
each photo at its original resolution. Downloads run in parallel
(--workers, default 8) so large galleries finish much faster. After
downloading, exact duplicates (identical file content) are detected by
hashing and removed automatically.

The photo gallery is rendered by the browser in visible mode by default.
Headless mode (--headless) works too: the script presents a regular Chrome
user agent (headless Chrome advertises "HeadlessChrome" by default, which
makes Google serve a degraded page without the photo gallery), so use
--headless on servers / CI environments without a display.

Author: Your Name
License: MIT
"""

import argparse
import hashlib
import io
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import unquote, urlparse, urlencode, parse_qsl, urlunparse

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
# Photo URLs look like https://lh5.googleusercontent.com/p/AF1Qip...=w320-h240-k-no
# or https://lh3.googleusercontent.com/gps-cs-s/AHRPTW...=w408-h306-k-no
PHOTO_HOST_RE = re.compile(r'^https?://lh\d\.googleusercontent\.com/', re.I)
WIDTH_IN_URL_RE = re.compile(r'=w(\d+)', re.I)
SIZE_SUFFIX_RE = re.compile(r'=w\d+.*$|=[sp]\d+.*$', re.I)
BG_IMAGE_RE = re.compile(r'url\(\s*["\']?(https?://[^)"\']+)["\']?\s*\)', re.I)
AVATAR_RE = re.compile(r'googleusercontent\.com/(a|a-)/', re.I)

# Non-photo assets to filter out (Google UI icons, map tiles, reviewer
# avatars, placeholders, ...)
SKIP_PATTERNS = (
    'gstatic.com',
    '/maps/vt',            # map tiles (any google.<tld>)
    'mt.googleapis.com',
    'streetviewpixels',    # tiny street-view thumbnails (100x75 previews)
    'ogw/default-user',    # default avatar placeholder
    'data:image',
    '/favicon',
    'logo',
    'marker',
    'avatar',
    'policies',
)

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/148.0.0.0 Safari/537.36'),
    'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
}

CONTENT_TYPE_EXT = {
    'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png',
    'image/webp': 'webp', 'image/gif': 'gif', 'image/avif': 'avif',
    'image/bmp': 'bmp',
}
PIL_FORMAT_EXT = {
    'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp', 'GIF': 'gif',
    'AVIF': 'avif', 'BMP': 'bmp',
}

# Downloads are I/O-bound, so a handful of parallel workers speeds up large
# galleries without hammering Google's servers.
DOWNLOAD_WORKERS = 8

_print_lock = threading.Lock()


def _thread_safe_print(*args, **kwargs):
    """Print without interleaved lines from parallel download workers."""
    with _print_lock:
        print(*args, **kwargs)


CONSENT_ACCEPT_TEXTS = ('Accept all', 'Accetta tutto', 'Aceptar todo',
                        'Tout accepter', 'Alle akzeptieren')

GALLERY_ITEM_XPATH = "//a[starts-with(@aria-label, 'Photo ')]"
HERO_XPATH = "//button[starts-with(@aria-label, 'Photo of')]"
SEE_PHOTOS_XPATH = "//button[.//*[contains(text(),'See photos')]]"


# --------------------------------------------------------------------------- #
# Extractor
# --------------------------------------------------------------------------- #
class GoogleMapsImageExtractor:
    """Main class for extracting images from Google Maps place listings."""

    def __init__(self, headless: bool = False, workers: int = DOWNLOAD_WORKERS):
        """
        Initialize the extractor.

        Args:
            headless (bool): Run Chrome headless. Works because the script
                overrides the headless user agent (see setup_driver).
            workers (int): Number of parallel download workers.
        """
        self.headless = headless
        self.workers = max(1, workers)
        self.driver = None

    # --------------------------- browser setup --------------------------- #
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless=new')
            # Headless Chrome advertises "HeadlessChrome" in its user agent,
            # which makes Google serve a degraded Maps page without the photo
            # gallery (no hero / "Photo of ..." button). Present the regular
            # Chrome UA instead so the gallery renders in headless mode too.
            options.add_argument(f'--user-agent={HEADERS["User-Agent"]}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--lang=en-US')
        options.add_argument('--window-size=1920,1080')
        # Look less like an automation target: hides the "Chrome is being
        # controlled by automated software" banner that can change the layout.
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # Selenium Manager (bundled with selenium >= 4.11) automatically
        # downloads and caches the chromedriver matching the installed
        # Chrome/Chromium version - no manual driver management needed.
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(60)

    def _accept_cookies_if_present(self, target_url: str) -> bool:
        """
        Dismiss the EU cookie-consent wall (any language) and get back to the
        place page. Returns True once we are past the consent page.
        """
        for _ in range(6):
            if 'consent.google' not in self.driver.current_url:
                return True
            clicked = False
            for button in self.driver.find_elements(By.TAG_NAME, 'button'):
                text = (button.text or '') + ' ' + (button.get_attribute('aria-label') or '')
                if any(k in text for k in CONSENT_ACCEPT_TEXTS):
                    try:
                        self.driver.execute_script("arguments[0].click();", button)
                        clicked = True
                        break
                    except Exception:
                        continue
            if not clicked:
                self.driver.get(target_url)
            time.sleep(3)
        return 'consent.google' not in self.driver.current_url

    @staticmethod
    def _with_hl(url: str) -> str:
        """Force an English UI (hl=en) so aria-labels are predictable."""
        parts = urlparse(url)
        query = dict(parse_qsl(parts.query))
        query['hl'] = 'en'
        return urlunparse(parts._replace(query=urlencode(query)))

    # --------------------------- page navigation -------------------------- #
    def _click_hero(self) -> bool:
        """
        Open the photo gallery by clicking the hero 'Photo of ...' button.
        The hero can take a few seconds to render (especially in headless
        mode), so poll for it. Gives up early when the page clearly has no
        photo controls at all (e.g. a place with no gallery).
        """
        deadline = time.time() + 10
        idle = 0
        while time.time() < deadline:
            found_any = False
            for xpath in (HERO_XPATH, SEE_PHOTOS_XPATH):
                try:
                    candidates = self.driver.find_elements(By.XPATH, xpath)
                except Exception:
                    continue
                if candidates:
                    found_any = True
                for button in candidates:
                    try:
                        if not button.is_displayed():
                            continue
                        self.driver.execute_script("arguments[0].click();", button)
                    except Exception:
                        continue  # element went stale mid-poll; try next round
                    time.sleep(1.2)
                    return True
            if not found_any:
                idle += 1
                if idle >= 4:
                    # No hero / 'See photos' control exists in the DOM, so
                    # the gallery is not reachable from this page.
                    break
            else:
                idle = 0
            time.sleep(0.75)
        return False

    def _click_all_tab(self):
        """Make sure the 'All' photo tab is selected in the gallery."""
        try:
            for tab in self.driver.find_elements(By.XPATH, "//*[@role='tab']"):
                label = (tab.get_attribute('aria-label') or tab.text or '').strip()
                if label == 'All' or label.startswith('All '):
                    if tab.get_attribute('aria-selected') != 'true':
                        self.driver.execute_script("arguments[0].click();", tab)
                        time.sleep(1.2)
                    return
        except Exception:
            pass

    def _scroll_to_load_all(self, max_rounds: int = 300) -> Set[str]:
        """
        Repeatedly scroll every scrollable container (photo grid, strips,
        page) until no new photo URLs appear for several consecutive rounds.
        The gallery is virtualized (items leave the DOM once scrolled past),
        so we ACCUMULATE URLs across rounds rather than keeping the last
        snapshot.

        Critically, the scroll is INCREMENTAL (a small step per round), not a
        single jump to the bottom: with virtualization the browser only renders
        rows near the current scroll position, so jumping to the end means the
        middle rows are never rendered at all and their URLs never reach the
        DOM.

        We never flip direction mid-pass: flipping on a temporary stall (a
        slow lazy-load batch) terminates the scan early and silently drops
        every photo below the current position. Instead we run three
        sequential passes — down, up (verification), down (verification) —
        each of which stops only once the scroll has stalled AND no new URLs
        have appeared AND the content has stopped growing, for several
        consecutive rounds.

        Returns:
            Set[str]: All photo URLs discovered so far
        """
        seen: Set[str] = set()
        failures = 0
        viewport = int(self.driver.execute_script("return window.innerHeight") or 800)
        step = max(viewport * 0.8, 500)

        def scroll_once(direction: int):
            """One incremental scroll step. Returns (max_delta, max_height)."""
            return self.driver.execute_script(
                """
                var step = arguments[0], dir = arguments[1], maxDelta = 0, maxHeight = 0;
                document.querySelectorAll('div, section').forEach(function (el) {
                    var dh = el.scrollHeight - el.clientHeight;
                    var dw = el.scrollWidth - el.clientWidth;
                    if (dh > 200 || dw > 200) {
                        var before = el.scrollTop;
                        el.scrollTop = before + step * dir;
                        var delta = el.scrollTop - before;
                        if (delta > maxDelta) maxDelta = delta;
                        if (el.scrollHeight > maxHeight) maxHeight = el.scrollHeight;
                    }
                });
                var docH = document.documentElement.scrollHeight || 0;
                if (docH > maxHeight) maxHeight = docH;
                var before = window.scrollY || document.documentElement.scrollTop || 0;
                window.scrollBy(0, step * dir);
                var wdelta = Math.abs(
                    (window.scrollY || document.documentElement.scrollTop || 0) - before);
                if (wdelta > maxDelta) maxDelta = wdelta;
                return [maxDelta, maxHeight];
                """,
                step, direction)

        def run_pass(direction: int, label: str, patience: int, min_rounds: int):
            nonlocal seen, failures
            idle_moved = 0      # consecutive rounds where nothing scrolled
            idle_urls = 0       # consecutive rounds with no new URLs
            idle_height = 0     # consecutive rounds the content stopped growing
            max_height = 0
            for round_no in range(max_rounds):
                try:
                    moved, new_height = scroll_once(direction)
                except Exception:
                    failures += 1
                    if failures >= 3:
                        print("  page seems to have gone away; stopping scroll")
                        return
                    time.sleep(2)
                    continue
                time.sleep(0.5)

                current = self._collect_photo_urls()
                new = current - seen
                if new:
                    print(f"  [{label}] loaded {len(new)} new photo URL(s) "
                          f"(total {len(seen | current)})")
                    seen |= current
                    idle_urls = 0
                else:
                    idle_urls += 1

                if moved < step * 0.3:
                    idle_moved += 1
                else:
                    idle_moved = 0

                # Track whether the content is still growing (a lazy-load batch
                # landing slowly keeps adding rows even when the last round
                # produced no new URLs yet).
                if new_height > max_height:
                    max_height = new_height
                    idle_height = 0
                else:
                    idle_height += 1

                if (round_no >= min_rounds
                        and idle_moved >= patience
                        and idle_urls >= patience
                        and idle_height >= patience):
                    break
            print(f"  [{label}] pass complete ({len(seen)} URL(s) total)")

        run_pass(1, "down", patience=5, min_rounds=6)
        run_pass(-1, "up", patience=3, min_rounds=3)
        run_pass(1, "down", patience=3, min_rounds=3)
        return seen

    # ---------------------------- gallery tabs ---------------------------- #
    def _gallery_tabs(self) -> List[Tuple[str, object]]:
        """
        Return the gallery's photo tabs ('All' first), skipping the panorama
        tab ('Street View & 360°'), which has no scrollable photo grid.
        """
        try:
            tabs = self.driver.find_elements(By.XPATH, "//*[@role='tab']")
        except Exception:
            return []
        labelled: List[Tuple[str, object]] = []
        for tab in tabs:
            label = (tab.get_attribute('aria-label') or tab.text or '').strip()
            if not label:
                continue
            lower = label.lower()
            if 'street view' in lower or '360' in lower:
                continue
            labelled.append((label, tab))
        # 'All' first, then the rest alphabetically for a deterministic order.
        labelled.sort(key=lambda lt: (lt[0] != 'All', lt[0]))
        return labelled

    def _collect_all_tabs(self) -> Set[str]:
        """
        Scroll the photo grid under EVERY gallery tab and union the URLs.
        Google can anchor the viewer on different media (regular photos vs
        360° shots) and render different grids per tab, so a single-tab scan
        can miss photos. The 'All' tab usually covers everything, but walking
        the other tabs is a cheap safety net against silently skipped rows.
        """
        all_urls: Set[str] = set()
        tabs = self._gallery_tabs()
        if not tabs:
            return self._scroll_to_load_all()
        for idx, (label, tab) in enumerate(tabs, 1):
            print(f"Scrolling gallery tab {label!r} ({idx}/{len(tabs)})...")
            try:
                if tab.get_attribute('aria-selected') != 'true':
                    self.driver.execute_script("arguments[0].click();", tab)
                    time.sleep(1.5)
            except Exception:
                continue
            urls = self._scroll_to_load_all()
            print(f"  tab {label!r} yielded {len(urls)} URL(s)")
            all_urls |= urls
            # Reset scroll positions so the next tab starts from the top.
            try:
                self.driver.execute_script(
                    "document.querySelectorAll('div,section').forEach(function(el){"
                    "el.scrollTop = 0;}); window.scrollTo(0, 0);")
            except Exception:
                pass
            time.sleep(0.4)
        return all_urls

    # --------------------------- viewer sweep ----------------------------- #
    def _open_viewer(self) -> bool:
        """
        Click the first visible photo in the gallery to open the full-screen
        photo viewer (lightbox), which loads photos one at a time.
        """
        for xpath in (GALLERY_ITEM_XPATH,
                      "//a[contains(@aria-label, 'Photo')]",
                      "//img[contains(@src, 'googleusercontent')]"):
            try:
                for el in self.driver.find_elements(By.XPATH, xpath):
                    if el.is_displayed():
                        self.driver.execute_script("arguments[0].click();", el)
                        time.sleep(1.2)
                        return True
            except Exception:
                continue
        return False

    def _viewer_snapshot(self) -> Set[str]:
        """Photo-host URLs currently in the DOM (the viewer's main photo plus
        any filmstrip/grid thumbnails rendered around it)."""
        return {u for u in self._collect_photo_urls()
                if PHOTO_HOST_RE.match(u) and not self.should_skip_image(u)}

    def _collect_viewer_photos(self, max_steps: int = 1000,
                               change_timeout: float = 4.0) -> Set[str]:
        """
        Step through the full-screen photo viewer photo by photo (arrow keys)
        and collect the URL of every photo. The virtualized grid can silently
        skip rows, but the viewer loads one photo at a time, so walking it
        complements the grid pass and fills any gaps.

        After each arrow press we POLL until the displayed photo actually
        changes (or `change_timeout` seconds elapse), so a slow connection
        cannot fool us into stopping early. The walk stops when navigation
        stops changing the photo (first/last photo) or when only already-known
        photos appear (full cycle back to the start).

        Returns:
            Set[str]: All photo URLs collected from the viewer.
        """
        urls: Set[str] = set()
        if not self._open_viewer():
            return urls

        body = self.driver.find_element(By.TAG_NAME, 'body')
        last_sig: Optional[Set[str]] = None

        def press_and_wait(key, timeout: float = change_timeout) -> Optional[Set[str]]:
            """Press a navigation key and wait for the displayed photo to
            change. Returns the new snapshot, or None if nothing changed
            within `timeout` seconds."""
            body.send_keys(key)
            for _ in range(max(1, int(timeout / 0.3))):
                time.sleep(0.3)
                sig = self._viewer_snapshot()
                if sig and sig != last_sig:
                    return sig
            return None

        # Back up to the very first photo so the forward pass below covers the
        # whole gallery even if we opened the viewer on a later photo.
        for _ in range(30):
            sig = self._viewer_snapshot()
            urls |= sig
            last_sig = sig
            changed = press_and_wait(Keys.ARROW_LEFT, timeout=2.0)
            if changed is None:
                break          # left no longer moves: we are at the first photo
            urls |= changed
            last_sig = changed

        # Walk forward photo by photo, collecting each one's URLs.
        non_growing = 0        # consecutive steps that added no new URL
        steps = 0
        while steps < max_steps:
            changed = press_and_wait(Keys.ARROW_RIGHT)
            if changed is None:
                break          # right no longer moves: last photo (or viewer closed)
            before_len = len(urls)
            urls |= changed
            if len(urls) == before_len:
                non_growing += 1
            else:
                non_growing = 0
            if non_growing >= 3:
                break          # only already-seen photos: full cycle complete
            last_sig = changed
            steps += 1

        # Close the viewer so the page is left in a clean state.
        try:
            body.send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return urls

    # --------------------------- URL collection --------------------------- #
    def _collect_photo_urls(self) -> Set[str]:
        """
        Collect every image URL currently in the DOM in ONE JavaScript pass.
        The old implementation made hundreds of WebDriver round-trips per call
        (one find_elements + one get_attribute per <img> attribute), which made
        every scroll round and every viewer snapshot take seconds. A single
        execute_script returns the whole list in a few milliseconds.
        """
        try:
            js_urls = self.driver.execute_script(
                r"""
                var urls = [], seen = {};
                function add(u) {
                    if (u && u.slice(0, 4) === 'http' && !seen[u]) {
                        seen[u] = 1;
                        urls.push(u);
                    }
                }
                // <img> src / data-src
                document.querySelectorAll('img').forEach(function (img) {
                    add(img.getAttribute('src'));
                    add(img.getAttribute('data-src'));
                    // srcset: keep the highest-width candidate (same rule as
                    // the old Python helper).
                    var ss = img.getAttribute('srcset');
                    if (ss) {
                        var best = null, bw = -1;
                        ss.split(',').forEach(function (c) {
                            var p = c.trim().split(/\s+/);
                            if (!p.length) return;
                            var w = 0;
                            if (p.length > 1 && /w$/.test(p[1])) {
                                w = parseInt(p[1], 10) || 0;
                            }
                            if (w >= bw) { bw = w; best = p[0]; }
                        });
                        if (best) add(best);
                    }
                });
                // CSS background-image URLs (gallery thumbnails are often divs).
                var re = /url\(\s*["']?(https?:\/\/[^)"']+)["']?\s*\)/gi;
                document.querySelectorAll('[style]').forEach(function (el) {
                    var css = el.getAttribute('style') || '';
                    var m;
                    while ((m = re.exec(css)) !== null) add(m[1]);
                });
                return urls;
                """)
            return {u for u in js_urls if u}
        except Exception:
            return set()

    @staticmethod
    def should_skip_image(img_url: str) -> bool:
        """
        Check if an image URL is a UI asset / non-photo rather than a
        user-contributed photo of the place.
        """
        lower = img_url.lower()
        return bool(AVATAR_RE.search(lower)) or \
            any(pattern in lower for pattern in SKIP_PATTERNS)

    def _filter_and_dedupe(self, urls: Set[str]) -> List[str]:
        """
        Drop junk URLs and deduplicate photos served in several thumbnail
        sizes, keeping the highest-resolution variant of each photo.
        Only googleusercontent photo hosts are considered.
        """
        best: Dict[str, Tuple[int, str]] = {}
        for url in urls:
            if not PHOTO_HOST_RE.match(url) or self.should_skip_image(url):
                continue
            match = WIDTH_IN_URL_RE.search(url)
            width = int(match.group(1)) if match else 0
            base = SIZE_SUFFIX_RE.sub('', url)
            if base not in best or width > best[base][0]:
                best[base] = (width, url)
        return [url for _, url in best.values()]

    @staticmethod
    def _original_photo_url(url: str) -> str:
        """
        Rewrite a sized googleusercontent URL (=w320-h240-k-no / =s512-...)
        to =s0, which serves the photo at its original resolution.
        """
        if PHOTO_HOST_RE.match(url) and '=' in url:
            base, params = url.rsplit('=', 1)
            if params.startswith(('w', 's')):
                return base + '=s0'
        return url

    # ----------------------------- downloading ---------------------------- #
    @staticmethod
    def _detect_extension(content: bytes, content_type: str) -> Optional[str]:
        """
        Determine a sensible file extension from headers / image content.
        Returns None if the payload does not look like an image.
        """
        if content_type:
            ctype = content_type.split(';')[0].strip().lower()
            if ctype in CONTENT_TYPE_EXT:
                return CONTENT_TYPE_EXT[ctype]
        try:
            fmt = Image.open(io.BytesIO(content)).format
            if fmt and fmt in PIL_FORMAT_EXT:
                return PIL_FORMAT_EXT[fmt]
        except Exception:
            pass
        return None

    def download_image(self, url: str, output_folder: str,
                       place_name: str, idx: int) -> bool:
        """
        Download a single photo at full resolution and save it as-is
        (no re-encoding, no resizing). One retry on transient failure.

        Returns:
            bool: True if the image was saved, False otherwise
        """
        full_url = self._original_photo_url(url)
        headers = dict(HEADERS)
        headers['Referer'] = 'https://www.google.com/maps'

        for attempt in range(2):
            try:
                response = requests.get(full_url, headers=headers, timeout=30)
                response.raise_for_status()
                content = response.content
                if len(content) < 200:
                    return False

                ext = self._detect_extension(
                    content, response.headers.get('Content-Type', ''))
                if ext is None:
                    # Not an image (e.g. an HTML error page) - don't save it.
                    _thread_safe_print(
                        f"  {full_url[:90]}... is not a valid image, skipping")
                    return False

                output_path = os.path.join(output_folder,
                                           f"{place_name}_{idx:04d}.{ext}")
                with open(output_path, 'wb') as fh:
                    fh.write(content)
                _thread_safe_print(
                    f"  saved: {output_path} ({len(content) / 1024:.0f} KB)")
                return True
            except Exception as exc:
                if attempt == 0:
                    time.sleep(1)
                    continue
                _thread_safe_print(f"  failed to download {full_url}: {exc}")
                return False
        return False

    # ---------------------------- deduplication --------------------------- #
    @staticmethod
    def _file_sha256(path: str) -> Optional[str]:
        """SHA-256 digest of a file's content, or None if it cannot be read."""
        try:
            digest = hashlib.sha256()
            with open(path, 'rb') as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b''):
                    digest.update(chunk)
            return digest.hexdigest()
        except OSError:
            return None

    def _remove_duplicate_photos(self, output_folder: str) -> int:
        """
        Hash every downloaded image and delete exact duplicates (identical
        file content), keeping the first file of each unique hash. Cleans up
        cases where the same photo was reachable under several URLs.

        Returns:
            int: Number of duplicate files removed.
        """
        try:
            names = sorted(n for n in os.listdir(output_folder)
                           if os.path.isfile(os.path.join(output_folder, n)))
        except OSError:
            return 0

        seen: Dict[str, str] = {}
        removed = 0
        for name in names:
            path = os.path.join(output_folder, name)
            digest = self._file_sha256(path)
            if digest is None:
                continue
            if digest in seen:
                try:
                    os.remove(path)
                    removed += 1
                    print(f"  duplicate removed: {name} (identical to {seen[digest]})")
                except OSError:
                    pass
            else:
                seen[digest] = name
        return removed

    # --------------------------- main workflow ---------------------------- #
    def extract_place_name(self, url: str) -> str:
        """
        Extract a filesystem-safe place name from a Google Maps URL,
        falling back to the page title.
        """
        name = ''
        match = re.search(r'/maps/place/([^/@]+)', url)
        if match:
            name = unquote(match.group(1)).replace('+', ' ')
        name = re.sub(r'[^\w\s-]', '', name).strip()
        if not name and self.driver is not None:
            title = self.driver.title or ''
            title = re.sub(r'\s*-\s*Google Maps.*$', '', title).strip()
            name = re.sub(r'[^\w\s-]', '', title)
        name = re.sub(r'\s+', '_', name) if name else 'google_maps_place'
        return name

    def process_google_maps_images(self, url: str) -> Optional[str]:
        """
        Download every photo from a Google Maps place page.

        Args:
            url (str): Google Maps place URL

        Returns:
            Optional[str]: Output folder path if successful, None otherwise
        """
        try:
            self.setup_driver()
            url = self._with_hl(url)
            self.driver.get(url)
            self._accept_cookies_if_present(url)
            time.sleep(2)

            place_name = self.extract_place_name(url)
            print(f"Processing: {place_name}")

            output_folder = place_name
            os.makedirs(output_folder, exist_ok=True)

            # 1) Open the photo gallery through the hero image / "See photos".
            gallery_opened = self._click_hero()
            if gallery_opened:
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located(
                            (By.XPATH, GALLERY_ITEM_XPATH)))
                except Exception:
                    print("  gallery did not open, falling back to page scrape")
                    self.driver.get(url)
                    time.sleep(3)
                    gallery_opened = False
                else:
                    self._click_all_tab()

            # 2) Scroll every gallery tab until all lazy-loaded photos have
            #    been discovered. Google can anchor the viewer on different
            #    media and virtualize the grid, so a single shallow pass
            #    silently misses most photos.
            if gallery_opened:
                print("Scrolling every gallery tab to load all photos...")
                raw_urls = self._collect_all_tabs()
            else:
                print("Scrolling to load all photos...")
                raw_urls = self._scroll_to_load_all()
            print(f"Found {len(raw_urls)} raw image URL(s)")

            # 3) Extra pass: step through the photo viewer one photo at a time.
            #    The virtualized grid can silently skip rows; the viewer loads
            #    photos individually, so this fills any gaps the scroll pass
            #    missed.
            if gallery_opened:
                print("Stepping through the photo viewer for a complete set...")
                viewer_urls = self._collect_viewer_photos()
                if viewer_urls:
                    new_ones = viewer_urls - raw_urls
                    print(f"  viewer pass collected {len(viewer_urls)} URL(s) "
                          f"({len(new_ones)} new)")
                    raw_urls |= viewer_urls

            photo_urls = self._filter_and_dedupe(raw_urls)
            if not photo_urls:
                print("No photos found. Page title:", self.driver.title)
                print("Page source snippet:")
                print(self.driver.page_source[:1000])
                return None

            print(f"Downloading {len(photo_urls)} unique photo(s) "
                  f"with {self.workers} parallel worker(s)...")
            successful = 0
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                futures = [pool.submit(self.download_image, photo_url,
                                       output_folder, place_name, idx)
                           for idx, photo_url in enumerate(photo_urls, 1)]
                for future in as_completed(futures):
                    try:
                        if future.result():
                            successful += 1
                    except Exception:
                        pass

            # 4) Remove exact duplicates (identical file content).
            removed_dupes = self._remove_duplicate_photos(output_folder)
            if removed_dupes:
                print(f"Removed {removed_dupes} duplicate image(s).")

            print(f"Processing complete! Downloaded {successful} image(s) "
                  f"({successful - removed_dupes} unique after deduplication).")
            print(f"Check the folder: {output_folder}")
            return output_folder

        except Exception as exc:
            print(f"Error during processing: {exc}")
            return None
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def is_valid_maps_url(url: str) -> bool:
    """Accept any google.* / maps.google.com place URL."""
    return bool(re.search(r'google\.[a-z.]{2,}/maps/place/', url, re.I)) or \
        bool(re.search(r'maps\.google\.\w+/place/', url, re.I))


def main():
    """Main function to run the image extractor."""
    parser = argparse.ArgumentParser(
        description='Extract and download all images from a Google Maps place listing')
    parser.add_argument('url', nargs='?', help='Google Maps place URL to extract images from')
    parser.add_argument('--headless', action='store_true',
                        help='Run Chrome headless (no visible window; '
                             'suitable for servers/CI)')
    parser.add_argument('--no-headless', action='store_true',
                        help='Run browser in visible mode (default)')
    parser.add_argument('--workers', type=int, default=DOWNLOAD_WORKERS,
                        help='Number of parallel download workers '
                             f'(default: {DOWNLOAD_WORKERS})')
    parser.add_argument('--example', action='store_true', help='Run with an example URL')

    args = parser.parse_args()

    if args.example or not args.url:
        maps_url = "https://www.google.com/maps/place/Il+Gigante+che+dorme+-+Bed+and+Breakfast/@42.5374855,13.6955344,17z/data=!4m9!3m8!1s0x1331db27aedf4661:0xbd0f99782ad77817!5m2!4m1!1i2!8m2!3d42.5374816!4d13.6981093!16s%2Fg%2F12hmyxjch?entry=ttu&g_ep=EgoyMDI2MDgyNS4wIKXMDSoASAFQAw%3D%3D"
        print("Using example URL (Dott. Fabio Massimo Perotti)")
    else:
        maps_url = args.url

    if not maps_url.startswith('http'):
        maps_url = 'https://' + maps_url

    if not is_valid_maps_url(maps_url):
        print("Error: Invalid URL. Please provide a valid Google Maps place URL, "
              "e.g. https://www.google.com/maps/place/Some+Place/...")
        return

    extractor = GoogleMapsImageExtractor(
        headless=args.headless and not args.no_headless, workers=args.workers)
    extractor.process_google_maps_images(maps_url)


if __name__ == "__main__":
    main()

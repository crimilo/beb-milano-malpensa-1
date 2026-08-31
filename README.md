# B&B Milano Malpensa 1 — sito web

Sito web statico per **B&amp;B Milano Malpensa 1** (Castano Primo, MI), costruito con
[Astro](https://astro.build), **bilingue italiano (default) / inglese** e ottimizzato per
SEO locale (aeroporto di Malpensa, Castano Primo, Milano, lavoro e trasferte).

## Pagine (IT + EN)

| Percorso | Intento |
| --- | --- |
| `/` e `/en/` | Home hub: B&B a Castano Primo tra Milano e Malpensa |
| `/beb-per-lavoro/` e `/en/beb-per-lavoro/` | B&B per lavoro: trasferte, pendolari, aziende (FAQ + schema FAQPage) |
| `/beb-vicino-aeroporto-malpensa/` e `/en/…` | B&B con navetta e parcheggio per Malpensa (FAQPage) |
| `/beb-castano-primo/` e `/en/…` | B&B a Castano Primo (SEO locale, provincia di Milano) |
| `/camere/` e `/en/camere/` | Camere con **prezzi sempre visibili** e foto sotto ogni card |
| `/contatti/` e `/en/contatti/` | NAP, come arrivare, telefono e WhatsApp |

`/beb-canale-villoresi/` è stata rimossa e redirezionata (301, via `_redirects`) su
`/beb-per-lavoro/`, per spingere sul traffico business invece che sulla natura.

## Stack e ottimizzazioni

- **Astro 7** + `@astrojs/cloudflare` + `@astrojs/sitemap` (hreflang it/en + x-default)
- i18n: italiano default (`prefixDefaultLocale: false`), inglese sotto `/en/`, `hreflang` in `<head>` e sitemap
- Immagini **solo AVIF** (`public/photos/`), max 1400 px, q≈50; galleria a 1 colonna su mobile
- **3 font** in WOFF2 subsettati e inlined (Fraunces, Inter, Caveat): niente FOUT/CLS (`font-display: swap`, no preload)
- Lightbox a tap (zoom / de-zoom, sfondo scuro) su tutte le immagini
- Bottone WhatsApp circolare fisso con glow, header fixed con **un solo CTA** ("Chiama ora")
- **Prezzi template** (media zona Malpensa/Castano Primo): da €45 singola, da €60 doppia, da €75 tripla, da €90 quadrupla — sempre visibili su home, camere e pagine servizio
- Schema.org validi: `LodgingBusiness` (NAP, geo, rating 3.7/176, priceRange €45–€120) + `BreadcrumbList` + `FAQPage` + `WebSite`, per lingua
- Recensioni reali da Google (curate)
- `sitemap-index.xml`, `robots.txt` (allow all), favicon e OG image generati dal logo (monogramma M + swoosh)

## Sviluppo

```bash
bun install        # o npm install
bun run dev        # astro dev
bun run build      # astro build -> dist/
bun run preview    # build + preview
bun run deploy     # astro build + wrangler deploy (Cloudflare)
```

## Prima di andare in produzione

1. **Dominio**: sostituisci `https://beb-milano-malpensa-1.it` con il dominio reale in
   `src/data/site.ts` (`SITE.url`), `astro.config.mjs` (`site`) e `public/robots.txt`.
2. Controlla NAP, prezzi e recensioni in `src/data/site.ts`.
3. `wrangler.jsonc` è configurato per l'account Cloudflare di chi deploya.

## Struttura

```
src/
  data/          # dati centrali (NAP, i18n, prezzi, recensioni, foto, schema)
  components/    # Header (lang switch), Footer, Gallery, Reviews, CTA, lightbox…
  layouts/       # Layout con head SEO/OG/hreflang/schema
  pages/         # 6 pagine IT + 6 pagine EN (src/pages/en/)
  styles/        # global.css (design tokens, font inline)
public/
  photos/        # immagini AVIF
  fonts/         # font WOFF2 subsettati (source)
  favicon.*, og.jpg, robots.txt, site.webmanifest
```

Lighthouse locale (server a singolo thread, throttling simulato): perf 97–99,
accessibility / best-practices / SEO 100, CLS 0.

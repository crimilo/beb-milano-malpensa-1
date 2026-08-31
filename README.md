# B&B Milano Malpensa 1 — sito web

Sito web statico per **B&amp;B Milano Malpensa 1** (Castano Primo, MI), costruito con
[Astro](https://astro.build) e ottimizzato per SEO locale (aeroporto di Malpensa,
Castano Primo, Canale Villoresi, provincia di Milano).

## Pagine

| Percorso | Intento |
| --- | --- |
| `/` | Home hub: B&B a Castano Primo vicino a Malpensa |
| `/beb-vicino-aeroporto-malpensa/` | B&B con navetta e parcheggio per Malpensa (FAQ + schema FAQPage) |
| `/beb-castano-primo/` | B&B a Castano Primo (SEO locale, provincia di Milano) |
| `/beb-canale-villoresi/` | Ciclabile del Canale Villoresi, natura e Ticino |
| `/camere/` | Tipologie di camere, bagni privati e servizi |
| `/contatti/` | NAP, come arrivare, telefono e WhatsApp |

## Stack e ottimizzazioni

- **Astro 7** + `@astrojs/cloudflare` (deploy su Cloudflare Workers/Pages) + `@astrojs/sitemap`
- Immagini **solo AVIF** (`public/photos/`), ottimizzate (max 1400 px, q≈50)
- **3 famiglie di font** in WOFF2 subsettati al solo set di glifi usato e inlined
  nel CSS (`font-display: swap`, niente preload): Fraunces (titoli), Inter (testo),
  Caveat (accenti)
- Font inlined ⇒ niente FOUT/CLS da swap (CLS 0 in Lighthouse)
- Lightbox a tap (zoom / de-zoom, sfondo scuro) su tutte le immagini
- Bottone WhatsApp circolare fisso con glow, header fixed con **un solo CTA** ("Chiama ora")
- Schema.org: `LodgingBusiness` + `BreadcrumbList` + `FAQPage` + `WebSite` (validi)
- Recensioni reali da Google (curate, non inventate)
- `sitemap-index.xml`, `robots.txt` (allow all), favicon e OG image generati dal logo

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
   - `src/data/site.ts` → `SITE.url`
   - `astro.config.mjs` → `site`
   - `public/robots.txt` → `Sitemap:`
2. Controlla dati NAP (indirizzo/telefono) in `src/data/site.ts`.
3. `wrangler.jsonc` è configurato per l'account Cloudflare di chi deploya.

## Struttura

```
src/
  data/          # dati centrali (NAP, recensioni, foto, schema)
  components/    # Header, Footer, Gallery, Reviews, CTA, lightbox…
  layouts/       # Layout con head SEO/OG/schema
  pages/         # 6 pagine
  styles/        # global.css (design tokens, font inline)
public/
  photos/        # immagini AVIF
  fonts/         # font WOFF2 subsettati (source)
  favicon.*, og.jpg, robots.txt, site.webmanifest
```

Lighthouse locale (server a singolo thread, throttling simulato): perf 96,
accessibility / best-practices / SEO 100, CLS 0.

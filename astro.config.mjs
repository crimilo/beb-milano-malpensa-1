// @ts-check
import { defineConfig } from 'astro/config';

import cloudflare from '@astrojs/cloudflare';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://beb-milano-malpensa-1.it',
  adapter: cloudflare(),
  i18n: {
    defaultLocale: 'it',
    locales: ['it', 'en'],
    routing: { prefixDefaultLocale: false },
  },
  integrations: [
    sitemap({
      i18n: {
        defaultLocale: 'it',
        locales: { it: 'it-IT', en: 'en' },
      },
    }),
  ],
  redirects: {
    // Canale Villoresi page removed in favour of the business-travel focus.
    '/beb-canale-villoresi/': '/beb-per-lavoro/',
  },
  build: {
    inlineStylesheets: 'always',
  },
});

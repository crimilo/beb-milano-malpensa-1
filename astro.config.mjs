// @ts-check
import { defineConfig } from 'astro/config';

import cloudflare from '@astrojs/cloudflare';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://beb-milano-malpensa-1.it',
  adapter: cloudflare(),
  integrations: [sitemap()],
  build: {
    inlineStylesheets: 'always',
  },
});

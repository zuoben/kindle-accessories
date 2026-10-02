import { defineConfig } from 'astro/config';
import { SITE_URL } from './src/data/site.mjs';

export default defineConfig({
  site: SITE_URL,
  trailingSlash: 'always',
  output: 'static',
  build: { format: 'directory' },
});

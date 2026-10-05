import type { APIRoute } from 'astro';
import { SITE_URL, PUBLISHED, PUBLISHED_OCT5 } from '../data/site.mjs';

const newer = new Set(['/', '/kindle-paperwhite/', '/kindle-case/', '/kindle-paperwhite-case/', '/kindle-scribe-case/', '/kindle-cover/', '/kindle-sleeve/', '/kindle-stand/']);

const paths = ['/', '/kindle-paperwhite/', '/kindle-case/', '/kindle-paperwhite-case/', '/kindle-scribe-case/', '/kindle-cover/', '/kindle-sleeve/', '/kindle-stand/', '/faq/', '/about/', '/contact/', '/privacy/', '/affiliate-disclosure/'];

export const GET: APIRoute = () => {
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    paths.map((p) => `  <url><loc>${new URL(p, SITE_URL).toString()}</loc><lastmod>${newer.has(p) ? PUBLISHED_OCT5 : PUBLISHED}</lastmod></url>`).join('\n') +
    `\n</urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};

import type { APIRoute } from 'astro';
import { SITE_URL, PUBLISHED } from '../data/site.mjs';

const paths = ['/', '/kindle-paperwhite/', '/kindle-case/', '/kindle-paperwhite-case/', '/kindle-scribe-case/', '/faq/', '/about/', '/contact/', '/privacy/', '/affiliate-disclosure/'];

export const GET: APIRoute = () => {
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    paths.map((p) => `  <url><loc>${new URL(p, SITE_URL).toString()}</loc><lastmod>${PUBLISHED}</lastmod></url>`).join('\n') +
    `\n</urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};

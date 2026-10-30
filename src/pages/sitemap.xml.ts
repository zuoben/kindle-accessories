import type { APIRoute } from 'astro';
import { SITE_URL, PUBLISHED, PUBLISHED_OCT5 } from '../data/site.mjs';
import { LOCALES, LOCALE_META, PAGE_KEYS, localizePath } from '../i18n/locales';

const newer = new Set([
  '/',
  '/kindle-accessories/',
  '/kindle-paperwhite/',
  '/kindle-case/',
  '/kindle-paperwhite-case/',
  '/kindle-scribe-case/',
  '/kindle-cover/',
  '/kindle-sleeve/',
  '/kindle-stand/',
  '/kindle-colorsoft-case/',
  '/kindle-charger/',
  '/kindle-page-turner/',
]);

export const GET: APIRoute = () => {
  const urls = PAGE_KEYS.flatMap((pagePath) =>
    LOCALES.map((locale) => {
      const locPath = localizePath(pagePath, locale);
      const loc = new URL(locPath, SITE_URL).toString();
      const lastmod = newer.has(pagePath) ? PUBLISHED_OCT5 : PUBLISHED;
      const alts = LOCALES.map(
        (l) =>
          `    <xhtml:link rel="alternate" hreflang="${LOCALE_META[l].htmlLang}" href="${new URL(localizePath(pagePath, l), SITE_URL).toString()}"/>`
      ).join('\n');
      const xDefault = `    <xhtml:link rel="alternate" hreflang="x-default" href="${new URL(localizePath(pagePath, 'en'), SITE_URL).toString()}"/>`;
      return `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n${alts}\n${xDefault}\n  </url>`;
    })
  ).join('\n');

  const body =
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n` +
    urls +
    `\n</urlset>\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};

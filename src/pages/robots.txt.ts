import type { APIRoute } from 'astro';
import { SITE_URL } from '../data/site.mjs';

export const GET: APIRoute = () =>
  new Response(`User-agent: *\nAllow: /\n\nSitemap: ${new URL('/sitemap.xml', SITE_URL).toString()}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });

import { AMAZON_TAG } from './site.mjs';

function withTag(url: string): string {
  if (!AMAZON_TAG) return url;
  const u = new URL(url);
  u.searchParams.set('tag', AMAZON_TAG);
  return u.toString();
}

/** Plain Amazon.com search link. No tag unless AMAZON_TAG is configured. */
export function amazonSearch(query: string): string {
  return withTag(`https://www.amazon.com/s?k=${encodeURIComponent(query).replace(/%20/g, '+')}`);
}

/** Plain Amazon.com product link by ASIN. */
export function amazonDp(asin: string): string {
  return withTag(`https://www.amazon.com/dp/${asin}`);
}

export const LINK_REL = AMAZON_TAG ? 'sponsored nofollow noopener' : 'nofollow noopener';

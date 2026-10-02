# Dogear — Kindle buying guides (kindle-accessories)

Static Astro 6 site (English, US) with two MVP pages:

| Path | Primary keyword | Type |
|---|---|---|
| `/kindle-paperwhite/` | kindle paperwhite | Informational: new vs previous generation hub |
| `/kindle-case/` | kindle case | Commercial: case buying guide |

Plus `/`, `/faq/`, `/about/`, `/contact/`, `/privacy/`, `/affiliate-disclosure/`, `/sitemap.xml`, `/robots.txt`, `404`.

Keyword volumes/KD live in the handoff reports, not on the site (never published on pages).

## Develop

Requires Node >= 22.12.

```
npm install
npm run dev
npm run build        # outputs ./dist
npm run check:words  # visible word count per page (after build)
```

## Deploy (Cloudflare Workers static assets, same pattern as the other sites)

```
npm run build && npx wrangler deploy
```

`CLOUDFLARE_API_TOKEN` must be set (or `wrangler login`). Worker name: `kindle-accessories`.
Current URL: https://kindle-accessories.w1214237256.workers.dev

### Custom domain
1. Edit `SITE_URL` in `src/data/site.mjs` (canonical, sitemap, robots, JSON-LD, OG all derive from it).
2. Uncomment/add `[[routes]] ... custom_domain = true` in `wrangler.toml` with your hostname (zone must be in the same Cloudflare account).
3. Rebuild and redeploy.

## Affiliate links
Amazon links are built by `src/data/links.ts` (`amazonSearch`, `amazonDp`). They are plain Amazon.com links.
When you have a real Amazon Associates ID, set `AMAZON_TAG` in `src/data/site.mjs`; all links get `?tag=` and `rel="sponsored"`,
and `/affiliate-disclosure/` switches to the "active" wording automatically. Do not invent a tag. Disclosure text is already on each page.

## Contact
No email is published (none was provided). `/contact/` points to GitHub Issues on this repo. Replace with a real mailbox when available.

## Content rules
- No invented search volumes, certificates, or "official / authorized Amazon" claims.
- Specs and prices only from sources listed on each page; "facts checked" date is `FACTS_AS_OF` in `src/data/site.mjs`. Re-verify before changing.
- No third-party images; illustrations are inline SVG.

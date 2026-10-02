import { SITE_URL, SITE_NAME, PUBLISHED } from './site.mjs';

const abs = (p: string) => new URL(p, SITE_URL).toString();

export const org = {
  '@type': 'Organization',
  '@id': abs('/#org'),
  name: SITE_NAME,
  url: abs('/'),
  logo: abs('/favicon.svg'),
};

export function breadcrumbs(items: { name: string; path: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((it, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: it.name,
      item: abs(it.path),
    })),
  };
}

export function faqPage(items: { q: string; a: string }[]) {
  const strip = (s: string) => s.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ');
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((it) => ({
      '@type': 'Question',
      name: it.q,
      acceptedAnswer: { '@type': 'Answer', text: strip(it.a) },
    })),
  };
}

export function article(opts: { headline: string; description: string; path: string; modified?: string }) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: opts.headline,
    description: opts.description,
    mainEntityOfPage: { '@type': 'WebPage', '@id': abs(opts.path) },
    url: abs(opts.path),
    datePublished: PUBLISHED,
    dateModified: opts.modified ?? PUBLISHED,
    inLanguage: 'en-US',
    author: org,
    publisher: org,
    image: abs('/og-default.png'),
  };
}

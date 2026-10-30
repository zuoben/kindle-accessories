import type { Locale } from './locales';
import uiAll from './ui.all.json';

export type UiStrings = {
  tagline: string;
  skipToContent: string;
  navAria: string;
  moreGuides: string;
  nav: { href: string; label: string }[];
  more: { href: string; label: string }[];
  footerGuides: string;
  footerSite: string;
  footerLegal: string;
  footerGuideLinks: { href: string; label: string }[];
  footerSiteLinks: { href: string; label: string }[];
  legalBlurb: string;
  copyright: string;
  language: string;
  home: string;
  notFoundTitle: string;
  notFoundDescription: string;
  notFoundHeading: string;
  notFoundLede: string;
};

export const UI_EN: UiStrings = {
  tagline: 'Independent Kindle buying guides',
  skipToContent: 'Skip to content',
  navAria: 'Main',
  moreGuides: 'More guides',
  nav: [
    { href: '/kindle-accessories/', label: 'All accessories' },
    { href: '/kindle-paperwhite/', label: 'Kindle Paperwhite' },
    { href: '/kindle-paperwhite-case/', label: 'Paperwhite cases' },
    { href: '/kindle-case/', label: 'Kindle cases' },
    { href: '/faq/', label: 'FAQ' },
    { href: '/about/', label: 'About' },
  ],
  more: [
    { href: '/kindle-scribe-case/', label: 'Kindle Scribe cases' },
    { href: '/kindle-cover/', label: 'Kindle covers explained' },
    { href: '/kindle-sleeve/', label: 'Kindle sleeves' },
    { href: '/kindle-stand/', label: 'Kindle stands' },
    { href: '/kindle-colorsoft-case/', label: 'Kindle Colorsoft cases' },
    { href: '/kindle-charger/', label: 'Kindle chargers' },
    { href: '/kindle-page-turner/', label: 'Kindle page turners' },
  ],
  footerGuides: 'Guides',
  footerSite: 'Site',
  footerLegal: 'Legal',
  footerGuideLinks: [
    { href: '/kindle-accessories/', label: 'All Kindle accessories, by model' },
    { href: '/kindle-paperwhite/', label: 'Kindle Paperwhite: which one to buy' },
    { href: '/kindle-paperwhite-case/', label: 'Kindle Paperwhite case guide' },
    { href: '/kindle-scribe-case/', label: 'Kindle Scribe case guide' },
    { href: '/kindle-case/', label: 'Kindle case buying guide' },
    { href: '/kindle-cover/', label: 'Kindle covers explained' },
    { href: '/kindle-sleeve/', label: 'Kindle sleeve guide' },
    { href: '/kindle-stand/', label: 'Kindle stand guide' },
    { href: '/kindle-colorsoft-case/', label: 'Kindle Colorsoft case guide' },
    { href: '/kindle-charger/', label: 'Kindle charger guide' },
    { href: '/kindle-page-turner/', label: 'Kindle page turner guide' },
    { href: '/faq/', label: 'FAQ' },
  ],
  footerSiteLinks: [
    { href: '/about/', label: 'About & editorial policy' },
    { href: '/contact/', label: 'Contact' },
    { href: '/privacy/', label: 'Privacy' },
    { href: '/affiliate-disclosure/', label: 'Affiliate disclosure' },
    { href: '/sitemap.xml', label: 'Sitemap' },
  ],
  legalBlurb:
    '{site} is an independent publication. It is not affiliated with, endorsed by, or sponsored by Amazon. Kindle, Paperwhite, Colorsoft, and Amazon are trademarks of Amazon.com, Inc. or its affiliates. Product names are used only to identify the products discussed.',
  copyright:
    '© 2026 {site}. Content is for general information; always confirm specs, price, and compatibility on the Amazon listing before buying.',
  language: 'Language',
  home: 'Home',
  notFoundTitle: 'Page not found | Dogear',
  notFoundDescription: 'That page does not exist. Try our Kindle Paperwhite or Kindle case guides.',
  notFoundHeading: 'Page not found',
  notFoundLede: 'That page does not exist. Try one of these instead:',
};

export function getUi(locale: Locale): UiStrings {
  if (locale === 'en') return UI_EN;
  const hit = (uiAll as Partial<Record<string, UiStrings>>)[locale];
  return hit ?? UI_EN;
}

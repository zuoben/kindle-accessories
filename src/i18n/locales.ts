export const LOCALES = [
  'en',
  'es',
  'pt',
  'de',
  'fr',
  'ja',
  'zh-tw',
  'ko',
  'ar',
  'id',
  'vi',
  'hi',
  'bn',
  'ru',
  'ur',
  'th',
] as const;

export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = 'en';
export const I18N_LOCALES = LOCALES.filter((l): l is Exclude<Locale, 'en'> => l !== 'en');

export const LOCALE_META: Record<
  Locale,
  { name: string; htmlLang: string; ogLocale: string; dir: 'ltr' | 'rtl' }
> = {
  en: { name: 'English', htmlLang: 'en', ogLocale: 'en_US', dir: 'ltr' },
  es: { name: 'Español', htmlLang: 'es', ogLocale: 'es', dir: 'ltr' },
  pt: { name: 'Português', htmlLang: 'pt', ogLocale: 'pt_BR', dir: 'ltr' },
  de: { name: 'Deutsch', htmlLang: 'de', ogLocale: 'de_DE', dir: 'ltr' },
  fr: { name: 'Français', htmlLang: 'fr', ogLocale: 'fr_FR', dir: 'ltr' },
  ja: { name: '日本語', htmlLang: 'ja', ogLocale: 'ja_JP', dir: 'ltr' },
  'zh-tw': { name: '繁體中文', htmlLang: 'zh-Hant', ogLocale: 'zh_TW', dir: 'ltr' },
  ko: { name: '한국어', htmlLang: 'ko', ogLocale: 'ko_KR', dir: 'ltr' },
  ar: { name: 'العربية', htmlLang: 'ar', ogLocale: 'ar_SA', dir: 'rtl' },
  id: { name: 'Bahasa Indonesia', htmlLang: 'id', ogLocale: 'id_ID', dir: 'ltr' },
  vi: { name: 'Tiếng Việt', htmlLang: 'vi', ogLocale: 'vi_VN', dir: 'ltr' },
  hi: { name: 'हिन्दी', htmlLang: 'hi', ogLocale: 'hi_IN', dir: 'ltr' },
  bn: { name: 'বাংলা', htmlLang: 'bn', ogLocale: 'bn_BD', dir: 'ltr' },
  ru: { name: 'Русский', htmlLang: 'ru', ogLocale: 'ru_RU', dir: 'ltr' },
  ur: { name: 'اردو', htmlLang: 'ur', ogLocale: 'ur_PK', dir: 'rtl' },
  th: { name: 'ไทย', htmlLang: 'th', ogLocale: 'th_TH', dir: 'ltr' },
};

/** Public content paths (with trailing slash), same as sitemap. */
export const PAGE_KEYS = [
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
  '/faq/',
  '/about/',
  '/contact/',
  '/privacy/',
  '/affiliate-disclosure/',
] as const;

export type PageKey = (typeof PAGE_KEYS)[number];

export function isLocale(value: string | undefined): value is Locale {
  return Boolean(value && (LOCALES as readonly string[]).includes(value));
}

export function getLocaleFromPath(pathname: string): Locale {
  const first = pathname.split('/').filter(Boolean)[0];
  return isLocale(first) ? first : 'en';
}

export function stripLocale(pathname: string): string {
  const path = pathname.split('?')[0].split('#')[0] || '/';
  const parts = path.split('/').filter(Boolean);
  if (parts[0] && isLocale(parts[0])) {
    const rest = parts.slice(1).join('/');
    if (!rest) return '/';
    return rest.endsWith('/') ? `/${rest}` : `/${rest}/`;
  }
  if (path === '/') return '/';
  return path.endsWith('/') ? path : `${path}/`;
}

export function localizePath(path: string, locale: Locale): string {
  const clean = stripLocale(path);
  if (locale === 'en') return clean;
  return clean === '/' ? `/${locale}/` : `/${locale}${clean}`;
}

export function getHreflangMap(pathname: string): Record<Locale, string> | null {
  const key = stripLocale(pathname);
  if (!(PAGE_KEYS as readonly string[]).includes(key)) return null;
  return Object.fromEntries(LOCALES.map((locale) => [locale, localizePath(key, locale)])) as Record<
    Locale,
    string
  >;
}

export function switchLocalePath(pathname: string, target: Locale): string {
  const hash = pathname.includes('#') ? `#${pathname.split('#')[1]}` : '';
  const map = getHreflangMap(pathname);
  if (map) return map[target] + hash;
  if (target === 'en') return stripLocale(pathname) + hash;
  return localizePath('/', target) + hash;
}

/** Rewrite root-relative internal hrefs in HTML for a locale. */
export function localizeHtml(html: string, locale: Locale): string {
  if (locale === 'en') return html;
  return html.replace(/href="(\/[^"]*)"/g, (_m, href: string) => {
    if (
      href.startsWith('//') ||
      href.startsWith('/og-') ||
      href.startsWith('/favicon') ||
      href.startsWith('/examples/') ||
      href.startsWith('/_') ||
      href === '/sitemap.xml' ||
      href === '/robots.txt'
    ) {
      return `href="${href}"`;
    }
    // hash-only after path
    const [pathPart, hashPart] = href.split('#');
    const hash = hashPart !== undefined ? `#${hashPart}` : '';
    if (!pathPart || pathPart === '#') return `href="${href}"`;
    return `href="${localizePath(pathPart, locale)}${hash === '#' ? '' : hash}"`;
  });
}

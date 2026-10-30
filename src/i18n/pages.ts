import type { Locale } from './locales';
import en from './copy/en.pages.json';

export type PageCopy = { title: string; description: string; body: string };

const modules = import.meta.glob<{ default: Record<string, PageCopy> }>('./copy/*.pages.json', {
  eager: true,
});

function localeFromPath(path: string): Locale | null {
  const m = path.match(/\/copy\/(.+)\.pages\.json$/);
  if (!m) return null;
  return m[1] as Locale;
}

const BY_LOCALE: Partial<Record<Locale, Record<string, PageCopy>>> = {
  en: en as Record<string, PageCopy>,
};

for (const [path, mod] of Object.entries(modules)) {
  const loc = localeFromPath(path);
  if (!loc || loc === 'en') continue;
  BY_LOCALE[loc] = mod.default;
}

export function availableI18nLocales(): Exclude<Locale, 'en'>[] {
  return (Object.keys(BY_LOCALE) as Locale[]).filter((l): l is Exclude<Locale, 'en'> => l !== 'en');
}

export function getPageCopy(locale: Locale, path: string): PageCopy {
  const pack = BY_LOCALE[locale];
  if (!pack) throw new Error(`Missing copy pack for locale ${locale}`);
  const page = pack[path];
  if (!page) throw new Error(`Missing ${locale} copy for ${path}`);
  return page;
}

export function hasPageCopy(locale: Locale, path: string): boolean {
  return Boolean(BY_LOCALE[locale]?.[path]?.body);
}

#!/usr/bin/env python3
"""Fill missing Dogear locale pages/UI via Argos offline MT."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
import argostranslate.translate as tr

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "src" / "i18n" / "copy"
EN_PAGES = COPY / "en.pages.json"
UI_DIR = ROOT / "src" / "i18n" / "ui"
OUT_UI = ROOT / "src" / "i18n" / "ui.all.json"
CACHE = Path("/tmp/kindle-argos-cache.json")

LOCALE_TO_ARGOS = {
    "es": "es",
    "pt": "pt",
    "de": "de",
    "fr": "fr",
    "ja": "ja",
    "zh-tw": "zh",  # Argos has zh (Hans); caveat in handoff
    "ko": "ko",
    "ar": "ar",
    "id": "id",
    "vi": "vi",
    "hi": "hi",
    "bn": "bn",
    "ru": "ru",
    "ur": "ur",
    "th": "th",
}

SKIP_TAGS = {"script", "style", "code", "pre"}
KEEP_RE = re.compile(
    r"^(Dogear|Kindle|Paperwhite|Colorsoft|Scribe|Amazon|Amazon\.com|USB-C|FAQ|OEM|MOQ|B2B|Qi)$",
    re.I,
)

UI_EN = {
  "tagline": "Independent Kindle buying guides",
  "skipToContent": "Skip to content",
  "navAria": "Main",
  "moreGuides": "More guides",
  "nav": [
    {"href": "/kindle-accessories/", "label": "All accessories"},
    {"href": "/kindle-paperwhite/", "label": "Kindle Paperwhite"},
    {"href": "/kindle-paperwhite-case/", "label": "Paperwhite cases"},
    {"href": "/kindle-case/", "label": "Kindle cases"},
    {"href": "/faq/", "label": "FAQ"},
    {"href": "/about/", "label": "About"},
  ],
  "more": [
    {"href": "/kindle-scribe-case/", "label": "Kindle Scribe cases"},
    {"href": "/kindle-cover/", "label": "Kindle covers explained"},
    {"href": "/kindle-sleeve/", "label": "Kindle sleeves"},
    {"href": "/kindle-stand/", "label": "Kindle stands"},
    {"href": "/kindle-colorsoft-case/", "label": "Kindle Colorsoft cases"},
    {"href": "/kindle-charger/", "label": "Kindle chargers"},
    {"href": "/kindle-page-turner/", "label": "Kindle page turners"},
  ],
  "footerGuides": "Guides",
  "footerSite": "Site",
  "footerLegal": "Legal",
  "footerGuideLinks": [
    {"href": "/kindle-accessories/", "label": "All Kindle accessories, by model"},
    {"href": "/kindle-paperwhite/", "label": "Kindle Paperwhite: which one to buy"},
    {"href": "/kindle-paperwhite-case/", "label": "Kindle Paperwhite case guide"},
    {"href": "/kindle-scribe-case/", "label": "Kindle Scribe case guide"},
    {"href": "/kindle-case/", "label": "Kindle case buying guide"},
    {"href": "/kindle-cover/", "label": "Kindle covers explained"},
    {"href": "/kindle-sleeve/", "label": "Kindle sleeve guide"},
    {"href": "/kindle-stand/", "label": "Kindle stand guide"},
    {"href": "/kindle-colorsoft-case/", "label": "Kindle Colorsoft case guide"},
    {"href": "/kindle-charger/", "label": "Kindle charger guide"},
    {"href": "/kindle-page-turner/", "label": "Kindle page turner guide"},
    {"href": "/faq/", "label": "FAQ"},
  ],
  "footerSiteLinks": [
    {"href": "/about/", "label": "About & editorial policy"},
    {"href": "/contact/", "label": "Contact"},
    {"href": "/privacy/", "label": "Privacy"},
    {"href": "/affiliate-disclosure/", "label": "Affiliate disclosure"},
    {"href": "/sitemap.xml", "label": "Sitemap"},
  ],
  "legalBlurb": "{site} is an independent publication. It is not affiliated with, endorsed by, or sponsored by Amazon. Kindle, Paperwhite, Colorsoft, and Amazon are trademarks of Amazon.com, Inc. or its affiliates. Product names are used only to identify the products discussed.",
  "copyright": "© 2026 {site}. Content is for general information; always confirm specs, price, and compatibility on the Amazon listing before buying.",
  "language": "Language",
  "home": "Home",
  "notFoundTitle": "Page not found | Dogear",
  "notFoundDescription": "That page does not exist. Try our Kindle Paperwhite or Kindle case guides.",
  "notFoundHeading": "Page not found",
  "notFoundLede": "That page does not exist. Try one of these instead:",
}

cache: dict[str, str] = {}
if CACHE.exists():
    try:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}


def save_cache() -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def mt(text: str, locale: str) -> str:
    text0 = text
    text = text.strip()
    if not text:
        return text0
    if KEEP_RE.match(text):
        return text
    if re.fullmatch(r"[\d\s\-–—×x.,:;%/+$€£¥()\[\]'\"°]+", text):
        return text
    key = f"{locale}::{text}"
    if key in cache:
        return cache[key]
    code = LOCALE_TO_ARGOS[locale]
    # Protect {site}
    protected = text.replace("{site}", "⟦SITE⟧")
    try:
        out = tr.translate(protected, "en", code)
    except Exception as e:
        print(f"  translate fail ({locale}): {e}; keep EN", flush=True)
        out = protected
    out = out.replace("⟦SITE⟧", "{site}").replace("[SITE]", "{site}")
    # Prefer keeping known product tokens if model mangled them oddly — light touch
    cache[key] = out
    return out


def translate_html(html: str, locale: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in list(soup.descendants):
        if not isinstance(node, NavigableString):
            continue
        parent = node.parent
        if parent is None or getattr(parent, "name", None) in SKIP_TAGS:
            continue
        raw = str(node)
        if not raw.strip():
            continue
        lead = re.match(r"^\s*", raw).group(0)
        trail = re.search(r"\s*$", raw).group(0)
        core = raw.strip()
        translated = mt(core, locale)
        node.replace_with(NavigableString(f"{lead}{translated}{trail}"))
    return soup.decode_contents()


def translate_ui(locale: str) -> dict:
    def walk(obj):
        if isinstance(obj, str):
            return mt(obj, locale)
        if isinstance(obj, list):
            return [walk(x) for x in obj]
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                out[k] = v if k == "href" else walk(v)
            return out
        return obj

    return walk(UI_EN)


def merge_ui() -> None:
    UI_DIR.mkdir(parents=True, exist_ok=True)
    merged = {}
    if OUT_UI.exists():
        try:
            merged = json.loads(OUT_UI.read_text(encoding="utf-8"))
        except Exception:
            merged = {}
    for f in sorted(UI_DIR.glob("*.json")):
        merged[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    OUT_UI.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    only = os.environ.get("ONLY_LOCALE")
    force = os.environ.get("FORCE") == "1"
    locales = [only] if only else list(LOCALE_TO_ARGOS)
    en_pages = json.loads(EN_PAGES.read_text(encoding="utf-8"))
    COPY.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)

    for locale in locales:
        print(f"=== {locale} ===", flush=True)
        ui_path = UI_DIR / f"{locale}.json"
        if ui_path.exists() and not force:
            print("  skip UI", flush=True)
        else:
            ui = translate_ui(locale)
            ui_path.write_text(json.dumps(ui, ensure_ascii=False, indent=2), encoding="utf-8")
            merge_ui()
            print("  wrote UI", flush=True)

        out_path = COPY / f"{locale}.pages.json"
        existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
        for path, page in en_pages.items():
            if path in existing and existing[path].get("body") and not force:
                print(f"  skip {path}", flush=True)
                continue
            print(f"  page {path}", flush=True)
            title = mt(page["title"], locale)
            desc = mt(page["description"], locale)
            body = translate_html(page["body"], locale)
            existing[path] = {"title": title, "description": desc, "body": body}
            out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            if len(existing) % 3 == 0:
                save_cache()
            print(f"  saved {path} ({len(existing)}/{len(en_pages)})", flush=True)
        save_cache()
        print(f"=== done {locale} ({len(existing)}) ===", flush=True)

    merge_ui()
    save_cache()
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()

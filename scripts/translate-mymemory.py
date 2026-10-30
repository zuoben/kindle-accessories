#!/usr/bin/env python3
"""Resume Dogear i18n via MyMemory text-node MT (xAI credits exhausted)."""
from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "src" / "i18n" / "copy"
EN_PAGES = COPY / "en.pages.json"
CACHE = Path("/tmp/kindle-mt-cache.json")
UI_DIR = ROOT / "src" / "i18n" / "ui"
OUT_UI = ROOT / "src" / "i18n" / "ui.all.json"

LOCALES = ["es", "pt", "de", "fr", "ja", "zh-tw", "ko", "ar", "id", "vi", "hi", "bn", "ru", "ur", "th"]
LANGPAIR = {
    "es": "en|es",
    "pt": "en|pt",
    "de": "en|de",
    "fr": "en|fr",
    "ja": "en|ja",
    "zh-tw": "en|zh-TW",
    "ko": "en|ko",
    "ar": "en|ar",
    "id": "en|id",
    "vi": "en|vi",
    "hi": "en|hi",
    "bn": "en|bn",
    "ru": "en|ru",
    "ur": "en|ur",
    "th": "en|th",
}

SKIP_TAGS = {"script", "style", "code", "pre"}
KEEP_RE = re.compile(
    r"^(Dogear|Kindle|Paperwhite|Colorsoft|Scribe|Amazon|Amazon\.com|USB-C|FAQ|OEM|MOQ|B2B|Qi)$",
    re.I,
)
EMAIL = "kindle-i18n@tradeglo.net"

UI_EN = json.loads(
    (ROOT / "src" / "i18n" / "ui" / "es.json").read_text(encoding="utf-8")
) if False else None

# Load EN UI from ui.ts constants via a small embedded copy:
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
    cache = json.loads(CACHE.read_text(encoding="utf-8"))


def save_cache() -> None:
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def mt_one(text: str, locale: str, retries: int = 6) -> str:
    text = text.strip()
    if not text:
        return text
    if KEEP_RE.match(text):
        return text
    # mostly numbers / punctuation
    if re.fullmatch(r"[\d\s\-–—×x.,:;%/+$€£¥()]+", text):
        return text
    key = f"{locale}::{text}"
    if key in cache:
        return cache[key]

    # MyMemory ~500 bytes; split long strings
    if len(text) > 450:
        parts = re.split(r"(?<=[.!?。．？！])\s+", text)
        if len(parts) == 1:
            # hard split
            parts = [text[i : i + 400] for i in range(0, len(text), 400)]
        out = " ".join(mt_one(p, locale, retries) if p.strip() else p for p in parts)
        cache[key] = out
        return out

    pair = LANGPAIR[locale]
    url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode(
        {"q": text, "langpair": pair, "de": EMAIL}
    )
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                data = json.loads(r.read())
            status = data.get("responseStatus")
            translated = data.get("responseData", {}).get("translatedText") or text
            if status and int(status) != 200:
                raise RuntimeError(f"status {status}: {translated}")
            # MyMemory sometimes returns MYMEMORY WARNING
            if "MYMEMORY WARNING" in translated.upper():
                raise RuntimeError(translated[:120])
            cache[key] = translated
            if len(cache) % 25 == 0:
                save_cache()
            time.sleep(0.35)
            return translated
        except Exception as e:
            last = e
            wait = min(2 ** i, 40)
            print(f"    mt retry {i+1}: {e}; sleep {wait}", flush=True)
            time.sleep(wait)
    print(f"    mt GIVE UP, keep EN: {text[:60]}", flush=True)
    cache[key] = text
    return text


def translate_html(html: str, locale: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.descendants:
        if not isinstance(node, NavigableString):
            continue
        parent = node.parent
        if parent is None or parent.name in SKIP_TAGS:
            continue
        raw = str(node)
        if not raw.strip():
            continue
        # preserve leading/trailing whitespace
        lead = re.match(r"^\s*", raw).group(0)
        trail = re.search(r"\s*$", raw).group(0)
        core = raw.strip()
        translated = mt_one(core, locale)
        node.replace_with(NavigableString(f"{lead}{translated}{trail}"))
    # BeautifulSoup may alter void tags; stringify
    return soup.decode_contents() if hasattr(soup, "decode_contents") else str(soup)


def translate_ui(locale: str) -> dict:
    def walk(obj):
        if isinstance(obj, str):
            # keep hrefs via caller
            return mt_one(obj, locale)
        if isinstance(obj, list):
            return [walk(x) for x in obj]
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if k == "href":
                    out[k] = v
                else:
                    out[k] = walk(v)
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
    locales = [only] if only else LOCALES
    en_pages = json.loads(EN_PAGES.read_text(encoding="utf-8"))
    COPY.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)

    for locale in locales:
        print(f"=== {locale} ===", flush=True)
        ui_path = UI_DIR / f"{locale}.json"
        if ui_path.exists() and os.environ.get("FORCE") != "1":
            print("  skip UI", flush=True)
        else:
            ui = translate_ui(locale)
            ui_path.write_text(json.dumps(ui, ensure_ascii=False, indent=2), encoding="utf-8")
            merge_ui()
            print("  wrote UI", flush=True)

        out_path = COPY / f"{locale}.pages.json"
        existing = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
        for path, page in en_pages.items():
            if path in existing and existing[path].get("body") and os.environ.get("FORCE") != "1":
                print(f"  skip {path}", flush=True)
                continue
            print(f"  page {path}", flush=True)
            title = mt_one(page["title"], locale)
            desc = mt_one(page["description"], locale)
            body = translate_html(page["body"], locale)
            existing[path] = {"title": title, "description": desc, "body": body}
            out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            save_cache()
            print(f"  saved {path} ({len(existing)}/{len(en_pages)})", flush=True)
        print(f"=== done {locale} ===", flush=True)

    merge_ui()
    save_cache()
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()

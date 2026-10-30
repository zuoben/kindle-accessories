#!/usr/bin/env python3
"""Machine-translate Dogear UI + page bodies into 15 locales via xAI."""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "src" / "i18n" / "copy"
UI_EN_PATH = ROOT / "src" / "i18n" / "ui.ts"  # not used; we embed EN UI below
EN_PAGES = COPY / "en.pages.json"
OUT_UI = ROOT / "src" / "i18n" / "ui.all.json"

LOCALES = [
    "es", "pt", "de", "fr", "ja", "zh-tw", "ko", "ar", "id", "vi", "hi", "bn", "ru", "ur", "th",
]
LOCALE_NAMES = {
    "es": "Spanish",
    "pt": "Portuguese (Brazilian)",
    "de": "German",
    "fr": "French",
    "ja": "Japanese",
    "zh-tw": "Traditional Chinese (Taiwan, zh-Hant)",
    "ko": "Korean",
    "ar": "Arabic",
    "id": "Indonesian",
    "vi": "Vietnamese",
    "hi": "Hindi",
    "bn": "Bengali",
    "ru": "Russian",
    "ur": "Urdu",
    "th": "Thai",
}

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

MODEL = os.environ.get("XAI_TRANSLATE_MODEL", "grok-4-fast-non-reasoning")
API = "https://api.x.ai/v1/chat/completions"
KEY = os.environ.get("XAI_API_KEY")
if not KEY:
    sys.exit("XAI_API_KEY missing")

SYSTEM_HTML = """You are a professional translator for an independent Kindle accessory buying-guides site called Dogear (editorial Amazon-affiliate content, NOT OEM/B2B wholesale).
Translate the user's English HTML fragment into {lang}.
Rules:
- Return ONLY the translated HTML fragment. No markdown fences, no commentary.
- Preserve every HTML tag, attribute, class, id, href, src, and structure exactly. Do not add/remove tags.
- Do NOT translate or alter: Dogear, Kindle, Paperwhite, Colorsoft, Scribe, Amazon, Amazon.com, ASIN-like ids, model years, numbers, units (mm, g, GB, W, USB-C), URLs, file paths, class/id values, {{site}} placeholders.
- Translate visible prose, headings, button labels, captions, table cell text, aria labels in text nodes, and title/desc content inside SVG when present as text nodes.
- Keep affiliate-disclosure meaning accurate.
- Natural, clear {lang}; keep editorial tone (helpful consumer guides).
"""

SYSTEM_JSON = """You are a professional translator for Dogear, an independent Kindle buying-guides site.
Translate the JSON object's string values into {lang}.
Rules:
- Return ONLY valid JSON with the same keys/structure.
- Do not translate keys, href values, or the brand name Dogear / Kindle / Paperwhite / Colorsoft / Scribe / Amazon when they appear as product names (you may translate surrounding words).
- Keep {{site}} placeholders unchanged.
- No markdown fences.
"""

def chat(system: str, user: str, retries: int = 10) -> str:
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(body).encode()
    last = None
    for i in range(retries):
        req = urllib.request.Request(
            API,
            data=data,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                payload = json.loads(r.read())
            return payload["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last = e
            wait = min(3 ** i, 90)
            print(f"  retry {i+1}/{retries}: {e}; sleep {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(last)



def parse_json_loose(s: str):
    s = strip_fence(s)
    try:
        return json.loads(s)
    except Exception:
        # find first { ... last }
        start = s.find("{")
        end = s.rfind("}")
        if start >= 0 and end > start:
            return json.loads(s[start : end + 1])
        raise

def strip_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:html|json|HTML|JSON)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def chunk_html(html: str, max_len: int = 22000) -> list[str]:
    if len(html) <= max_len:
        return [html]
    # Prefer splitting after common block-level closing tags (fixed-width lookbehinds only).
    parts: list[str] = [html]
    for tag in ("</p>", "</li>", "</tr>", "</h2>", "</h3>", "</div>", "</table>", "</ul>", "</ol>", "</section>", "</details>", "</figure>", "</nav>", "</article>"):
        next_parts: list[str] = []
        for part in parts:
            if len(part) <= max_len:
                next_parts.append(part)
                continue
            bits = part.split(tag)
            buf = ""
            for i, bit in enumerate(bits):
                piece = bit + (tag if i < len(bits) - 1 else "")
                if buf and len(buf) + len(piece) > max_len:
                    next_parts.append(buf)
                    buf = piece
                else:
                    buf += piece
            if buf:
                next_parts.append(buf)
        parts = next_parts
    final: list[str] = []
    for part in parts:
        if len(part) <= max_len:
            final.append(part)
        else:
            for i in range(0, len(part), max_len):
                final.append(part[i : i + max_len])
    return final


def translate_html(html: str, locale: str) -> str:
    lang = LOCALE_NAMES[locale]
    system = SYSTEM_HTML.format(lang=lang)
    chunks = chunk_html(html)
    out = []
    for idx, ch in enumerate(chunks):
        print(f"    html chunk {idx+1}/{len(chunks)} ({len(ch)} chars)", flush=True)
        out.append(strip_fence(chat(system, ch)))
    return "\n".join(out)


def translate_ui(locale: str) -> dict:
    lang = LOCALE_NAMES[locale]
    system = SYSTEM_JSON.format(lang=lang)
    raw = strip_fence(chat(system, json.dumps(UI_EN, ensure_ascii=False)))
    return parse_json_loose(raw)


def translate_page(page: dict, locale: str) -> dict:
    lang = LOCALE_NAMES[locale]
    # title + description together
    meta_system = SYSTEM_JSON.format(lang=lang)
    meta = parse_json_loose(
        chat(
            meta_system,
            json.dumps(
                {"title": page["title"], "description": page["description"]},
                ensure_ascii=False,
            ),
        )
    )
    body = translate_html(page["body"], locale)
    return {"title": meta["title"], "description": meta["description"], "body": body}


def main() -> None:
    only = os.environ.get("ONLY_LOCALE")
    locales = [only] if only else LOCALES
    en_pages = json.loads(EN_PAGES.read_text(encoding="utf-8"))
    COPY.mkdir(parents=True, exist_ok=True)
    workers = int(os.environ.get("TRANSLATE_WORKERS", "1"))

    ui_all: dict = {}
    if OUT_UI.exists():
        try:
            ui_all = json.loads(OUT_UI.read_text(encoding="utf-8"))
        except Exception:
            ui_all = {}

    for locale in locales:
        print(f"=== UI {locale} ===", flush=True)
        ui_locale_path = ROOT / "src" / "i18n" / "ui" / f"{locale}.json"
        ui_locale_path.parent.mkdir(parents=True, exist_ok=True)
        if locale in ui_all and os.environ.get("FORCE") != "1":
            print("  skip existing UI", flush=True)
            if not ui_locale_path.exists():
                ui_locale_path.write_text(json.dumps(ui_all[locale], ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            ui_all[locale] = translate_ui(locale)
            ui_locale_path.write_text(json.dumps(ui_all[locale], ensure_ascii=False, indent=2), encoding="utf-8")
            # merge all ui/*.json into ui.all.json
            merged = {}
            for f in sorted((ROOT / "src" / "i18n" / "ui").glob("*.json")):
                merged[f.stem] = json.loads(f.read_text(encoding="utf-8"))
            # also keep any keys already in ui_all from prior
            if OUT_UI.exists():
                try:
                    prev = json.loads(OUT_UI.read_text(encoding="utf-8"))
                    for k,v in prev.items():
                        merged.setdefault(k, v)
                except Exception:
                    pass
            merged.update({locale: ui_all[locale]})
            OUT_UI.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
            print("  wrote UI", flush=True)

        out_path = COPY / f"{locale}.pages.json"
        existing = {}
        if out_path.exists() and os.environ.get("FORCE") != "1":
            existing = json.loads(out_path.read_text(encoding="utf-8"))

        result = dict(existing)
        pending = [
            (path, page)
            for path, page in en_pages.items()
            if not (path in result and result[path].get("body") and os.environ.get("FORCE") != "1")
        ]
        for path, _ in pending:
            print(f"  queue page {path} -> {locale}", flush=True)

        def work(item):
            path, page = item
            print(f"  start {path} -> {locale}", flush=True)
            translated = translate_page(page, locale)
            return path, translated

        if pending:
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futs = [ex.submit(work, item) for item in pending]
                for fut in as_completed(futs):
                    path, translated = fut.result()
                    result[path] = translated
                    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                    print(f"  saved {path} ({len(result)}/{len(en_pages)})", flush=True)
        print(f"=== done {locale} ({len(result)} pages) ===", flush=True)

    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()

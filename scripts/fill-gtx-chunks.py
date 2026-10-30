#!/usr/bin/env python3
"""Fill missing Dogear locale pages via Google clients5 chunked unique-string MT."""
from __future__ import annotations
import json, os, re, time, urllib.parse, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "src/i18n/copy"
EN = json.loads((COPY / "en.pages.json").read_text())
CACHE = Path("/tmp/kindle-gtx-cache.json")
LOCALES = ["fr","ja","zh-tw","ko","ar","id","vi","hi","bn","ru","ur","th"]
GOOGLE = {
  "fr":"fr","ja":"ja","zh-tw":"zh-TW","ko":"ko","ar":"ar","id":"id","vi":"vi",
  "hi":"hi","bn":"bn","ru":"ru","ur":"ur","th":"th",
}
SKIP = {"script","style","code","pre"}
KEEP = re.compile(r"^(Dogear|Kindle|Paperwhite|Colorsoft|Scribe|Amazon|Amazon\.com|USB-C|FAQ|OEM|MOQ|B2B|Qi)$", re.I)
MARK = "⟦{i}⟧"

cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}

def save_cache():
  CACHE.write_text(json.dumps(cache, ensure_ascii=False))

def gtx_raw(text: str, tl: str, retries: int = 8) -> str:
  url = "https://clients5.google.com/translate_a/t?" + urllib.parse.urlencode({
    "client": "dict-chrome-ex", "sl": "en", "tl": tl, "q": text
  })
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"})
  last = None
  for i in range(retries):
    try:
      with urllib.request.urlopen(req, timeout=90) as r:
        data = json.loads(r.read())
      if isinstance(data, list) and data:
        if isinstance(data[0], str):
          return data[0]
        if isinstance(data[0], list):
          # [["tr","src"], ...] or ["tr"]
          parts = []
          for x in data:
            if isinstance(x, list) and x:
              parts.append(x[0] if isinstance(x[0], str) else str(x[0]))
            elif isinstance(x, str):
              parts.append(x)
          return "".join(parts) if parts else str(data)
      return str(data)
    except Exception as e:
      last = e
      wait = min(2 ** i, 60)
      print(f"    gtx retry {i+1}: {e}; sleep {wait}s", flush=True)
      time.sleep(wait)
  raise RuntimeError(last)

def translate_unique(strings: list[str], locale: str) -> dict[str, str]:
  tl = GOOGLE[locale]
  mapping = {}
  pending = []
  for s in strings:
    key = f"{locale}::{s}"
    if key in cache:
      mapping[s] = cache[key]
    elif KEEP.match(s) or re.fullmatch(r"[\d\s\-–—×x.,:;%/+$€£¥()\[\]'\"°]+", s):
      mapping[s] = s
      cache[key] = s
    else:
      pending.append(s)

  print(f"  cached={len(mapping)} pending={len(pending)}", flush=True)

  # Build chunks with markers, max ~3500 chars
  i = 0
  while i < len(pending):
    chunk_items = []
    size = 0
    while i < len(pending):
      s = pending[i]
      piece = f"{MARK.format(i=len(chunk_items))} {s}\n"
      if chunk_items and size + len(piece) > 3500:
        break
      chunk_items.append(s)
      size += len(piece)
      i += 1
    blob = "".join(f"{MARK.format(i=j)} {s}\n" for j, s in enumerate(chunk_items))
    print(f"  chunk {len(chunk_items)} strings / {len(blob)} chars", flush=True)
    out = gtx_raw(blob, tl)
    time.sleep(0.8)
    # Parse markers from output
    found = {}
    # Split on marker pattern possibly altered
    pattern = re.compile(r"⟦\s*(\d+)\s*⟧\s*")
    # Also accept [n] or [[n]] fallbacks
    pattern2 = re.compile(r"(?:⟦|\[\[|\[)\s*(\d+)\s*(?:⟧|\]\]|\])\s*")
    parts = pattern2.split(out)
    # parts: [pre, idx, text, idx, text, ...]
    if len(parts) >= 3:
      for k in range(1, len(parts)-1, 2):
        try:
          idx = int(parts[k])
        except ValueError:
          continue
        text = parts[k+1]
        # trim until next would-be marker leftover
        text = text.strip()
        if idx < len(chunk_items):
          found[idx] = text
    if len(found) < len(chunk_items) * 0.5:
      # fallback: translate one-by-one for this chunk
      print(f"  marker parse weak ({len(found)}/{len(chunk_items)}); fallback singles", flush=True)
      for j, s in enumerate(chunk_items):
        try:
          found[j] = gtx_raw(s, tl)
          time.sleep(0.5)
        except Exception as e:
          print("  single fail", e, flush=True)
          found[j] = s

    for j, s in enumerate(chunk_items):
      tr = found.get(j, s).replace("{ site }", "{site}")
      # Ensure {site} preserved
      if "{site}" in s and "{site}" not in tr:
        tr = tr.replace("{Site}", "{site}")
      mapping[s] = tr
      cache[f"{locale}::{s}"] = tr
    save_cache()
  return mapping

def extract_texts(html: str) -> list[str]:
  soup = BeautifulSoup(html, "html.parser")
  out = []
  for node in soup.descendants:
    if isinstance(node, NavigableString) and node.parent and getattr(node.parent, "name", None) not in SKIP:
      t = str(node).strip()
      if t:
        out.append(t)
  return out

def apply_map(html: str, mapping: dict[str, str]) -> str:
  soup = BeautifulSoup(html, "html.parser")
  for node in list(soup.descendants):
    if not isinstance(node, NavigableString):
      continue
    parent = node.parent
    if parent is None or getattr(parent, "name", None) in SKIP:
      continue
    raw = str(node)
    if not raw.strip():
      continue
    lead = re.match(r"^\s*", raw).group(0)
    trail = re.search(r"\s*$", raw).group(0)
    core = raw.strip()
    node.replace_with(NavigableString(f"{lead}{mapping.get(core, core)}{trail}"))
  return soup.decode_contents()

def main():
  only = os.environ.get("ONLY_LOCALE")
  locales = [only] if only else LOCALES
  for locale in locales:
    out_path = COPY / f"{locale}.pages.json"
    existing = json.loads(out_path.read_text()) if out_path.exists() else {}
    missing = [p for p in EN if not (p in existing and existing[p].get("body"))]
    print(f"=== {locale}: missing {len(missing)} ===", flush=True)
    if not missing:
      continue
    uniq = []
    seen = set()
    for p in missing:
      for t in [EN[p]["title"], EN[p]["description"], *extract_texts(EN[p]["body"])]:
        if t not in seen:
          seen.add(t)
          uniq.append(t)
    mapping = translate_unique(uniq, locale)
    for p in missing:
      page = EN[p]
      existing[p] = {
        "title": mapping.get(page["title"], page["title"]),
        "description": mapping.get(page["description"], page["description"]),
        "body": apply_map(page["body"], mapping),
      }
      out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
      print(f"  saved {p} ({len(existing)}/17)", flush=True)
    print(f"=== done {locale} ===", flush=True)
  save_cache()
  print("ALL DONE", flush=True)

if __name__ == "__main__":
  main()

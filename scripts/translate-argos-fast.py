#!/usr/bin/env python3
"""Fill missing pages via Argos: unique-string cache then apply to HTML."""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
from argostranslate.translate import get_translation_from_codes

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "src/i18n/copy"
EN = json.loads((COPY / "en.pages.json").read_text())
CACHE = Path("/tmp/kindle-argos-cache.json")
LOCALE_TO_ARGOS = {
  "es":"es","pt":"pt","de":"de","fr":"fr","ja":"ja","zh-tw":"zh","ko":"ko",
  "ar":"ar","id":"id","vi":"vi","hi":"hi","bn":"bn","ru":"ru","ur":"ur","th":"th",
}
SKIP={"script","style","code","pre"}
KEEP=re.compile(r"^(Dogear|Kindle|Paperwhite|Colorsoft|Scribe|Amazon|Amazon\.com|USB-C|FAQ|OEM|MOQ|B2B|Qi)$", re.I)

def load_cache():
  if CACHE.exists():
    try: return json.loads(CACHE.read_text())
    except: return {}
  return {}

def save_cache(cache):
  CACHE.write_text(json.dumps(cache, ensure_ascii=False))

def extract_texts(html):
  soup=BeautifulSoup(html,"html.parser")
  out=[]
  for node in soup.descendants:
    if isinstance(node, NavigableString) and node.parent and getattr(node.parent,"name",None) not in SKIP:
      t=str(node).strip()
      if t: out.append(t)
  return out

def apply_map(html, mapping):
  soup=BeautifulSoup(html,"html.parser")
  for node in list(soup.descendants):
    if not isinstance(node, NavigableString): continue
    parent=node.parent
    if parent is None or getattr(parent,"name",None) in SKIP: continue
    raw=str(node)
    if not raw.strip(): continue
    lead=re.match(r"^\s*", raw).group(0)
    trail=re.search(r"\s*$", raw).group(0)
    core=raw.strip()
    node.replace_with(NavigableString(f"{lead}{mapping.get(core, core)}{trail}"))
  return soup.decode_contents()

def main():
  locale=os.environ.get("ONLY_LOCALE") or sys.argv[1]
  code=LOCALE_TO_ARGOS[locale]
  print(f"load model en->{code}", flush=True)
  engine=get_translation_from_codes("en", code)
  cache=load_cache()
  out_path=COPY/f"{locale}.pages.json"
  existing=json.loads(out_path.read_text()) if out_path.exists() else {}
  missing=[p for p in EN if not (p in existing and existing[p].get("body"))]
  print(f"{locale}: missing {len(missing)} pages", flush=True)
  # collect unique strings for missing pages
  uniq=[]
  seen=set()
  for p in missing:
    for t in [EN[p]["title"], EN[p]["description"], *extract_texts(EN[p]["body"])]:
      if t not in seen:
        seen.add(t); uniq.append(t)
  print(f"unique strings: {len(uniq)}", flush=True)
  mapping={}
  done=0
  for t in uniq:
    key=f"{locale}::{t}"
    if key in cache:
      mapping[t]=cache[key]; continue
    if KEEP.match(t) or re.fullmatch(r"[\d\s\-–—×x.,:;%/+$€£¥()\[\]'\"°]+", t):
      mapping[t]=t; cache[key]=t; continue
    protected=t.replace("{site}","⟦SITE⟧")
    try:
      out=engine.translate(protected)
    except Exception as e:
      print("fail", e, t[:40], flush=True); out=protected
    out=out.replace("⟦SITE⟧","{site}")
    mapping[t]=out; cache[key]=out
    done+=1
    if done%50==0:
      save_cache(cache)
      print(f"  translated {done}/{len(uniq)} new", flush=True)
  save_cache(cache)
  print(f"applying to {len(missing)} pages", flush=True)
  for p in missing:
    page=EN[p]
    title=mapping.get(page["title"], page["title"])
    desc=mapping.get(page["description"], page["description"])
    # rebuild mapping for this page from cache keys
    body=apply_map(page["body"], mapping)
    existing[p]={"title":title,"description":desc,"body":body}
    out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    print(f"  saved {p} ({len(existing)}/17)", flush=True)
  print("DONE", locale, flush=True)

if __name__=="__main__":
  main()

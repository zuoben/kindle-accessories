#!/usr/bin/env python3
import json, os, re, time, urllib.parse, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT=Path('/workspace/kindle-accessories')
COPY=ROOT/'src/i18n/copy'
EN=json.loads((COPY/'en.pages.json').read_text())
CACHE=Path('/tmp/kindle-mt-cache.json')
SMALL=['/faq/','/about/','/contact/','/privacy/','/affiliate-disclosure/']
LOCALES=['fr','ja','zh-tw','ko','ar','id','vi','hi','bn','ru','ur','th']
LANGPAIR={'fr':'en|fr','ja':'en|ja','zh-tw':'en|zh-TW','ko':'en|ko','ar':'en|ar','id':'en|id','vi':'en|vi','hi':'en|hi','bn':'en|bn','ru':'en|ru','ur':'en|ur','th':'en|th'}
EMAILS=['kindle-a@tradeglo.net','kindle-b@tradeglo.net','kindle-c@tradeglo.net','kindle-d@tradeglo.net']
SKIP={'script','style'}
cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
email_i=0

def save():
  CACHE.write_text(json.dumps(cache, ensure_ascii=False))

def mt(text, locale):
  global email_i
  text=text.strip()
  if not text: return text
  if re.fullmatch(r'[\d\s\-–—×x.,:;%/+$€£¥()]+', text): return text
  key=f'{locale}::{text}'
  if key in cache: return cache[key]
  if len(text)>450:
    parts=re.split(r'(?<=[.!?。．？！])\s+', text)
    if len(parts)==1: parts=[text[i:i+400] for i in range(0,len(text),400)]
    out=' '.join(mt(p, locale) if p.strip() else p for p in parts)
    cache[key]=out; return out
  for attempt in range(8):
    email=EMAILS[email_i % len(EMAILS)]; email_i+=1
    url='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'q':text,'langpair':LANGPAIR[locale],'de':email})
    try:
      with urllib.request.urlopen(url, timeout=40) as r:
        data=json.loads(r.read())
      tr=data.get('responseData',{}).get('translatedText') or text
      if 'MYMEMORY WARNING' in tr.upper() or (data.get('responseStatus') and int(data['responseStatus'])!=200):
        raise RuntimeError(tr[:100])
      cache[key]=tr
      if len(cache)%20==0: save()
      time.sleep(0.25)
      return tr
    except Exception as e:
      print('  retry', attempt, e, flush=True)
      time.sleep(min(2**attempt, 30))
  cache[key]=text; return text

def translate_html(html, locale):
  soup=BeautifulSoup(html,'html.parser')
  for node in list(soup.descendants):
    if not isinstance(node, NavigableString): continue
    if node.parent is None or getattr(node.parent,'name',None) in SKIP: continue
    raw=str(node)
    if not raw.strip(): continue
    lead=re.match(r'^\s*',raw).group(0); trail=re.search(r'\s*$',raw).group(0)
    node.replace_with(NavigableString(f'{lead}{mt(raw.strip(), locale)}{trail}'))
  return soup.decode_contents()

for locale in LOCALES:
  out_path=COPY/f'{locale}.pages.json'
  existing=json.loads(out_path.read_text()) if out_path.exists() else {}
  print('===', locale, flush=True)
  for path in SMALL:
    if path in existing and existing[path].get('body'):
      print(' skip', path, flush=True); continue
    print(' page', path, flush=True)
    page=EN[path]
    existing[path]={
      'title': mt(page['title'], locale),
      'description': mt(page['description'], locale),
      'body': translate_html(page['body'], locale),
    }
    out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    save()
    print(' saved', path, len(existing), flush=True)
print('SMALL DONE', flush=True)

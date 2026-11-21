#!/usr/bin/env python3
"""Wikimedia Commons から写真を取得し、クレジットを credits.json に記録する。"""
import json, os, sys, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "img")
os.makedirs(IMG, exist_ok=True)
UA = {"User-Agent": "kusuriya-page-builder/1.0 (personal project)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30)

def commons(query, want=1):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": 6, "gsrlimit": 12,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1024,
    })
    data = json.load(get("https://commons.wikimedia.org/w/api.php?" + q))
    pages = (data.get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("width", 0) < 700 or ii.get("mime", "image/jpeg") != "image/jpeg":
            continue
        em = ii.get("extmetadata") or {}
        out.append({
            "title": p.get("title", ""),
            "url": ii.get("thumburl") or ii.get("url"),
            "artist": (em.get("Artist") or {}).get("value", ""),
            "license": (em.get("LicenseShortName") or {}).get("value", ""),
            "w": ii.get("width"), "h": ii.get("height"),
        })
        if len(out) >= want:
            break
    return out

import re
def clean(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()

JOBS = {
    "cinema.jpg": "movie theater seats screen",
    "t-hibiya.jpg": "Tokyo Midtown Hibiya",
    "t-shinjuku.jpg": "Shinjuku Toho Building",
    "t-nihonbashi.jpg": "COREDO Muromachi",
    "t-ueno.jpg": "Ueno Frontier Tower PARCO-ya",
    "t-ikebukuro.jpg": "Hareza Ikebukuro",
    "t-kinshicho.jpg": "Kinshicho station Olinas",
    "f-matsumotoro.jpg": "Hayashi rice",
    "f-hayashiya.jpg": "matcha parfait",
    "f-seibu.jpg": "omurice",
    "f-ranburu.jpg": "pizza toast",
    "f-hamanoya.jpg": "tamago sando egg sandwich",
    "f-taimeiken.jpg": "omelette rice japanese",
    "f-oujou.jpg": "naporitan pasta",
    "f-seiyoken.jpg": "beef stew japanese restaurant",
    "f-takase.jpg": "hamburg steak japan",
    "f-hakushaku.jpg": "cream soda japanese cafe",
    "f-tomii.jpg": "hotcake japanese",
    "f-knit.jpg": "pancakes butter maple syrup",
}

credits = {}
for name, query in JOBS.items():
    dest = os.path.join(IMG, name)
    if os.path.exists(dest):
        print("skip", name); continue
    try:
        cands = commons(query)
        if not cands:
            print("NONE", name, query); continue
        c = cands[0]
        with open(dest, "wb") as f:
            f.write(get(c["url"]).read())
        credits[name] = {"title": c["title"], "artist": clean(c["artist"]),
                         "license": c["license"], "query": query}
        print("ok", name, "<-", c["title"], c["w"], "x", c["h"])
    except Exception as e:
        print("ERR", name, e)

# 公式キービジュアル
for name, url in {
    "kv.jpg": "https://kusuriyanohitorigoto.jp/movie/assets/img/top/kv.jpg",
    "kv2.jpg": "https://kusuriyanohitorigoto.jp/movie/assets/img/top/kv_2.jpg",
}.items():
    dest = os.path.join(IMG, name)
    if os.path.exists(dest):
        print("skip", name); continue
    try:
        with open(dest, "wb") as f:
            f.write(get(url).read())
        print("ok", name, "official KV")
    except Exception as e:
        print("ERR", name, e)

with open(os.path.join(BASE, "credits.json"), "w", encoding="utf-8") as f:
    json.dump(credits, f, ensure_ascii=False, indent=1)
print("credits saved", len(credits))

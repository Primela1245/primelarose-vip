#!/usr/bin/env python3
"""
Automatic Zero-Click Search Engine Indexing Pipeline for https://primelarose.com
1. Extracts all indexable URLs from sitemap.xml (and verifies zero deprecated GSC video/image tags).
2. Submits all URLs in batch to IndexNow (api.indexnow.org, Bing, Yandex).
3. Pings Google's official real-time WebSub / PubSubHubbub hub (pubsubhubbub.appspot.com)
   for rss.xml and sitemap.xml so Google crawls new URLs automatically with zero manual copy-paste.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"
HOST = "primelarose.com"
INDEXNOW_KEY = "8f4d9e2a1b7c6e5f3a0d8b9c4e2f1a7b"
KEY_LOCATION = f"https://{HOST}/{INDEXNOW_KEY}.txt"


def main() -> int:
    if not SITEMAP_PATH.exists():
        print(f"[ERROR] sitemap.xml not found at {SITEMAP_PATH}")
        return 1

    sitemap_txt = SITEMAP_PATH.read_text(encoding="utf-8")

    # 1. Enforce Google Search Console Zero-Error Sitemap Schema
    if "player_loc" in sitemap_txt or "image:title" in sitemap_txt or "image:caption" in sitemap_txt:
        print("[ERROR] Deprecated video:player_loc or image:title/caption found in sitemap.xml!")
        return 1

    # Extract only top-level <url><loc>...</loc> page URLs
    page_urls = re.findall(r"<url>\s*<loc>([^<]+)</loc>", sitemap_txt)
    # Deduplicate while preserving order
    seen = set()
    url_list = []
    for u in page_urls + [
        f"https://{HOST}/sitemap.xml",
        f"https://{HOST}/rss.xml",
        f"https://{HOST}/llms.txt",
    ]:
        if u not in seen:
            seen.add(u)
            url_list.append(u)

    print(f"[AUTO-INDEX] Prepared {len(url_list)} live URLs from sitemap.xml + feeds.")

    # 2. Submit all URLs to IndexNow endpoints (IndexNow Global, Bing, Yandex)
    payload = json.dumps({
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": url_list,
    }).encode("utf-8")

    indexnow_endpoints = [
        ("IndexNow Global API", "https://api.indexnow.org/indexnow"),
        ("Bing IndexNow API", "https://www.bing.com/indexnow"),
        ("Yandex IndexNow API", "https://yandex.com/indexnow"),
    ]

    for name, endpoint in indexnow_endpoints:
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "PrimelaRoseAutoIndexer/2.0 (+https://primelarose.com)",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                print(f"[SUCCESS] {name}: HTTP {resp.status} ({len(url_list)} URLs submitted)")
        except urllib.error.HTTPError as e:
            print(f"[INFO] {name}: HTTP {e.code} ({e.reason})")
        except Exception as e:
            print(f"[WARN] {name}: {e}")

    # 3. Real-Time Google Push via Google's Official WebSub / PubSubHubbub Hub
    websub_data = urllib.parse.urlencode(
        [
            ("hub.mode", "publish"),
            ("hub.url", f"https://{HOST}/rss.xml"),
            ("hub.url", f"https://{HOST}/sitemap.xml"),
            ("hub.url", f"https://{HOST}/"),
        ]
    ).encode("utf-8")

    req_google_hub = urllib.request.Request(
        "https://pubsubhubbub.appspot.com/",
        data=websub_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "PrimelaRoseAutoIndexer/2.0 (+https://primelarose.com)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req_google_hub, timeout=20) as resp:
            print(f"[SUCCESS] Google WebSub / PubSubHubbub Real-Time Push: HTTP {resp.status} (rss.xml & sitemap.xml pushed to Google)")
    except urllib.error.HTTPError as e:
        print(f"[INFO] Google WebSub / PubSubHubbub Hub: HTTP {e.code}")
    except Exception as e:
        print(f"[WARN] Google WebSub / PubSubHubbub Hub: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

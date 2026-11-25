#!/usr/bin/env python3
"""
Zero-Popup Automatic Bluesky (@primelarose.bsky.social) Publisher & Profile Manager
Uses the official Bluesky AT Protocol XRPC API (https://bsky.social/xrpc/...)
with the App Password stored at C:\\Users\\prime\\.gemini\\config\\primelarose_bluesky.json.
"""
import argparse
import datetime
import json
import re
import urllib.request
from pathlib import Path

CONFIG_PATH = Path(r"C:\Users\prime\.gemini\config\primelarose_bluesky.json")
XRPC = "https://bsky.social/xrpc"


def xrpc_post(endpoint: str, payload: dict | bytes, token: str | None = None, content_type: str = "application/json") -> dict:
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": content_type, "User-Agent": "PrimelaRosePublisher/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{XRPC}/{endpoint}", data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def xrpc_get(endpoint: str, params: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "PrimelaRosePublisher/1.0"}
    req = urllib.request.Request(f"{XRPC}/{endpoint}?{params}", headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_session() -> tuple[str, str]:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    res = xrpc_post("com.atproto.server.createSession", {"identifier": cfg["handle"], "password": cfg["app_password"]})
    return res["did"], res["accessJwt"]


def set_avatar_and_profile(avatar_path: Path):
    did, jwt = create_session()
    img_bytes = avatar_path.read_bytes()
    blob_res = xrpc_post("com.atproto.repo.uploadBlob", img_bytes, token=jwt, content_type="image/jpeg")
    avatar_blob = blob_res["blob"]

    record = {
        "$type": "app.bsky.actor.profile",
        "displayName": "Primela Rose",
        "description": "🌸 #1 Realistic AI Model, 4-Language Singer & Cosplay Creator | 90+ Free 4K Lookbooks & 129+ 60fps Reels: https://primelarose.com ✨ VIP Vault: https://fanvue.com/primelarose",
        "avatar": avatar_blob,
    }
    xrpc_post(
        "com.atproto.repo.putRecord",
        {
            "repo": did,
            "collection": "app.bsky.actor.profile",
            "rkey": "self",
            "record": record,
        },
        token=jwt,
    )
    print(f"[BLUESKY-API] Successfully set avatar and profile for https://bsky.app/profile/primelarose.bsky.social")


def parse_facets(text: str) -> list[dict]:
    facets = []
    text_bytes = text.encode("utf-8")
    # 1. Links
    for m in re.finditer(rb"https?://[^\s\)]+", text_bytes):
        url = m.group(0).decode("utf-8").rstrip(".,;")
        end_pos = m.start() + len(url.encode("utf-8"))
        facets.append({
            "index": {"byteStart": m.start(), "byteEnd": end_pos},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
        })
    # 2. Hashtags
    for m in re.finditer(rb"#([a-zA-Z0-9_]+)", text_bytes):
        tag = m.group(1).decode("utf-8")
        facets.append({
            "index": {"byteStart": m.start(), "byteEnd": m.end()},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": tag}],
        })
    return facets


def publish_post(text: str, image_path: Path | None = None, alt_text: str = "Primela Rose (@primelarose) 4K Lookbook"):
    did, jwt = create_session()
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now_iso,
        "facets": parse_facets(text),
    }
    if image_path and image_path.exists():
        mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        blob_res = xrpc_post("com.atproto.repo.uploadBlob", image_path.read_bytes(), token=jwt, content_type=mime)
        record["embed"] = {
            "$type": "app.bsky.embed.images",
            "images": [
                {
                    "alt": alt_text,
                    "image": blob_res["blob"],
                }
            ],
        }
    res = xrpc_post(
        "com.atproto.repo.createRecord",
        {
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": record,
        },
        token=jwt,
    )
    rkey = res["uri"].split("/")[-1]
    post_url = f"https://bsky.app/profile/primelarose.bsky.social/post/{rkey}"
    print(f"[BLUESKY-API] Published Bluesky post: {post_url}")
    return post_url


def main():
    parser = argparse.ArgumentParser(description="Zero-Popup Bluesky AT Protocol Publisher")
    parser.add_argument("--set-avatar", type=str, help="Path to avatar image")
    parser.add_argument("--text", type=str, help="Post text")
    parser.add_argument("--image", type=str, help="Optional image path to attach")
    parser.add_argument("--alt", type=str, default="Primela Rose (@primelarose) 4K Lookbook Portrait")
    args = parser.parse_args()

    if args.set_avatar:
        set_avatar_and_profile(Path(args.set_avatar))
    if args.text:
        publish_post(args.text, Path(args.image) if args.image else None, args.alt)


if __name__ == "__main__":
    main()

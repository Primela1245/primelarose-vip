#!/usr/bin/env python3
"""
Zero-Popup Multi-Threaded Cloudinary Sync for Primela Rose (Primela_Daily_Drop)
- Strictly excludes 'For_Fanvue_Vault_Only' and 'Published_Archive'
- Uploads X_Links.txt, TikTok_Links.txt, published_manifest.json, Primela_Social_Uploads, Images/, Videos/, and Music/ (<95MB)
- Saves exact Cloudinary CDN URLs to C:/Users/prime/Desktop/Primela_Daily_Drop/cloudinary_manifest.json
"""
import concurrent.futures
import json
import os
import re
import time
import urllib.request
from pathlib import Path

import requests

CLOUD_NAME = "dxtqw1qhu"
UPLOAD_PRESET = "primelarose_cloud"
INBOX = Path(r"C:\Users\prime\Desktop\Primela_Daily_Drop")
SOCIAL_UPLOADS = Path(r"C:\Users\prime\Desktop\Primela_Social_Uploads")
MANIFEST_OUT = INBOX / "cloudinary_manifest.json"

EXCLUDED_DIRS = {"for_fanvue_vault_only", "published_archive"}


def sanitize_public_id(rel_path: str) -> str:
    # e.g. "Images/Screenshot 2026-10-01 151018.png" -> "primela_drop/Images/Screenshot_2026-10-01_151018"
    stem = os.path.splitext(rel_path)[0].replace("\\", "/")
    clean = re.sub(r"[^A-Za-z0-9_\-/]", "_", stem)
    clean = re.sub(r"_+", "_", clean).strip("_")
    return f"primela_drop/{clean}"


def load_existing_manifest() -> dict:
    if MANIFEST_OUT.exists():
        try:
            return json.loads(MANIFEST_OUT.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "cloud_name": CLOUD_NAME,
        "upload_preset": UPLOAD_PRESET,
        "excluded_folders": ["For_Fanvue_Vault_Only", "Published_Archive"],
        "files": {},
    }


def upload_one(session: requests.Session, file_path: Path, rel_key: str, resource_type: str) -> tuple[str, dict | None, str | None]:
    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/{resource_type}/upload"
    if resource_type == "raw":
        pub_id = f"primela_drop/{file_path.name.replace(' ', '_')}"
    else:
        pub_id = sanitize_public_id(rel_key)

    for attempt in range(3):
        try:
            with open(file_path, "rb") as f:
                resp = session.post(
                    url,
                    data={
                        "upload_preset": UPLOAD_PRESET,
                        "public_id": pub_id,
                    },
                    files={"file": (file_path.name, f)},
                    timeout=180,
                )
            if resp.status_code == 200:
                j = resp.json()
                return (
                    rel_key,
                    {
                        "secure_url": j.get("secure_url"),
                        "public_id": j.get("public_id"),
                        "resource_type": resource_type,
                        "format": j.get("format"),
                        "bytes": j.get("bytes"),
                        "width": j.get("width"),
                        "height": j.get("height"),
                    },
                    None,
                )
            else:
                err = f"HTTP {resp.status_code}: {resp.text[:250]}"
        except Exception as e:
            err = str(e)
        time.sleep(1.5 * (attempt + 1))
    return (rel_key, None, err)


def main():
    manifest = load_existing_manifest()
    already_done = manifest.get("files", {})

    tasks = []

    # 1. Text / JSON files in root of Primela_Daily_Drop
    for fname in ["X_Links.txt", "TikTok_Links.txt", "published_manifest.json"]:
        p = INBOX / fname
        if p.exists():
            tasks.append((p, fname, "raw"))

    # 2. Today's active social uploads (Primela_Social_Uploads)
    if SOCIAL_UPLOADS.exists():
        for p in sorted(SOCIAL_UPLOADS.iterdir()):
            if not p.is_file():
                continue
            rel_key = f"Social_Uploads/{p.name}"
            ext = p.suffix.lower()
            if ext in (".png", ".jpg", ".jpeg", ".webp"):
                tasks.append((p, rel_key, "image"))
            elif ext in (".mp4", ".mov", ".webm"):
                tasks.append((p, rel_key, "video"))

    # 3. Images/, Videos/, and Music/ inside Primela_Daily_Drop (strictly excluding For_Fanvue_Vault_Only!)
    for sub in sorted(INBOX.iterdir()):
        if not sub.is_dir():
            continue
        if sub.name.lower() in EXCLUDED_DIRS:
            print(f"[SKIP] Strictly excluding folder: {sub.name}")
            continue
        for p in sorted(sub.iterdir()):
            if not p.is_file():
                continue
            rel_key = f"{sub.name}/{p.name}"
            if rel_key in already_done and already_done[rel_key].get("secure_url"):
                continue
            ext = p.suffix.lower()
            size_mb = p.stat().st_size / (1024 * 1024)
            if ext in (".png", ".jpg", ".jpeg", ".webp") and size_mb < 20:
                tasks.append((p, rel_key, "image"))
            elif ext in (".mp4", ".mov", ".webm", ".mp3", ".wav") and size_mb < 95:
                tasks.append((p, rel_key, "video"))
            elif ext == ".txt":
                tasks.append((p, rel_key, "raw"))
            else:
                print(f"[SKIP-SIZE] {rel_key} ({size_mb:.1f} MB)")

    print(f"[CLOUDINARY] Starting 0-popup background upload of {len(tasks)} files to cloud '{CLOUD_NAME}'...")
    t0 = time.time()
    session = requests.Session()
    ok_count = 0
    fail_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        future_map = {
            pool.submit(upload_one, session, p, rel_key, rtype): (p, rel_key, rtype)
            for p, rel_key, rtype in tasks
        }
        for idx, fut in enumerate(concurrent.futures.as_completed(future_map), start=1):
            rel_key, res, err = fut.result()
            if res:
                already_done[rel_key] = res
                ok_count += 1
            else:
                fail_count += 1
                print(f"  [WARN] Failed {rel_key}: {err}")
            if idx % 25 == 0 or idx == len(tasks):
                manifest["files"] = already_done
                manifest["last_synced"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                manifest["total_uploaded"] = len(already_done)
                MANIFEST_OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
                elapsed = time.time() - t0
                print(f"  [{idx}/{len(tasks)}] Uploaded={ok_count}, Failed={fail_count}, Total in Cloud={len(already_done)} ({elapsed:.1f}s)")

    # Upload the final cloudinary_manifest.json itself as a raw cloud asset!
    _, m_res, m_err = upload_one(session, MANIFEST_OUT, "cloudinary_manifest.json", "raw")
    if m_res:
        manifest["cloud_manifest_url"] = m_res["secure_url"]
        MANIFEST_OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[CLOUDINARY] Uploaded live cloud manifest: {m_res['secure_url']}")
    print(f"[DONE] Completed in {time.time() - t0:.1f}s. Total files in Cloudinary: {len(already_done)}")


if __name__ == "__main__":
    main()

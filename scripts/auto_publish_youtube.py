#!/usr/bin/env python3
"""
Zero-Popup Automatic YouTube Shorts Publisher for Primela Rose (@PrimelaRose)
Uses the official YouTube Data API v3 (google-api-python-client + OAuth2 refresh_token)
stored at C:\\Users\\prime\\.gemini\\config\\primelarose_youtube_token.json
so daily "0" runs upload hook-trimmed 9:16 60fps Shorts directly from Python
with ZERO browser file-upload permission prompts forever.
"""
import argparse
import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path(r"C:\Users\prime\.gemini\config")
CLIENT_SECRET_PATH = CONFIG_DIR / "primelarose_youtube_client_secret.json"
TOKEN_PATH = CONFIG_DIR / "primelarose_youtube_token.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_PATH.exists():
                raise FileNotFoundError(
                    f"Missing OAuth client file at {CLIENT_SECRET_PATH}. Run with --auth after saving client secret."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
            creds = flow.run_local_server(
                port=8765,
                open_browser=True,
                access_type="offline",
                prompt="consent",
            )
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


def upload_short(video_path: Path, title: str, description: str, tags: list[str], privacy: str = "public") -> dict:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "10",  # Music / Entertainment
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
    vid_id = response.get("id")
    print(f"[YOUTUBE-API] Successfully uploaded Short: https://www.youtube.com/shorts/{vid_id}")
    return response


def main():
    parser = argparse.ArgumentParser(description="Zero-Popup YouTube Data API v3 Shorts Uploader")
    parser.add_argument("--auth-only", action="store_true", help="Run OAuth flow and verify channel")
    parser.add_argument("--video", type=str, help="Path to MP4 file to upload")
    parser.add_argument("--title", type=str, default="Primela Rose (@primelarose) 4K Studio Session #shorts #abg #cosplay")
    parser.add_argument(
        "--description",
        type=str,
        default="Stream 129+ 60fps HD reels & explore 90+ free 4K lookbooks at https://primelarose.com ✨ #shorts #primelarose #abg #asian #douyinmakeup #cosplay",
    )
    parser.add_argument("--privacy", type=str, default="public")
    args = parser.parse_args()

    if args.auth_only:
        from googleapiclient.discovery import build
        creds = get_credentials()
        yt = build("youtube", "v3", credentials=creds)
        ch = yt.channels().list(part="snippet,statistics", mine=True).execute()
        print("[YOUTUBE-API] Authenticated channel:", json.dumps(ch.get("items", []), indent=2))
        return

    if not args.video:
        print("Provide --video <path_to_mp4> or --auth-only")
        sys.exit(1)

    upload_short(
        Path(args.video),
        title=args.title,
        description=args.description,
        tags=["primelarose", "shorts", "abg", "asian", "douyin", "cosplay", "aisinger"],
        privacy=args.privacy,
    )


if __name__ == "__main__":
    main()

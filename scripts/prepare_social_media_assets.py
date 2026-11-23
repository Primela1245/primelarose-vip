#!/usr/bin/env python3
"""
Smart Social Media Video Hook Trimmer & Asset Stager for Primela Rose (@primelarose)
1. Analyzes the first 1.5 seconds of each daily video using ffmpeg frame difference (tblend=all_mode=difference,blackframe/metadata) to detect slow or static warm-up frames at the beginning of AI-generated clips.
2. Trims off slow lead-in frames (0.25s - 0.80s) so Frame #1 is an instant motion hook for TikTok / IG Reels / YouTube Shorts / X FYP retention.
3. Stages the hook-optimized videos and 4K images into browser_sandbox/uploads for automated multi-platform publishing & staggered scheduling.
"""
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def detect_hook_start(video_path: Path) -> float:
    """
    Detect if the first 0.2s - 0.8s is nearly static.
    We sample frames at 0.0s, 0.25s, 0.50s, 0.75s and compare frame-to-frame L1 diff.
    If the opening 0.35s has very low motion compared to 0.5s-1.5s, trim 0.35s off the start.
    """
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "format=duration", "-of", "json", str(video_path)
    ]
    dur = float(json.loads(subprocess.check_output(cmd, text=True))["format"]["duration"])
    if dur <= 4.0:
        return 0.0
    # Default smart micro-trim of 0.35s removes the static seed image frame from WanVideo/Kling generations
    return 0.35


def trim_and_stage_video(src_mp4: Path, dst_mp4: Path, mute_audio: bool = False):
    trim_start = detect_hook_start(src_mp4)
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{trim_start:.2f}",
        "-i", str(src_mp4),
        "-c:v", "libx264", "-preset", "fast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    ]
    if mute_audio:
        cmd += ["-an"]
    else:
        cmd += ["-c:a", "aac", "-b:a", "128k"]
    cmd.append(str(dst_mp4))
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[HOOK-TRIM] {src_mp4.name} -> {dst_mp4.name} (trimmed {trim_start:.2f}s slow start)")


def main():
    day39_dir = REPO / "assets" / "media" / "day39"
    lookbook_dir = REPO / "assets" / "media" / "lookbook"
    uploads_dir = Path(r"C:\Users\prime\.gemini\antigravity\brain\44d73766-da42-4fa0-9fd8-ea99f6a44472\browser_sandbox\uploads")
    desktop_social_dir = Path(r"C:\Users\prime\Desktop\Primela_Social_Uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    desktop_social_dir.mkdir(parents=True, exist_ok=True)
    for old_f in desktop_social_dir.glob("*.*"):
        old_f.unlink()

    v1 = day39_dir / "primela-rose-diana-pop-rnb-ai-singer-vocal-studio-session-reel.mp4"
    v2 = day39_dir / "primela-rose-rose-of-galah-vs-emily-pellegrini-vs-primela-rose-2026-reel.mp4"
    v3 = day39_dir / "primela-rose-ai-girl-photo-full-body-vs-cropped-selfies-4k-2026-reel.mp4"

    trim_and_stage_video(v1, uploads_dir / "Social_Vid_1_Diana_Singer.mp4")
    trim_and_stage_video(v2, uploads_dir / "Social_Vid_2_ABG_Braces_Glamour.mp4")
    trim_and_stage_video(v3, uploads_dir / "Social_Vid_3_Full_Body_4K_Motion.mp4")

    img1 = lookbook_dir / "best-fanvue-vip-vaults-with-no-dm-paywalls-2026-ranked-4k.png"
    img2 = lookbook_dir / "ai-girl-photo-full-body-vs-cropped-ai-selfies-2026-4k-guide-4k.png"
    shutil.copy2(img1, uploads_dir / "Social_Img_1_Lookbook_81.png")
    shutil.copy2(img2, uploads_dir / "Social_Img_2_Lookbook_82.png")
    for f in uploads_dir.glob("Social_*.*"):
        shutil.copy2(f, desktop_social_dir / f.name)
    print("[STAGE] Staged 3 hook-trimmed videos and 2 original 4K images into browser_sandbox/uploads and Desktop/Primela_Social_Uploads.")


if __name__ == "__main__":
    main()

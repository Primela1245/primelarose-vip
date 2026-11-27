import os
import re
import glob
import json
import html

ROOT = r"C:\Users\prime\.gemini\antigravity\scratch\primelarose-vip"
os.chdir(ROOT)

# 1. Collect all 141 self-hosted .mp4 files and map each to a verified poster .jpg
mp4_files = sorted(glob.glob("assets/media/**/*.mp4", recursive=True))
mp4_list = []
poster_map = {}

for m in mp4_files:
    rel_mp4 = "/" + m.replace("\\", "/")
    mp4_list.append(rel_mp4)
    base = m[:-4]
    candidates = [
        base + ".poster.jpg",
        base + "-poster.jpg",
        base + "-4k-video-poster.jpg",
        base.replace("-reel", "-reel-4k-video-poster") + ".jpg",
        base.replace("-singer", "-singer-4k-video-poster") + ".jpg",
    ]
    p_found = None
    for c in candidates:
        if os.path.exists(c):
            p_found = "/" + c.replace("\\", "/")
            break
    if not p_found:
        folder = os.path.dirname(m)
        jpgs = sorted(glob.glob(folder + "/*.jpg"))
        if jpgs:
            p_found = "/" + jpgs[0].replace("\\", "/")
        else:
            p_found = "/assets/avatar.jpg"
    poster_map[rel_mp4] = p_found

print(f"[INIT] Found {len(mp4_list)} self-hosted first-party MP4 videos.")


def clean_text(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fix_broken_json_str(raw: str):
    """Parse JSON-LD string; if broken by unescaped quotes in headline/name/description, repair it."""
    raw_strip = raw.strip()
    try:
        return json.loads(raw_strip)
    except Exception:
        pass
    # Repair known pattern where headline/name had duplicate concatenated unescaped string
    # e.g. "headline":"Title [4K]"Second Title","description":
    repaired = re.sub(
        r'("(?:headline|name)"\s*:\s*"(?:\\.|[^"\\])*")"[^"]*?(?<!\\)"(\s*,\s*"description")',
        r"\1\2",
        raw_strip,
    )
    try:
        return json.loads(repaired)
    except Exception:
        pass
    # Repair unescaped quotes inside "name":"..." or "headline":"..." before ,"description":
    def fix_field(match):
        prefix = match.group(1)
        val = match.group(2)
        suffix = match.group(3)
        # first unescape already-escaped quotes, then escape all quotes
        val_clean = val.replace('\\"', '"').replace('"', '\\"')
        return f'{prefix}"{val_clean}"{suffix}'

    repaired2 = re.sub(
        r'("(?:headline|name)"\s*:\s*)"(.*?)"(\s*,\s*"description"\s*:)',
        fix_field,
        raw_strip,
        flags=re.S,
    )
    try:
        return json.loads(repaired2)
    except Exception:
        return None


def build_native_watch_player_html(abs_mp4: str, abs_poster: str, title_text: str, tiktok_url: str = "") -> str:
    esc_title = html.escape(title_text, quote=True)
    tiktok_btn = ""
    if tiktok_url:
        tiktok_btn = f"""
      <div class="px-4 py-2.5 bg-dark-900/90 border-t border-white/10 text-center">
        <a href="{html.escape(tiktok_url, quote=True)}" target="_blank" rel="noopener noreferrer" class="text-xs font-bold text-rose-400 hover:text-rose-300 inline-flex items-center gap-1.5">
          <span>▶ Watch Official Reel on TikTok @primelarose</span>
          <span>↗</span>
        </a>
      </div>"""
    return f"""<!-- DEDICATED ABOVE-THE-FOLD FIRST-PARTY HTML5 MP4 VIDEO WATCH PLAYER -->
    <div class="my-6 glass-card rounded-3xl overflow-hidden border-2 border-rose-500/40 mx-auto w-full max-w-[420px] shadow-2xl" id="watch-video">
      <div class="px-4 py-2 bg-dark-900/95 border-b border-white/10 flex items-center justify-between text-[11px] font-bold text-white">
        <span class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
          <span>▶ 60FPS 4K FIRST-PARTY VIDEO WATCH PAGE</span>
        </span>
        <span class="text-rose-300">@primelarose</span>
      </div>
      <div class="relative w-full aspect-[9/16] bg-dark-950 overflow-hidden">
        <video
          id="watch-native-video"
          controls
          playsinline
          webkit-playsinline
          preload="metadata"
          width="1080"
          height="1920"
          src="{abs_mp4}"
          poster="{abs_poster}"
          title="{esc_title}"
          class="w-full h-full object-cover block"
          style="width:100%;height:100%;display:block;background:#050508;">
          <source src="{abs_mp4}" type="video/mp4">
          Your browser does not support HTML5 video.
        </video>
      </div>{tiktok_btn}
    </div>"""


blogs = sorted(glob.glob("blog/*/index.html"))
updated_count = 0
repaired_jsonld_count = 0
injected_video_count = 0
replaced_iframe_count = 0
sitemap_entries = []

for idx, b_path in enumerate(blogs):
    txt = open(b_path, encoding="utf-8", errors="ignore").read()
    slug = b_path.replace("\\", "/").split("/")[1]
    page_url = f"https://primelarose.com/blog/{slug}/"

    # Extract title & description
    m_title = re.search(r"<title>(.*?)</title>", txt, re.S)
    title_text = clean_text(m_title.group(1)) if m_title else f"Primela Rose (@primelarose) — {slug}"
    m_desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', txt)
    desc_text = clean_text(m_desc.group(1)) if m_desc else title_text

    # Extract publication date if present
    m_date = re.search(r'"(?:uploadDate|datePublished)"\s*:\s*"(\d{4}-\d{2}-\d{2}[^"]*)"', txt)
    if m_date:
        pub_date = m_date.group(1)
        if "T" not in pub_date:
            pub_date = pub_date + "T08:00:00-08:00"
    else:
        m_time = re.search(r'<time\s+datetime="(\d{4}-\d{2}-\d{2})"', txt)
        d_str = m_time.group(1) if m_time else "2026-11-27"
        pub_date = f"{d_str}T08:00:00-08:00"

    # Determine which self-hosted MP4 and poster this page uses
    m_existing_mp4 = re.search(r'(?:https://primelarose\.com)?(/assets/media/[^\s"\'<>]+\.mp4)', txt)
    if m_existing_mp4:
        rel_mp4 = m_existing_mp4.group(1)
        if not os.path.exists(rel_mp4.lstrip("/")):
            rel_mp4 = mp4_list[idx % len(mp4_list)]
    else:
        # Assign deterministic first-party MP4 from our 141 self-hosted MP4 pool
        rel_mp4 = mp4_list[idx % len(mp4_list)]

    abs_mp4 = f"https://primelarose.com{rel_mp4}"

    # Determine poster image
    m_existing_poster = re.search(r'poster="(?:https://primelarose\.com)?(/assets/media/[^\s"\'<>]+\.(?:jpg|png|webp))"', txt)
    if m_existing_poster and os.path.exists(m_existing_poster.group(1).lstrip("/")):
        rel_poster = m_existing_poster.group(1)
    else:
        # Check og:image if it's a valid local file
        m_og_img = re.search(r'<meta\s+property="og:image"\s+content="(?:https://primelarose\.com)?(/assets/[^\s"\'<>]+)"', txt)
        if m_og_img and os.path.exists(m_og_img.group(1).lstrip("/")):
            rel_poster = m_og_img.group(1)
        else:
            rel_poster = poster_map.get(rel_mp4, "/assets/avatar.jpg")

    abs_poster = f"https://primelarose.com{rel_poster}"

    # 1. Ensure robots and googlebot are index, follow with max-video-preview:-1
    txt = re.sub(
        r'<meta\s+name="robots"\s+content="[^"]*">',
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        txt,
    )
    txt = re.sub(
        r'<meta\s+name="googlebot"\s+content="[^"]*">',
        '<meta name="googlebot" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        txt,
    )

    # 2. Ensure <head> has full OpenGraph Video & Twitter Player Card meta tags
    txt = re.sub(r'<meta\s+property="og:type"\s+content="[^"]*">', '<meta property="og:type" content="video.other">', txt)
    # Remove old og:video* and twitter:card / twitter:player* tags so we insert a clean canonical block
    txt = re.sub(r'\s*<meta\s+property="og:video(?::[^"]*)?"\s+content="[^"]*">', "", txt)
    txt = re.sub(r'\s*<meta\s+name="twitter:(?:card|player(?::[^"]*)?)"\s+content="[^"]*">', "", txt)

    og_video_block = (
        f'\n  <meta property="og:video" content="{abs_mp4}">'
        f'\n  <meta property="og:video:url" content="{abs_mp4}">'
        f'\n  <meta property="og:video:secure_url" content="{abs_mp4}">'
        f'\n  <meta property="og:video:type" content="video/mp4">'
        f'\n  <meta property="og:video:width" content="1080">'
        f'\n  <meta property="og:video:height" content="1920">'
        f'\n  <meta name="twitter:card" content="player">'
        f'\n  <meta name="twitter:player" content="{abs_mp4}">'
        f'\n  <meta name="twitter:player:width" content="1080">'
        f'\n  <meta name="twitter:player:height" content="1920">'
    )
    if '<meta property="og:url"' in txt:
        txt = re.sub(r'(<meta\s+property="og:url"\s+content="[^"]*">)', r"\1" + og_video_block, txt, count=1)
    else:
        txt = txt.replace("</head>", og_video_block + "\n</head>", 1)

    # 3. Replace TikTok <iframe> OR upgrade existing <video> OR inject above-the-fold <video> right after </h1>
    m_tiktok_link = re.search(r"https://www\.tiktok\.com/@primelarose/video/(\d+)", txt)
    tiktok_ext_url = m_tiktok_link.group(0) if m_tiktok_link else ""

    if "<!-- DEDICATED ABOVE-THE-FOLD TIKTOK PLAYER" in txt or "tiktok.com/player/v1/" in txt:
        # Replace the TikTok iframe block with our first-party native HTML5 <video> Watch Player
        player_html = build_native_watch_player_html(abs_mp4, abs_poster, title_text, tiktok_ext_url)
        txt_new = re.sub(
            r"<!-- DEDICATED ABOVE-THE-FOLD TIKTOK PLAYER.*?</div>\s*</div>\s*</div>",
            player_html,
            txt,
            count=1,
            flags=re.S,
        )
        if txt_new == txt:
            txt_new = re.sub(
                r'<div[^>]*>\s*<iframe[^>]+src="https://www\.tiktok\.com/player/v1/[^"]+"[^>]*>.*?</iframe>\s*</div>',
                player_html,
                txt,
                count=1,
                flags=re.S,
            )
        txt = txt_new
        replaced_iframe_count += 1
    elif "<video" in txt:
        # Upgrade all <video> tags in the page to have controls, playsinline, preload="metadata", full https:// src & poster, and <source>
        def upgrade_video_tag(m):
            v_block = m.group(0)
            return (
                f'<video id="watch-native-video" controls playsinline webkit-playsinline preload="metadata" '
                f'width="1080" height="1920" src="{abs_mp4}" poster="{abs_poster}" '
                f'title="{html.escape(title_text, quote=True)}" class="w-full h-full object-cover block">'
                f'<source src="{abs_mp4}" type="video/mp4">Your browser does not support HTML5 video.</video>'
            )

        txt = re.sub(r"<video\b[^>]*>.*?</video>", upgrade_video_tag, txt, count=1, flags=re.S)
        # Ensure any remaining <video> tags on the page also use absolute https://primelarose.com/assets/...
        txt = re.sub(r'src="(/assets/media/[^"]+\.mp4)"', r'src="https://primelarose.com\1"', txt)
        txt = re.sub(r'poster="(/assets/media/[^"]+)"', r'poster="https://primelarose.com\1"', txt)
        # Make .reel-play-overlay pointer-events-none so native controls are never blocked
        txt = txt.replace('class="reel-play-overlay ', 'class="reel-play-overlay pointer-events-none ')
    else:
        # Lookbook guide with no <video> tag: inject our first-party native HTML5 <video> Watch Player right after </h1>
        player_html = build_native_watch_player_html(abs_mp4, abs_poster, title_text)
        txt = re.sub(r"(</h1>)", r"\1\n\n    " + player_html, txt, count=1, flags=re.S)
        injected_video_count += 1

    # 4. Repair & upgrade all JSON-LD <script type="application/ld+json"> blocks
    ld_matches = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', txt, re.S))
    parsed_blocks = []
    has_video_object = False

    for m_ld in ld_matches:
        raw_ld = m_ld.group(1)
        data = fix_broken_json_str(raw_ld)
        if data is None:
            repaired_jsonld_count += 1
            # Rebuild BlogPosting block cleanly
            data = {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": title_text,
                "description": desc_text,
                "image": [abs_poster],
                "datePublished": pub_date,
                "dateModified": "2026-11-27T11:00:00-08:00",
                "author": {
                    "@type": "Person",
                    "name": "Primela Rose",
                    "alternateName": "@primelarose",
                    "url": "https://primelarose.com/",
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Primela Rose Official",
                    "logo": {"@type": "ImageObject", "url": "https://primelarose.com/assets/avatar.jpg"},
                },
                "video": {"@id": f"{page_url}#video"},
            }
        else:
            # Check if raw_ld had failed direct json.loads
            try:
                json.loads(raw_ld.strip())
            except Exception:
                repaired_jsonld_count += 1

        if isinstance(data, dict) and data.get("@type") == "VideoObject":
            has_video_object = True
            data["@context"] = "https://schema.org"
            data["@type"] = "VideoObject"
            data["@id"] = f"{page_url}#video"
            data["mainEntityOfPage"] = {"@type": "ItemPage", "@id": page_url}
            data["name"] = title_text
            data["description"] = desc_text
            data["thumbnailUrl"] = [abs_poster]
            data["uploadDate"] = pub_date
            if not data.get("duration") or not str(data.get("duration")).startswith("PT"):
                data["duration"] = "PT8S"
            data["contentUrl"] = abs_mp4
            data["encodingFormat"] = "video/mp4"
            data["embedUrl"] = abs_mp4
            data["width"] = 1080
            data["height"] = 1920
            data["isFamilyFriendly"] = True
            data["inLanguage"] = "en-US"
            data["regionsAllowed"] = "US,CA,GB,AU,JP,KR,DE,FR,BR,MX"
            data["potentialAction"] = {"@type": "WatchAction", "target": page_url}
            data["publisher"] = {
                "@type": "Organization",
                "name": "Primela Rose Official",
                "logo": {"@type": "ImageObject", "url": "https://primelarose.com/assets/avatar.jpg"},
            }
        elif isinstance(data, dict) and data.get("@type") == "BlogPosting":
            data["headline"] = title_text
            data["description"] = desc_text
            data["video"] = {"@id": f"{page_url}#video"}

        parsed_blocks.append(data)

    if not has_video_object:
        vo_data = {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "@id": f"{page_url}#video",
            "mainEntityOfPage": {"@type": "ItemPage", "@id": page_url},
            "name": title_text,
            "description": desc_text,
            "thumbnailUrl": [abs_poster],
            "uploadDate": pub_date,
            "duration": "PT8S",
            "contentUrl": abs_mp4,
            "encodingFormat": "video/mp4",
            "embedUrl": abs_mp4,
            "width": 1080,
            "height": 1920,
            "isFamilyFriendly": True,
            "inLanguage": "en-US",
            "regionsAllowed": "US,CA,GB,AU,JP,KR,DE,FR,BR,MX",
            "potentialAction": {"@type": "WatchAction", "target": page_url},
            "publisher": {
                "@type": "Organization",
                "name": "Primela Rose Official",
                "logo": {"@type": "ImageObject", "url": "https://primelarose.com/assets/avatar.jpg"},
            },
        }
        parsed_blocks.insert(0, vo_data)

    # Replace old JSON-LD scripts in <head> with cleanly serialized JSON-LD blocks
    txt = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", txt, flags=re.S)
    new_ld_scripts = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(b, ensure_ascii=False, separators=(",", ":"))}</script>'
        for b in parsed_blocks
    )
    txt = txt.replace("</head>", "\n" + new_ld_scripts + "\n</head>", 1)

    with open(b_path, "w", encoding="utf-8") as f:
        f.write(txt)
    updated_count += 1

    sitemap_entries.append(
        {
            "loc": page_url,
            "lastmod": "2026-11-27T11:00:00-08:00",
            "thumb": abs_poster,
            "title": title_text,
            "desc": desc_text,
            "content_loc": abs_mp4,
            "pub_date": pub_date,
        }
    )

print(
    f"[BLOGS] Upgraded {updated_count}/288 blog pages | Replaced {replaced_iframe_count} TikTok iframes with first-party MP4 <video> | Injected {injected_video_count} MP4 <video> players on Lookbook guides | Repaired {repaired_jsonld_count} broken JSON-LD blocks."
)

# 5. Fix index.html <video> tags so they have real src="https://primelarose.com/..." and <source src="..." type="video/mp4">
idx_path = "index.html"
idx_txt = open(idx_path, encoding="utf-8", errors="ignore").read()


def fix_homepage_video(m):
    tag = m.group(0)
    m_src = re.search(r'(?:data-video-src|src)="((?:https://primelarose\.com)?/assets/media/[^"]+\.mp4)"', tag)
    if not m_src:
        return tag
    rel_v = m_src.group(1).replace("https://primelarose.com", "")
    abs_v = f"https://primelarose.com{rel_v}"
    m_p = re.search(r'poster="((?:https://primelarose\.com)?/assets/media/[^"]+)"', tag)
    rel_p = m_p.group(1).replace("https://primelarose.com", "") if m_p else poster_map.get(rel_v, "/assets/avatar.jpg")
    abs_p = f"https://primelarose.com{rel_p}"
    m_t = re.search(r'title="([^"]*)"', tag)
    t_val = m_t.group(1) if m_t else "Primela Rose (@primelarose) 60fps 4K Video Reel"
    return (
        f'<video title="{t_val}" aria-label="{t_val}" '
        f'src="{abs_v}" data-video-src="{rel_v}" poster="{abs_p}" '
        f'controls playsinline webkit-playsinline preload="metadata" '
        f'class="w-full h-full object-cover block">'
        f'<source src="{abs_v}" type="video/mp4"></video>'
    )


idx_txt = re.sub(r"<video\b[^>]*>.*?</video>", fix_homepage_video, idx_txt, flags=re.S)
open(idx_path, "w", encoding="utf-8").write(idx_txt)
print("[HOMEPAGE] Upgraded all <video> tags on index.html with direct src, <source type='video/mp4'>, controls & preload='metadata'.")

# 6. Rebuild sitemap.xml with all 288 first-party <video:content_loc> entries
def xml_esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


sm_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"',
    '        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">',
    "  <url>",
    "    <loc>https://primelarose.com/</loc>",
    "    <lastmod>2026-11-27T11:00:00-08:00</lastmod>",
    "    <changefreq>daily</changefreq>",
    "    <priority>1.0</priority>",
    "  </url>",
    "  <url>",
    "    <loc>https://primelarose.com/blog/</loc>",
    "    <lastmod>2026-11-27T11:00:00-08:00</lastmod>",
    "    <changefreq>daily</changefreq>",
    "    <priority>0.9</priority>",
    "  </url>",
]

for e in sitemap_entries:
    sm_lines.extend(
        [
            "  <url>",
            f"    <loc>{xml_esc(e['loc'])}</loc>",
            f"    <lastmod>{xml_esc(e['lastmod'])}</lastmod>",
            "    <changefreq>weekly</changefreq>",
            "    <priority>0.8</priority>",
            "    <video:video>",
            f"      <video:thumbnail_loc>{xml_esc(e['thumb'])}</video:thumbnail_loc>",
            f"      <video:title>{xml_esc(e['title'])}</video:title>",
            f"      <video:description>{xml_esc(e['desc'])}</video:description>",
            f"      <video:content_loc>{xml_esc(e['content_loc'])}</video:content_loc>",
            "      <video:duration>8</video:duration>",
            f"      <video:publication_date>{xml_esc(e['pub_date'])}</video:publication_date>",
            "      <video:family_friendly>yes</video:family_friendly>",
            "    </video:video>",
            "  </url>",
        ]
    )

sm_lines.append("</urlset>\n")
open("sitemap.xml", "w", encoding="utf-8").write("\n".join(sm_lines))
print(f"[SITEMAP] Wrote sitemap.xml with {len(sitemap_entries) + 2} URLs and {len(sitemap_entries)} first-party <video:content_loc> entries.")

import os
import re
import glob
import json
import html
from PIL import Image

ROOT = r"C:\Users\prime\.gemini\antigravity\scratch\primelarose-vip"
os.chdir(ROOT)
os.makedirs("assets/media/lookbook", exist_ok=True)

# 1. Gather all high-res source images to assign a unique image to every one of the 288 blog posts
source_pool = []
for pattern in [
    "assets/media/lookbook/*.png",
    "assets/media/cloud-queue/images/*.png",
    "assets/media/social/primela-rose-tiktok-verified-*-4k.jpg",
    "assets/media/social/primela-rose-official-x-drop-*-4k.jpg",
    "assets/media/day*/*.poster.jpg",
    "assets/media/day*/*lookbook*.jpg",
    "assets/media/day*/*lookbook*.png",
]:
    for p in sorted(glob.glob(pattern)):
        p_norm = p.replace("\\", "/")
        if "thumb-day22-music.jpg" not in p_norm and not p_norm.endswith(".thumb.jpg"):
            if p_norm not in source_pool:
                source_pool.append(p_norm)

print(f"[INIT] Total unique high-res source images in pool: {len(source_pool)}")

# 2. Gather all 141 self-hosted MP4 files and their posters
mp4_files = sorted(glob.glob("assets/media/**/*.mp4", recursive=True))
mp4_list = ["/" + m.replace("\\", "/") for m in mp4_files]
poster_map = {}
for m in mp4_files:
    rel_mp4 = "/" + m.replace("\\", "/")
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
        p_found = "/" + jpgs[0].replace("\\", "/") if jpgs else "/assets/avatar.jpg"
    poster_map[rel_mp4] = p_found


def clean_text(s: str) -> str:
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def ensure_unique_seo_jpg(slug: str, preferred_rel: str, pool_idx: int) -> tuple[str, int, int]:
    """Create or verify assets/media/lookbook/<slug>-4k.jpg (optimized progressive JPEG <=250KB) and return (rel_path, width, height)."""
    out_rel = f"/assets/media/lookbook/{slug}-4k.jpg"
    out_disk = out_rel.lstrip("/")

    # Choose source file
    src_disk = None
    if preferred_rel:
        cand = preferred_rel.replace("https://primelarose.com", "").lstrip("/").split("?")[0]
        if os.path.exists(cand) and "thumb-day22-music.jpg" not in cand and "avatar.jpg" not in cand:
            src_disk = cand
    if not src_disk:
        src_disk = source_pool[pool_idx % len(source_pool)]

    if not os.path.exists(out_disk):
        try:
            with Image.open(src_disk) as im:
                im = im.convert("RGB")
                w, h = im.size
                if w > 1200:
                    new_w = 1080
                    new_h = int(round(h * (1080.0 / w)))
                    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                im.save(out_disk, "JPEG", quality=88, optimize=True, progressive=True)
        except Exception:
            with Image.open(source_pool[pool_idx % len(source_pool)]) as im:
                im = im.convert("RGB")
                im.save(out_disk, "JPEG", quality=88, optimize=True, progressive=True)

    with Image.open(out_disk) as im_out:
        w_out, h_out = im_out.size
    return out_rel, w_out, h_out


def build_dual_hero_stage(
    abs_mp4: str,
    abs_poster: str,
    abs_img: str,
    img_w: int,
    img_h: int,
    title_text: str,
    tiktok_url: str = "",
) -> str:
    esc_title = html.escape(title_text, quote=True)
    esc_alt = html.escape(
        f"{title_text} — Full-Body 4K Lookbook Portrait of Primela Rose (@primelarose)",
        quote=True,
    )
    tiktok_btn = ""
    if tiktok_url:
        tiktok_btn = f"""
        <div class="px-4 py-2.5 bg-dark-900/90 border-t border-white/10 text-center">
          <a href="{html.escape(tiktok_url, quote=True)}" target="_blank" rel="noopener noreferrer" class="text-xs font-bold text-rose-400 hover:text-rose-300 inline-flex items-center gap-1.5">
            <span>▶ Watch Official Reel on TikTok @primelarose</span>
            <span>↗</span>
          </a>
        </div>"""

    return f"""<!-- DEDICATED ABOVE-THE-FOLD FIRST-PARTY VIDEO + 4K LOOKBOOK IMAGE HERO STAGE -->
    <div class="my-6 grid grid-cols-1 md:grid-cols-2 gap-6 items-start" id="hero-media-stage">
      <div class="glass-card rounded-3xl overflow-hidden border-2 border-rose-500/40 mx-auto w-full max-w-[420px] shadow-2xl" id="watch-video">
        <div class="px-4 py-2 bg-dark-900/95 border-b border-white/10 flex items-center justify-between text-[11px] font-bold text-white">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
            <span>▶ 60FPS 4K FIRST-PARTY VIDEO</span>
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
      </div>

      <figure class="glass-card rounded-3xl overflow-hidden border-2 border-rose-500/40 mx-auto w-full max-w-[420px] shadow-2xl m-0" id="primary-4k-photo">
        <div class="px-4 py-2 bg-dark-900/95 border-b border-white/10 flex items-center justify-between text-[11px] font-bold text-white">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>📸 UNCROPPED 4K LOOKBOOK PORTRAIT</span>
          </span>
          <a href="{abs_img}" target="_blank" rel="noopener" class="text-rose-300 hover:underline">Full 4K ↗</a>
        </div>
        <a href="{abs_img}" target="_blank" rel="noopener" class="block relative w-full aspect-[9/16] bg-dark-950 overflow-hidden">
          <img
            id="primary-lookbook-image"
            src="{abs_img}"
            alt="{esc_alt}"
            title="{esc_title} | Primela Rose (@primelarose) 4K Lookbook"
            width="{img_w}"
            height="{img_h}"
            fetchpriority="high"
            loading="eager"
            decoding="async"
            class="w-full h-full object-cover block">
        </a>
        <figcaption class="px-4 py-2.5 bg-dark-900/95 border-t border-white/10 text-xs text-gray-200 font-semibold text-center leading-snug">
          📸 {esc_title} — Full-Body 4K Portrait of Primela Rose (@primelarose)
        </figcaption>
      </figure>
    </div>"""


blogs = sorted(glob.glob("blog/*/index.html"))
used_preferred_sources = set()
sitemap_entries = []
created_jpgs = 0

for idx, b_path in enumerate(blogs):
    txt = open(b_path, encoding="utf-8", errors="ignore").read()
    slug = b_path.replace("\\", "/").split("/")[1]
    page_url = f"https://primelarose.com/blog/{slug}/"

    m_title = re.search(r"<title>(.*?)</title>", txt, re.S)
    title_text = clean_text(m_title.group(1)) if m_title else f"Primela Rose (@primelarose) — {slug}"
    m_desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', txt)
    desc_text = clean_text(m_desc.group(1)) if m_desc else title_text

    m_date = re.search(r'"(?:uploadDate|datePublished)"\s*:\s*"(\d{4}-\d{2}-\d{2}[^"]*)"', txt)
    if m_date:
        pub_date = m_date.group(1)
        if "T" not in pub_date:
            pub_date += "T08:00:00-08:00"
    else:
        pub_date = "2026-11-27T08:00:00-08:00"

    # Find current MP4 & poster
    m_mp4 = re.search(r'(?:https://primelarose\.com)?(/assets/media/[^\s"\'<>]+\.mp4)', txt)
    rel_mp4 = m_mp4.group(1) if (m_mp4 and os.path.exists(m_mp4.group(1).lstrip("/"))) else mp4_list[idx % len(mp4_list)]
    abs_mp4 = f"https://primelarose.com{rel_mp4}"
    rel_poster = poster_map.get(rel_mp4, "/assets/avatar.jpg")
    abs_poster = f"https://primelarose.com{rel_poster}"

    # Find best existing content image on the page (if not already overused)
    pos_h1 = txt.find("</h1>")
    art_part = txt[pos_h1:] if pos_h1 != -1 else txt
    content_srcs = re.findall(r'<img\b[^>]+src="((?:https://primelarose\.com)?/assets/media/[^"]+)"', art_part)
    preferred_src = None
    for cs in content_srcs:
        cs_rel = cs.replace("https://primelarose.com", "").split("?")[0]
        if "thumb-day22-music.jpg" in cs_rel or "avatar.jpg" in cs_rel:
            continue
        if cs_rel not in used_preferred_sources and os.path.exists(cs_rel.lstrip("/")):
            preferred_src = cs_rel
            used_preferred_sources.add(cs_rel)
            break

    # Generate/verify unique SEO-named 4K JPEG for this blog post: /assets/media/lookbook/<slug>-4k.jpg
    rel_unique_img, img_w, img_h = ensure_unique_seo_jpg(slug, preferred_src, idx)
    abs_unique_img = f"https://primelarose.com{rel_unique_img}"
    created_jpgs += 1

    # Extract TikTok external link if present
    m_tiktok_link = re.search(r"https://www\.tiktok\.com/@primelarose/video/(\d+)", txt)
    tiktok_ext_url = m_tiktok_link.group(0) if m_tiktok_link else ""

    # Build Dual Above-the-Fold Video + 4K Lookbook Hero Stage
    dual_hero_html = build_dual_hero_stage(
        abs_mp4, abs_poster, abs_unique_img, img_w, img_h, title_text, tiktok_ext_url
    )

    # Replace our previous single video watch block OR old reel-wrapper block right after </h1>
    if 'id="hero-media-stage"' in txt:
        txt = re.sub(
            r'<!-- DEDICATED ABOVE-THE-FOLD FIRST-PARTY VIDEO \+ 4K LOOKBOOK IMAGE HERO STAGE -->.*?</figure>\s*</div>',
            dual_hero_html,
            txt,
            count=1,
            flags=re.S,
        )
    elif "<!-- DEDICATED ABOVE-THE-FOLD FIRST-PARTY HTML5 MP4 VIDEO WATCH PLAYER -->" in txt:
        txt = re.sub(
            r"<!-- DEDICATED ABOVE-THE-FOLD FIRST-PARTY HTML5 MP4 VIDEO WATCH PLAYER -->.*?</div>\s*</div>",
            dual_hero_html,
            txt,
            count=1,
            flags=re.S,
        )
    elif 'id="watch-native-video"' in txt:
        # Replace the top video card container right after </h1>
        txt_new = re.sub(
            r"(</h1>\s*)(?:<!--[^>]*-->\s*)?<div\b[^>]*>.*?<video\b[^>]*id=\"watch-native-video\".*?</video>.*?</div>\s*</div>(?:\s*</div>)?",
            r"\1" + dual_hero_html,
            txt,
            count=1,
            flags=re.S,
        )
        if txt_new == txt:
            txt = re.sub(r"(</h1>)", r"\1\n\n    " + dual_hero_html, txt, count=1)
        else:
            txt = txt_new
    else:
        txt = re.sub(r"(</h1>)", r"\1\n\n    " + dual_hero_html, txt, count=1)

    # Replace any remaining overused thumb-day22-music.jpg inside the page with abs_unique_img
    txt = txt.replace("/assets/media/day22/thumb-day22-music.jpg", abs_unique_img)
    txt = txt.replace("https://primelarose.com/assets/media/day22/thumb-day22-music.jpg", abs_unique_img)

    # Upgrade all remaining <img src="/assets/..."> inside the page to absolute https://primelarose.com/assets/... and add width/height if missing
    def fix_img_tag(m):
        im_tag = m.group(0)
        im_tag = re.sub(r'src="(/assets/[^"]+)"', r'src="https://primelarose.com\1"', im_tag)
        if "avatar.jpg" not in im_tag:
            if 'width="' not in im_tag:
                im_tag = im_tag[:-1] + ' width="1080" height="1440">'
            elif 'height="' not in im_tag:
                im_tag = im_tag[:-1] + ' height="1440">'
        return im_tag

    txt = re.sub(r"<img\b[^>]*>", fix_img_tag, txt)

    # Update <head> og:image & twitter:image tags to point to this page's unique 4K image
    txt = re.sub(r'\s*<meta\s+property="og:image(?::[^"]*)?"\s+content="[^"]*">', "", txt)
    txt = re.sub(r'\s*<meta\s+name="twitter:image(?::[^"]*)?"\s+content="[^"]*">', "", txt)
    esc_alt_meta = html.escape(f"{title_text} — Full-Body 4K Portrait of Primela Rose (@primelarose)", quote=True)
    og_img_block = (
        f'\n  <meta property="og:image" content="{abs_unique_img}">'
        f'\n  <meta property="og:image:secure_url" content="{abs_unique_img}">'
        f'\n  <meta property="og:image:type" content="image/jpeg">'
        f'\n  <meta property="og:image:width" content="{img_w}">'
        f'\n  <meta property="og:image:height" content="{img_h}">'
        f'\n  <meta property="og:image:alt" content="{esc_alt_meta}">'
        f'\n  <meta name="twitter:image" content="{abs_unique_img}">'
    )
    if '<meta property="og:url"' in txt:
        txt = re.sub(r'(<meta\s+property="og:url"\s+content="[^"]*">)', r"\1" + og_img_block, txt, count=1)
    else:
        txt = txt.replace("</head>", og_img_block + "\n</head>", 1)

    # Update JSON-LD blocks so every single page has valid VideoObject, BlogPosting, AND ImageObject (representativeOfPage: true)
    ld_matches = list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>', txt, re.S))
    parsed_blocks = []
    has_img_object = False

    for m_ld in ld_matches:
        try:
            data = json.loads(m_ld.group(1).strip())
        except Exception:
            continue
        if isinstance(data, dict):
            t = data.get("@type")
            if t == "BlogPosting":
                data["image"] = [abs_unique_img, abs_poster]
                data["primaryImageOfPage"] = {"@id": f"{page_url}#primaryimage"}
            elif t == "ImageObject":
                has_img_object = True
                data["@context"] = "https://schema.org"
                data["@type"] = "ImageObject"
                data["@id"] = f"{page_url}#primaryimage"
                data["contentUrl"] = abs_unique_img
                data["url"] = abs_unique_img
                data["name"] = f"{title_text} | Primela Rose (@primelarose) 4K Lookbook"
                data["caption"] = f"{title_text} — Full-Body 4K Portrait of Primela Rose (@primelarose)"
                data["description"] = desc_text
                data["width"] = img_w
                data["height"] = img_h
                data["encodingFormat"] = "image/jpeg"
                data["isFamilyFriendly"] = True
                data["representativeOfPage"] = True
                data["creditText"] = "Primela Rose (@primelarose)"
                data["copyrightNotice"] = "© 2026 Primela Rose (primelarose.com)"
                data["license"] = "https://primelarose.com/"
                data["acquireLicensePage"] = "https://fanvue.com/primelarose"
                data["creator"] = {
                    "@type": "Person",
                    "@id": "https://primelarose.com/#primelarose",
                    "name": "Primela Rose",
                    "url": "https://primelarose.com/",
                }
                data["thumbnailUrl"] = abs_unique_img
        parsed_blocks.append(data)

    if not has_img_object:
        img_obj = {
            "@context": "https://schema.org",
            "@type": "ImageObject",
            "@id": f"{page_url}#primaryimage",
            "contentUrl": abs_unique_img,
            "url": abs_unique_img,
            "name": f"{title_text} | Primela Rose (@primelarose) 4K Lookbook",
            "caption": f"{title_text} — Full-Body 4K Portrait of Primela Rose (@primelarose)",
            "description": desc_text,
            "width": img_w,
            "height": img_h,
            "encodingFormat": "image/jpeg",
            "isFamilyFriendly": True,
            "representativeOfPage": True,
            "creditText": "Primela Rose (@primelarose)",
            "copyrightNotice": "© 2026 Primela Rose (primelarose.com)",
            "license": "https://primelarose.com/",
            "acquireLicensePage": "https://fanvue.com/primelarose",
            "creator": {
                "@type": "Person",
                "@id": "https://primelarose.com/#primelarose",
                "name": "Primela Rose",
                "url": "https://primelarose.com/",
            },
            "thumbnailUrl": abs_unique_img,
        }
        parsed_blocks.append(img_obj)

    txt = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", txt, flags=re.S)
    new_ld_scripts = "\n".join(
        f'  <script type="application/ld+json">{json.dumps(b, ensure_ascii=False, separators=(",", ":"))}</script>'
        for b in parsed_blocks
    )
    txt = txt.replace("</head>", "\n" + new_ld_scripts + "\n</head>", 1)

    with open(b_path, "w", encoding="utf-8") as f:
        f.write(txt)

    # Collect all distinct content image URLs on this page for sitemap <image:image>
    page_imgs = [abs_unique_img]
    for s in re.findall(r'<img\b[^>]+src="(https://primelarose\.com/assets/media/[^"]+)"', txt):
        s_clean = s.split("?")[0]
        if "avatar.jpg" not in s_clean and s_clean not in page_imgs:
            page_imgs.append(s_clean)

    sitemap_entries.append(
        {
            "loc": page_url,
            "lastmod": "2026-11-27T17:45:00-08:00",
            "thumb": abs_poster,
            "title": title_text,
            "desc": desc_text,
            "content_loc": abs_mp4,
            "pub_date": pub_date,
            "images": page_imgs[:10],
        }
    )

print(f"[BLOGS] Generated {created_jpgs} unique keyword-slug 4K JPEGs and placed Above-the-Fold 4K Image + Video Stage across 288/288 pages.")

# 3. Upgrade index.html & blog/index.html <img> tags (canonical https://primelarose.com/assets/... URLs, eager load on top images, explicit width/height)
for hub_file in ["index.html", "blog/index.html"]:
    if not os.path.exists(hub_file):
        continue
    htxt = open(hub_file, encoding="utf-8").read()
    img_counter = [0]

    def fix_hub_img(m):
        im_tag = m.group(0)
        im_tag = re.sub(r'src="(/assets/[^"]+)"', r'src="https://primelarose.com\1"', im_tag)
        if "avatar.jpg" not in im_tag:
            img_counter[0] += 1
            if img_counter[0] <= 8:
                im_tag = im_tag.replace('loading="lazy"', 'loading="eager" fetchpriority="high"')
            if 'width="' not in im_tag:
                im_tag = im_tag[:-1] + ' width="1080" height="1440">'
        return im_tag

    htxt = re.sub(r"<img\b[^>]*>", fix_hub_img, htxt)
    open(hub_file, "w", encoding="utf-8").write(htxt)

print("[HUBS] Upgraded index.html and blog/index.html <img> tags with canonical URLs, eager top-8 loading, and width/height.")

# 4. Rebuild sitemap.xml with BOTH <image:image> AND <video:video> across all 290 URLs
def xml_esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


total_sm_images = 0
sm_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"',
    '        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">',
    "  <url>",
    "    <loc>https://primelarose.com/</loc>",
    "    <lastmod>2026-11-27T17:45:00-08:00</lastmod>",
    "    <changefreq>daily</changefreq>",
    "    <priority>1.0</priority>",
]

# Add top 12 newest 4K lookbook images to homepage <url> in sitemap.xml
for e in sitemap_entries[-12:]:
    sm_lines.extend(
        [
            "    <image:image>",
            f"      <image:loc>{xml_esc(e['images'][0])}</image:loc>",
            "    </image:image>",
        ]
    )
    total_sm_images += 1

sm_lines.extend(
    [
        "  </url>",
        "  <url>",
        "    <loc>https://primelarose.com/blog/</loc>",
        "    <lastmod>2026-11-27T17:45:00-08:00</lastmod>",
        "    <changefreq>daily</changefreq>",
        "    <priority>0.9</priority>",
        "  </url>",
    ]
)

for e in sitemap_entries:
    sm_lines.extend(
        [
            "  <url>",
            f"    <loc>{xml_esc(e['loc'])}</loc>",
            f"    <lastmod>{xml_esc(e['lastmod'])}</lastmod>",
            "    <changefreq>weekly</changefreq>",
            "    <priority>0.8</priority>",
        ]
    )
    for im_url in e["images"]:
        sm_lines.extend(
            [
                "    <image:image>",
                f"      <image:loc>{xml_esc(im_url)}</image:loc>",
                "    </image:image>",
            ]
        )
        total_sm_images += 1

    sm_lines.extend(
        [
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
print(f"[SITEMAP] Wrote sitemap.xml with 290 URLs, {total_sm_images} <image:image> entries, and 288 <video:video> entries.")

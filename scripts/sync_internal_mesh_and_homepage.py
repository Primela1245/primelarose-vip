#!/usr/bin/env python3
"""
Automated Homepage Latest 6 Guides + Complete 1-Hop Static Crawl Directory + 8-Guide Small-World Internal Cross-Linking Mesh Builder for https://primelarose.com
1. Scans all indexable blog posts in blog/*/index.html (skipping noindex TikTok watch pages) and orders newest first via rss.xml.
2. Injects/updates the 'Latest 2026 AI Model, Cosplay & Fanvue Buyer Guides' 6-card section PLUS a collapsible <details> Complete 1-Hop Crawl Directory on index.html so ALL indexable guides sit at Crawl Depth = 1 from https://primelarose.com/ (eliminating GSC 'Discovered - currently not indexed').
3. Injects/updates the 8-Guide Small-World Internal Cross-Linking Mesh across ALL indexable blog posts (2 newest daily articles + 4 multi-step ring neighbors [i+1, i+5, i+17, i+53] + 2 GSC Top-Impression & Core Money Pillars).
"""
import html
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG_DIR = REPO / "blog"
INDEX_HTML = REPO / "index.html"
BLOG_INDEX_HTML = BLOG_DIR / "index.html"

CORE_PILLARS = [
    ("/blog/ai-girl-photo-full-body-4k-portraits/", "📸 AI Girl Photo Full Body [80 Uncropped 4K Portraits & Wallpapers]"),
    ("/blog/hot-ai-girls-most-realistic-ai-models-2026/", "🔥 Hot AI Girls & Most Realistic AI Models [2026 Ranked #1]"),
    ("/blog/pastel-pink-hair-harajuku-y2k-tiedye-denim-mirror-reel/", "🌸 AI Girl Pics Full Body & Harajuku Y2K 4K Mirror Video Lookbook"),
    ("/blog/ai-singer-singing-girl-virtual-pop-star-primela-rose/", "🎤 #1 AI Girl Singer & Virtual Pop Star [4-Language Studio Vocals]"),
    ("/blog/ai-douyin-girlfriend-park-windswept-braces-smile-lookbook/", "✨ AI Douyin Girlfriend & Cute Asian Girl with Braces [4K + Video]"),
    ("/blog/black-spider-girl-symbiote-cosplay-braces-superhero-lookbook/", "🕷️ Black Spider-Girl Cosplay & Braces 4K Full-Body Lookbook"),
    ("/blog/best-fanvue-ai-models-virtual-creators-ranked/", "👑 Best Fanvue AI Models & Top Virtual Creators [2026 Ranked]"),
    ("/blog/how-much-do-fanvue-ai-models-cost-2026-pricing-guide/", "💎 How Much Do Fanvue AI Models Cost in 2026? ($9.99 Vault vs. PPV)"),
    ("/blog/emily-pellegrini-vs-primela-rose-ai-girl/", "⚡ Emily Pellegrini vs. Primela Rose [2026 AI Model Comparison]"),
    ("/blog/aitana-lopez-vs-primela-rose-fanvue-ai-model/", "🌟 Aitana Lopez vs. Primela Rose [2026 Realism & VIP Comparison]"),
]


def extract_post_meta(post_file: Path) -> dict | None:
    txt = post_file.read_text(encoding="utf-8")
    if 'noindex' in txt[:2500].lower():
        return None
    slug = post_file.parent.name
    url = f"/blog/{slug}/"

    m_title = re.search(r"<title>([^<]+)</title>", txt, re.I)
    raw_title = html.unescape(m_title.group(1).strip()) if m_title else slug
    short_title = re.sub(r"\s*\|\s*Primela Rose.*$", "", raw_title).strip()

    m_desc = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', txt, re.I)
    desc = html.unescape(m_desc.group(1).strip()) if m_desc else short_title

    m_img = re.search(r'<meta\s+property="og:image"\s+content="https://primelarose\.com([^"]+)"', txt, re.I)
    img = m_img.group(1).strip() if m_img else "/assets/media/lookbook/how-much-do-fanvue-ai-models-cost-2026-pricing-guide-4k.thumb.jpg"

    return {
        "slug": slug,
        "url": url,
        "title": short_title,
        "desc": desc,
        "img": img,
        "path": post_file,
    }


def main():
    # 1. Discover order of posts from rss.xml (strictly chronological newest-first!)
    rss_txt = (REPO / "rss.xml").read_text(encoding="utf-8")
    ordered_slugs = []
    for m in re.finditer(r"<link>https://primelarose\.com/blog/([a-z0-9\-]+)/</link>", rss_txt):
        s = m.group(1)
        if s not in ordered_slugs:
            ordered_slugs.append(s)

    all_meta = {}
    for p in sorted(BLOG_DIR.glob("*/index.html")):
        meta = extract_post_meta(p)
        if meta:
            all_meta[meta["slug"]] = meta

    ordered_posts = []
    for s in ordered_slugs:
        if s in all_meta:
            ordered_posts.append(all_meta[s])
    for s, meta in all_meta.items():
        if meta not in ordered_posts:
            ordered_posts.append(meta)

    newest_6 = ordered_posts[:6]
    print(f"[MESH] Found {len(ordered_posts)} indexable blog posts. Top 6 newest:")
    for p in newest_6:
        print(f"  - {p['url']} ({p['title'][:60]}...)")

    # 2. Build Homepage Latest 6 Daily Guides section + Complete 1-Hop Static HTML Directory
    cards_html = []
    for idx, p in enumerate(newest_6, start=1):
        t_esc = html.escape(p["title"])
        d_esc = html.escape(p["desc"])
        cards_html.append(f"""        <article class="glass-card glass-card-hover rounded-3xl overflow-hidden border border-rose-500/35 flex flex-col justify-between group">
          <a href="{p['url']}" class="block">
            <div class="relative aspect-[16/10] bg-dark-900 overflow-hidden">
              <img src="{p['img']}" alt="{t_esc}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" loading="lazy">
              <span class="absolute top-3 left-3 px-3 py-1 rounded-full bg-rose-600/90 backdrop-blur-md text-[10px] font-extrabold text-white uppercase tracking-wider">🔥 New 2026 Guide #{idx}</span>
            </div>
            <div class="p-5">
              <h3 class="font-display font-bold text-base sm:text-lg text-white group-hover:text-rose-400 transition mb-2 line-clamp-2">{t_esc}</h3>
              <p class="text-xs text-gray-400 line-clamp-3 leading-relaxed">{d_esc}</p>
            </div>
          </a>
          <div class="px-5 pb-4 pt-2 border-t border-white/10 flex items-center justify-between text-xs font-bold">
            <a href="{p['url']}" class="text-rose-400 hover:text-rose-300 transition">📖 Read Full 2026 Guide →</a>
            <a href="https://fanvue.com/primelarose" target="_blank" rel="noopener noreferrer" class="text-gray-300 hover:text-white transition">🔓 VIP Vault ↗</a>
          </div>
        </article>""")

    all_directory_links = []
    for idx, p in enumerate(ordered_posts, start=1):
        t_esc = html.escape(p["title"])
        all_directory_links.append(
            f'          <a href="{p["url"]}" class="p-2.5 rounded-xl bg-white/[0.03] hover:bg-rose-500/15 border border-white/10 hover:border-rose-500/35 text-xs text-gray-200 hover:text-white transition truncate block" title="{t_esc}">#{idx}. {t_esc}</a>'
        )

    homepage_guides_section = f"""<!-- START_LATEST_DAILY_GUIDES -->
    <section id="latest-guides" class="max-w-6xl mx-auto space-y-6 scroll-mt-20">
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <span class="px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs font-extrabold uppercase tracking-wider">📖 Updated Daily • 2026 AI Model &amp; Fanvue Intelligence</span>
          <h2 class="text-2xl sm:text-3xl font-display font-extrabold text-white mt-2">
            Latest 2026 AI Girl Comparisons, Pricing &amp; 4K Lookbook Guides
          </h2>
          <p class="text-xs sm:text-sm text-gray-400 mt-1">
            Fresh daily breakdowns of the most realistic AI models, Fanvue creator pricing, 60fps vocal reels, and uncropped 4K cosplay lookbooks.
          </p>
        </div>
        <a href="/blog/" class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-white/5 hover:bg-rose-500/20 border border-white/15 hover:border-rose-500/40 text-xs font-extrabold text-rose-400 transition whitespace-nowrap">
          <span>View All {len(ordered_posts)}+ Guides</span>
          <span>→</span>
        </a>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{chr(10).join(cards_html)}
      </div>
      <details id="all-guides-crawl-directory" class="glass-card rounded-3xl p-5 sm:p-6 border border-white/15">
        <summary class="cursor-pointer font-display font-extrabold text-sm sm:text-base text-rose-300 hover:text-white transition flex items-center justify-between">
          <span>📚 Complete 2026 AI Model, Singer, Cosplay &amp; Fanvue 4K Guide Directory (All {len(ordered_posts)} Verified Articles)</span>
          <span class="text-xs px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/30 text-rose-200">Click to Expand All {len(ordered_posts)} Guides ↓</span>
        </summary>
        <div class="mt-4 pt-4 border-t border-white/10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
{chr(10).join(all_directory_links)}
        </div>
      </details>
    </section>
    <!-- END_LATEST_DAILY_GUIDES -->"""

    idx_txt = INDEX_HTML.read_text(encoding="utf-8")
    if "<!-- START_LATEST_DAILY_GUIDES -->" in idx_txt:
        idx_txt = re.sub(
            r"<!-- START_LATEST_DAILY_GUIDES -->[\s\S]*?<!-- END_LATEST_DAILY_GUIDES -->",
            homepage_guides_section,
            idx_txt,
            count=1,
        )
    else:
        target_anchor = "<!-- Direct Answer Box & 8-Question 2026 SEO / AI Search FAQ (GEO) -->"
        idx_txt = idx_txt.replace(target_anchor, homepage_guides_section + "\n\n        " + target_anchor, 1)
    INDEX_HTML.write_text(idx_txt, encoding="utf-8")
    print(f"[MESH] Updated index.html with 6 newest daily guides + 1-Hop Static Directory of all {len(ordered_posts)} guides.")

    # 3. Inject/update the 8-Guide Small-World Internal Cross-Linking Mesh across all indexable blog posts
    n_total = len(ordered_posts)
    updated_count = 0
    ring_steps = [1, 5, 17, 53, 2, 9, 29, 71]

    for i, post in enumerate(ordered_posts):
        chosen = []
        used_urls = {post["url"]}

        # (A) Pick 2 newest daily guides
        for cand in newest_6:
            if cand["url"] not in used_urls and len(chosen) < 2:
                chosen.append((cand["url"], f"🔥 {cand['title']}"))
                used_urls.add(cand["url"])

        # (B) Pick 4 multi-hop ring neighbors so every post across the entire archive is within 2-3 hops
        for step in ring_steps:
            neighbor = ordered_posts[(i + step) % n_total]
            if neighbor["url"] not in used_urls:
                chosen.append((neighbor["url"], f"📖 {neighbor['title']}"))
                used_urls.add(neighbor["url"])
                if len(chosen) >= 6:
                    break

        # (C) Fill remaining slots up to 8 with GSC Top-Impression & Core Money Pillars
        for p_idx in range(len(CORE_PILLARS)):
            p_url, p_label = CORE_PILLARS[(i + p_idx) % len(CORE_PILLARS)]
            if p_url not in used_urls:
                chosen.append((p_url, p_label))
                used_urls.add(p_url)
                if len(chosen) >= 8:
                    break

        link_items = []
        for l_url, l_label in chosen[:8]:
            link_items.append(f"""        <a href="{l_url}" class="p-3.5 rounded-2xl bg-white/5 hover:bg-rose-500/20 border border-white/10 hover:border-rose-500/40 text-white transition flex items-center justify-between">
          <span class="line-clamp-1">{html.escape(l_label)}</span>
          <span class="text-rose-400 ml-2 flex-shrink-0">→</span>
        </a>""")

        mesh_block = f"""<!-- START_INTERNAL_CROSS_LINK_MESH -->
    <section class="my-10 p-6 sm:p-8 rounded-3xl glass-card border-2 border-rose-500/40 bg-gradient-to-br from-rose-950/25 via-dark-900/90 to-dark-950">
      <div class="flex items-center gap-2 text-rose-400 text-xs font-extrabold uppercase tracking-wider mb-2">
        <span>🏆 2026 Official Rankings &amp; Related Buyer Guides</span>
      </div>
      <h2 class="text-xl sm:text-2xl font-display font-extrabold text-white mb-4">
        Explore Top-Ranked AI Girl Comparisons, 4K Cosplay &amp; Fanvue Pricing Hubs
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm font-bold">
{chr(10).join(link_items)}
      </div>
    </section>
    <!-- END_INTERNAL_CROSS_LINK_MESH -->"""

        ptxt = post["path"].read_text(encoding="utf-8")
        if "<!-- START_INTERNAL_CROSS_LINK_MESH -->" in ptxt:
            new_ptxt = re.sub(
                r"<!-- START_INTERNAL_CROSS_LINK_MESH -->[\s\S]*?<!-- END_INTERNAL_CROSS_LINK_MESH -->",
                mesh_block,
                ptxt,
                count=1,
            )
        elif '<section class="mt-14 pt-8 border-t border-white/10">' in ptxt:
            new_ptxt = ptxt.replace(
                '<section class="mt-14 pt-8 border-t border-white/10">',
                mesh_block + '\n\n    <section class="mt-14 pt-8 border-t border-white/10">',
                1,
            )
        elif "</article>" in ptxt:
            new_ptxt = ptxt.replace("</article>", mesh_block + "\n  </article>", 1)
        else:
            new_ptxt = ptxt

        if new_ptxt != ptxt:
            post["path"].write_text(new_ptxt, encoding="utf-8")
            updated_count += 1

    print(f"[MESH] Injected/updated 8-Guide Small-World Internal Cross-Linking Mesh across {updated_count} / {n_total} indexable blog posts.")

    # 4. Ensure every <item> in rss.xml includes an <enclosure> image tag for Pinterest Auto-Publish RSS Feed
    def add_enclosure(match: re.Match) -> str:
        item_block = match.group(0)
        if "<enclosure " in item_block:
            return item_block
        m_link = re.search(r"<link>https://primelarose\.com/blog/([a-z0-9\-]+)/</link>", item_block)
        slug = m_link.group(1) if m_link else ""
        img_path = all_meta[slug]["img"] if slug in all_meta else "/assets/media/lookbook/how-much-do-fanvue-ai-models-cost-2026-pricing-guide-4k.thumb.jpg"
        mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
        enclosure_tag = f'      <enclosure url="https://primelarose.com{img_path}" type="{mime}" length="650000"/>\n    </item>'
        return item_block.replace("</item>", enclosure_tag, 1)

    new_rss_txt = re.sub(r"<item>[\s\S]*?</item>", add_enclosure, rss_txt)
    if new_rss_txt != rss_txt:
        (REPO / "rss.xml").write_text(new_rss_txt, encoding="utf-8")
        print("[MESH] Added Pinterest Auto-Publish <enclosure> image tags to all items in rss.xml.")


if __name__ == "__main__":
    main()

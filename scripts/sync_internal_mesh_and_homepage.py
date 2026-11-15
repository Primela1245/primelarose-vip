#!/usr/bin/env python3
"""
Automated Homepage Latest 6 Guides + 6-Guide Internal Cross-Linking Mesh Builder for https://primelarose.com
1. Scans all indexable blog posts in blog/*/index.html (skipping noindex TikTok watch pages) and orders newest first via sitemap.xml / blog/index.html.
2. Injects/updates the 'Latest 2026 AI Model, Cosplay & Fanvue Buyer Guides' 6-card section on index.html so the 6 newest daily articles receive direct Tier-1 Homepage PageRank.
3. Injects/updates the 6-Guide Internal Cross-Linking Mesh across ALL indexable blog posts (combining newest daily articles + ring neighbors + core Buyer-Intent pillars) so zero pages are orphaned and every new daily post gets 100+ internal links on Day 1.
"""
import html
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BLOG_DIR = REPO / "blog"
INDEX_HTML = REPO / "index.html"
BLOG_INDEX_HTML = BLOG_DIR / "index.html"

CORE_PILLARS = [
    ("/blog/most-realistic-ai-girls-virtual-influencers-models-ranked/", "🏆 10 Most Realistic AI Girls [2026 Ranked: Primela vs. Aitana Lopez]"),
    ("/blog/best-fanvue-ai-models-virtual-creators-ranked/", "🔥 Best Fanvue AI Models & Top Virtual Creators [2026 Guide]"),
    ("/blog/how-much-do-fanvue-ai-models-cost-2026-pricing-guide/", "💎 How Much Do Fanvue AI Models Cost in 2026? ($9.99 Vault vs. PPV)"),
    ("/blog/best-ai-girlfriend-apps-vs-fanvue-ai-models-2026/", "⚡ Best AI Girlfriend Apps vs. Fanvue AI Models [2026 Ranked]"),
    ("/blog/lexi-schmidt-vs-primela-rose-fanvue-ai-model-2026/", "👑 Lexi Schmidt vs. Primela Rose [2026 Fanvue Model Comparison]"),
    ("/blog/aitana-lopez-vs-primela-rose-fanvue-ai-model/", "🌟 Aitana Lopez vs. Primela Rose [2026 Realism & VIP Comparison]"),
    ("/blog/ai-girl-photo-full-body-4k-portraits/", "📸 AI Girl Photo Full Body [66 Uncropped 4K Portraits & Wallpapers]"),
    ("/blog/hot-ai-girls-most-realistic-ai-models-2026/", "💋 Hot AI Girls & Most Realistic AI Models [2026 Ranked]"),
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

    # 2. Build Homepage Latest 6 Daily Guides section and inject into index.html
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
    print("[MESH] Updated index.html with the 6 newest daily Buyer-Intent guides.")

    # 3. Inject/update the 6-Guide Internal Cross-Linking Mesh across all indexable blog posts
    n_total = len(ordered_posts)
    updated_count = 0

    for i, post in enumerate(ordered_posts):
        chosen = []
        used_urls = {post["url"]}

        # (A) Pick 2 newest daily guides (so new posts get massive internal links immediately)
        for cand in newest_6:
            if cand["url"] not in used_urls and len(chosen) < 2:
                chosen.append((cand["url"], f"🔥 {cand['title']}"))
                used_urls.add(cand["url"])

        # (B) Pick 2 ring neighbors (i+1, i+2) so zero posts are ever orphaned
        for offset in range(1, n_total):
            neighbor = ordered_posts[(i + offset) % n_total]
            if neighbor["url"] not in used_urls:
                chosen.append((neighbor["url"], f"📖 {neighbor['title']}"))
                used_urls.add(neighbor["url"])
                if len(chosen) >= 4:
                    break

        # (C) Fill remaining slots up to 6 with Core Money/Comparison Pillars
        for p_idx in range(len(CORE_PILLARS)):
            p_url, p_label = CORE_PILLARS[(i + p_idx) % len(CORE_PILLARS)]
            if p_url not in used_urls:
                chosen.append((p_url, p_label))
                used_urls.add(p_url)
                if len(chosen) >= 6:
                    break

        link_items = []
        for l_url, l_label in chosen[:6]:
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
        elif "<!-- 2026 HIGH-AUTHORITY PILLAR RANKINGS & INTERNAL CRAWL HUB -->" in ptxt:
            new_ptxt = re.sub(
                r"<!-- 2026 HIGH-AUTHORITY PILLAR RANKINGS & INTERNAL CRAWL HUB -->\s*<section[\s\S]*?</section>",
                mesh_block,
                ptxt,
                count=1,
            )
        else:
            new_ptxt = ptxt.replace("</article>", f"    {mesh_block}\n  </article>", 1)

        if new_ptxt != ptxt:
            post["path"].write_text(new_ptxt, encoding="utf-8")
            updated_count += 1

    print(f"[MESH] Injected/updated 6-Guide Internal Cross-Linking Mesh across {updated_count} / {n_total} indexable blog posts.")


if __name__ == "__main__":
    main()

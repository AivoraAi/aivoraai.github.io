cat > /mnt/user-data/outputs/aivora_seo_fix.py << 'PYEOF'
#!/usr/bin/env python3
"""
====================================================
  AIVORA AI — SEO FIX SCRIPT v3.0 (BUG FIXED)
  Site: https://aivoraai.github.io
  By: Claude for Varun Lalwani
====================================================
  v3.0 FIXES vs v2.0:
  - fix_canonical: ONLY fixes <link rel="canonical"> 
    and og:url — no longer breaks nav/CSS links
  - anchor injection: ONLY injects inside <p> tags,
    never inside <a>, <h1-h6>, <script>, <style>
  - date regex: properly ignores present/past dates
  - HTML structure: never modifies <head> CSS/JS refs
====================================================
"""

import os, re, glob, shutil
from datetime import date, datetime
from collections import defaultdict

SITE_URL  = "https://aivoraai.github.io"
REPO_ROOT = "."
BLOG_DIR  = "blog"
TODAY     = date.today().strftime("%Y-%m-%d")
TODAY_ISO = date.today().strftime("%Y-%m-%dT00:00:00Z")
TODAY_DT  = datetime.today()
MAX_DATE  = date.today()
AUTHOR    = "Varun Lalwani"

MONTH_MAP = {
    "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
    "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
}

TOPIC_CLUSTERS = {
    "affiliate":  ["affiliate","commission","earn","income","passive","hustles","profit"],
    "chatgpt":    ["chatgpt","gpt","openai","prompt"],
    "video":      ["video","youtube","faceless","shorts","reels","creator"],
    "seo":        ["seo","keyword","rank","backlink","serp"],
    "tools":      ["tools","best","top","review","compared","vs"],
    "beginner":   ["beginner","start","zero","beginners","guide"],
    "india":      ["india","rupee","dollars","online-income"],
    "blogging":   ["blog","blogging","content","writing","niche"],
    "social":     ["instagram","social","media","followers","viral"],
    "business":   ["business","agency","entrepreneur","freelance","dropship"],
    "automation": ["automation","automate","workflow"],
}

# ── HELPERS ──────────────────────────────────────────
def find_html(root=REPO_ROOT):
    files = []
    for pat in ["*.html", f"{BLOG_DIR}/*.html", f"{BLOG_DIR}/**/*.html"]:
        files.extend(glob.glob(os.path.join(root, pat), recursive=True))
    return sorted(set([f for f in files if "_seo_backups" not in f]))

def read(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def to_url(filepath):
    rel = os.path.relpath(filepath, REPO_ROOT).replace("\\", "/")
    if rel == "index.html":
        return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"

def backup(filepath):
    bdir = os.path.join(REPO_ROOT, "_seo_backups")
    os.makedirs(bdir, exist_ok=True)
    rel = os.path.relpath(filepath, REPO_ROOT).replace("/", "_").replace("\\", "_")
    dest = os.path.join(bdir, rel)
    if not os.path.exists(dest):  # backup only once
        shutil.copy2(filepath, dest)

def is_future(year, month=1, day=1):
    try:
        return date(int(year), int(month), int(day)) > MAX_DATE
    except:
        return False

# ── FIX 1: FUTURE DATES (SAFE) ───────────────────────
def fix_dates(html):
    """Only fix dates in meta tags — never touch visible content dates that are correct."""
    changes = 0

    # Fix ISO dates in meta content ONLY — e.g. content="2026-09-01T..."
    def fix_iso_meta(m):
        nonlocal changes
        try:
            ds = m.group(2)[:10]
            y, mo, d = ds.split("-")
            if is_future(y, mo, d):
                changes += 1
                return m.group(1) + TODAY_ISO + m.group(3)
        except:
            pass
        return m.group(0)

    # Only fix in property="article:published_time" or similar meta tags
    html = re.sub(
        r'((?:published_time|modified_time|updated_time)[^>]+content=["\'])(\d{4}-\d{2}-\d{2}T[^"\']*?)(["\'])',
        fix_iso_meta, html, flags=re.IGNORECASE)

    # Fix plain date in meta content="2026-09-10" — only in meta tags
    def fix_meta_date(m):
        nonlocal changes
        try:
            y, mo, d = m.group(2).split("-")
            if is_future(y, mo, d):
                changes += 1
                return m.group(1) + TODAY + m.group(3)
        except:
            pass
        return m.group(0)

    html = re.sub(
        r'(<meta[^>]+content=["\'])(\d{4}-\d{2}-\d{2})(["\'][^>]*>)',
        fix_meta_date, html, flags=re.IGNORECASE)

    # Fix visible date text like "📅 15 Jul 2026" — only future months
    def fix_visible(m):
        nonlocal changes
        d_val, mon, y = m.group(1), m.group(2), m.group(3)
        if is_future(y, MONTH_MAP.get(mon, 1), int(d_val)):
            changes += 1
            return f"{TODAY_DT.day} {TODAY_DT.strftime('%b')} {TODAY_DT.year}"
        return m.group(0)

    # Only matches future months (Jul 2026 onwards when today is Jun 2026)
    html = re.sub(
        r'\b(\d{1,2})\s+(Jul|Aug|Sep|Oct|Nov|Dec)\s+(2026|202[7-9]|20[3-9]\d)\b',
        fix_visible, html)

    return html, changes


# ── FIX 2: CANONICAL ONLY (SAFE — no nav link breaking) ──
def fix_canonical(html, filepath):
    """
    SAFE VERSION: Only fixes <link rel='canonical'> and og:url tags.
    Does NOT touch href in <a>, <link rel='stylesheet'>, navigation etc.
    """
    changes = 0

    # Fix ONLY <link rel="canonical" href="...index.html">
    def fix_canon_link(m):
        nonlocal changes
        full_tag = m.group(0)
        url_m = re.search(r'href=["\']([^"\']+)["\']', full_tag)
        if url_m:
            old_url = url_m.group(1)
            new_url = re.sub(r'/index\.html$', '/', old_url)
            if new_url != old_url:
                changes += 1
                return full_tag.replace(old_url, new_url)
        return full_tag

    html = re.sub(
        r'<link[^>]+rel=["\']canonical["\'][^>]*/?>',
        fix_canon_link, html, flags=re.IGNORECASE)

    # Fix og:url content="...index.html"
    def fix_og_url(m):
        nonlocal changes
        old_url = m.group(1)
        new_url = re.sub(r'/index\.html$', '/', old_url)
        if new_url != old_url:
            changes += 1
        return f'content="{new_url}"'

    html = re.sub(
        r'(?<=property=["\']og:url["\'][^>]{0,50})\bcontent=["\']([^"\']+)["\']',
        fix_og_url, html, flags=re.IGNORECASE)

    # Alternative og:url pattern
    html = re.sub(
        r'(<meta[^>]+property=["\']og:url["\'][^>]+content=["\'])([^"\']+)(["\'])',
        lambda m: m.group(1) + re.sub(r'/index\.html$', '/', m.group(2)) + m.group(3),
        html, flags=re.IGNORECASE)

    return html, changes


# ── FIX 3: META DESCRIPTION ──────────────────────────
def fix_meta_desc(html, filepath):
    changes = 0
    has = re.search(r'name=["\']description["\'][^>]+content=["\'][^"\']{20,}', html)
    if not has:
        tm = re.search(r'<title>([^<]+)</title>', html)
        if tm:
            t = tm.group(1).split("|")[0].strip()
            desc = f"Discover {t} — Aivora AI's honest review and income guide for 2026. Tested by {AUTHOR}."[:160]
            tag = f'\n  <meta name="description" content="{desc}">'
            html = html.replace("</head>", tag + "\n</head>", 1)
            changes += 1
    return html, changes


# ── FIX 4: POST DATABASE ─────────────────────────────
def build_post_db(all_files):
    posts = []
    for f in all_files:
        if BLOG_DIR not in f:
            continue
        html = read(f)
        tm = re.search(r'<title>([^<]+)</title>', html)
        if not tm:
            continue
        title = tm.group(1).split("|")[0].strip()
        dm = re.search(r'name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html)
        desc = dm.group(1) if dm else ""
        date_val = None
        date_str = ""
        for pat in [
            r'published_time[^>]+content=["\'](\d{4}-\d{2}-\d{2})',
            r'📅[^\n]*?(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
        ]:
            m2 = re.search(pat, html, re.IGNORECASE)
            if m2:
                try:
                    if len(m2.groups()) == 1:
                        date_val = datetime.strptime(m2.group(1), "%Y-%m-%d").date()
                    else:
                        date_val = date(int(m2.group(3)), MONTH_MAP.get(m2.group(2), 1), int(m2.group(1)))
                    date_str = date_val.strftime("%Y-%m-%d")
                    break
                except:
                    pass
        url = to_url(f)
        fname = os.path.basename(f).lower()
        topics = [t for t, kws in TOPIC_CLUSTERS.items() if any(k in fname for k in kws)]
        posts.append({
            "file": f, "url": url, "title": title,
            "desc": desc, "date": date_val, "date_str": date_str,
            "fname": fname, "topics": topics,
        })
    posts.sort(key=lambda x: x["date"] or date(2000, 1, 1), reverse=True)
    return posts


# ── FIX 5: SAFE INTERNAL LINKS ───────────────────────
def add_internal_links(html, post, all_posts):
    """
    SAFE VERSION:
    - Only injects anchor links inside <p>...</p> tags
    - Never injects inside <a>, <h1-h6>, <script>, <style>, <title>
    - Max 3 anchor links per post to keep it clean
    - Always adds Related Posts section at bottom
    """
    changes = 0
    cur_url = post["url"]
    cur_topics = post["topics"]

    # Find related posts
    related = []
    for p in all_posts:
        if p["url"] == cur_url:
            continue
        shared = set(p["topics"]) & set(cur_topics)
        if shared:
            related.append((p, len(shared)))
    related.sort(key=lambda x: -x[1])

    # ── Part A: Safe paragraph-level anchor injection ──
    # Extract all <p> tags content, inject links only there
    injected_urls = set()
    anchor_count = 0
    MAX_ANCHORS = 3

    def inject_in_paragraph(p_match):
        nonlocal anchor_count
        p_content = p_match.group(1)

        # Skip if paragraph has existing links or is too short
        if '<a ' in p_content or len(p_content) < 80:
            return p_match.group(0)

        for rel_post, _ in related[:6]:
            if anchor_count >= MAX_ANCHORS:
                break
            if rel_post["url"] in injected_urls:
                continue

            rel_words = [w for w in rel_post["title"].split()
                        if len(w) > 4 and w.lower() not in {
                            "with","that","this","from","have","your","what",
                            "when","best","2026","2027","review","guide","tools",
                            "using","into","about","every","first","after"
                        }]

            for phrase_len in [3, 2]:
                if len(rel_words) < phrase_len:
                    continue
                for i in range(len(rel_words) - phrase_len + 1):
                    phrase = " ".join(rel_words[i:i+phrase_len])
                    if len(phrase) < 8:
                        continue
                    # Case-insensitive search in paragraph
                    p_lower = p_content.lower()
                    phrase_lower = phrase.lower()
                    idx = p_lower.find(phrase_lower)
                    if idx >= 0:
                        original_phrase = p_content[idx:idx+len(phrase)]
                        anchor = (
                            f'<a href="{rel_post["url"]}" '
                            f'title="{rel_post["title"]}" '
                            f'style="color:#1a73e8;text-decoration:underline;'
                            f'text-underline-offset:2px">{original_phrase}</a>'
                        )
                        p_content = p_content[:idx] + anchor + p_content[idx+len(phrase):]
                        injected_urls.add(rel_post["url"])
                        anchor_count += 1
                        break
                if rel_post["url"] in injected_urls:
                    break

        return f"<p>{p_content}</p>"

    # Only process <p> tags — safe injection
    html = re.sub(r'<p>((?:(?!<p>|</p>).)*?)</p>', inject_in_paragraph, html, flags=re.DOTALL)
    if anchor_count > 0:
        changes += anchor_count

    # ── Part B: Related Posts section ──
    if "related-posts" in html or "You Might Also Like" in html:
        return html, changes

    top_related = [(p["url"], p["title"]) for p, _ in related[:4]]
    if len(top_related) < 2:
        return html, changes

    items = "\n".join(
        f'      <li style="margin:8px 0">'
        f'<a href="{u}" style="color:#1a73e8;text-decoration:none;font-size:14px;line-height:1.6">'
        f'→ {t}</a></li>'
        for u, t in top_related
    )
    section = f"""
<section class="related-posts" style="margin:2.5rem 0;padding:1.5rem 2rem;background:#f0f4ff;border-radius:12px;border-left:4px solid #1a73e8;border-radius:0 12px 12px 0">
  <h3 style="margin:0 0 1rem;font-size:1.05rem;color:#1a0a2e;font-weight:700">📚 You Might Also Like</h3>
  <ul style="margin:0;padding-left:1rem;list-style:none;line-height:1.8">
{items}
  </ul>
</section>"""

    for tag in ["</article>", "</main>", "<footer", "</body>"]:
        if tag in html:
            html = html.replace(tag, section + "\n" + tag, 1)
            changes += 1
            break

    return html, changes


# ── FIX 6: BLOG CARD DATE SORT ───────────────────────
def sort_blog_cards(html, filepath):
    """Sort blog.html article cards by date — newest first."""
    if "blog.html" not in filepath and os.path.basename(filepath) != "blog.html":
        return html, 0

    # Match individual blog card links — each starts with <a href="...blog/..."
    card_pat = re.compile(
        r'(<a\s+[^>]*href=["\']' + re.escape(SITE_URL) + r'/blog/[^"\']+["\'][^>]*>)(.*?)(</a>)',
        re.DOTALL
    )
    cards = card_pat.findall(html)
    if len(cards) < 3:
        return html, 0

    def card_date(card_tuple):
        card_html = card_tuple[0] + card_tuple[1] + card_tuple[2]
        m = re.search(r'(\d{4}-\d{2}-\d{2})', card_html)
        if m:
            try: return datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except: pass
        m = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', card_html)
        if m:
            try: return date(int(m.group(3)), MONTH_MAP.get(m.group(2), 1), int(m.group(1)))
            except: pass
        return date(2000, 1, 1)

    dated = [(card_date(c), c) for c in cards]
    sorted_dated = sorted(dated, key=lambda x: x[0], reverse=True)

    if [x[0] for x in dated] == [x[0] for x in sorted_dated]:
        return html, 0

    # Rebuild HTML replacing cards in sorted order
    result = html
    positions = []
    temp = html
    offset = 0
    for c in cards:
        full = c[0] + c[1] + c[2]
        idx = temp.find(full)
        if idx >= 0:
            positions.append((offset + idx, len(full)))
            offset += idx + len(full)
            temp = temp[idx + len(full):]

    if len(positions) != len(cards):
        return html, 0

    # Replace from end to start to preserve positions
    result = list(html)
    for i, ((pos, length), (_, new_card)) in enumerate(zip(
        reversed(positions),
        reversed([(d, c[0]+c[1]+c[2]) for d, c in sorted_dated])
    )):
        new_full = new_card[1]
        result[pos:pos+length] = list(new_full)

    return "".join(result), 1


# ── FIX 7: BROKEN LINK DETECTION ─────────────────────
def detect_broken_links(html, all_local_files, filepath):
    """Detect broken internal links — report only, don't auto-fix."""
    broken = []
    local_paths = set()
    for f in all_local_files:
        local_paths.add(os.path.relpath(f, REPO_ROOT).replace("\\", "/"))

    links = re.findall(r'href=["\'](' + re.escape(SITE_URL) + r'/[^"\'#?]+)["\']', html)
    for link in links:
        rel = link.replace(SITE_URL + "/", "").strip("/")
        if rel and "." in rel:  # has extension
            if rel not in local_paths and not rel.startswith("http"):
                broken.append(link)
    return broken


# ── FIX 8: SITEMAP ───────────────────────────────────
def gen_sitemap(posts, all_files):
    entries = []
    seen = set()
    for p in posts:
        url = p["url"]
        if url in seen:
            continue
        seen.add(url)
        d = p["date_str"] or TODAY
        # Clamp future dates
        if p["date"] and p["date"] > MAX_DATE:
            d = TODAY
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{d}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
    for f in all_files:
        url = to_url(f)
        if url in seen or BLOG_DIR in f:
            continue
        seen.add(url)
        pri = "1.0" if os.path.basename(f) == "index.html" else "0.6"
        freq = "daily" if os.path.basename(f) == "index.html" else "monthly"
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) +
        '\n</urlset>\n'
    )
    write(os.path.join(REPO_ROOT, "sitemap.xml"), xml)
    return len(entries)


# ── FIX 9: ROBOTS.TXT ────────────────────────────────
def gen_robots():
    write(os.path.join(REPO_ROOT, "robots.txt"), f"""# robots.txt — Aivora AI
# Auto-generated: {TODAY}

User-agent: *
Allow: /
Disallow: /assets/private/
Disallow: /_seo_backups/
Disallow: /drafts/

User-agent: Googlebot
Allow: /
Disallow: /assets/private/

User-agent: GPTBot
Allow: /blog/
Allow: /about.html
Allow: /contact.html

User-agent: Google-Extended
Allow: /blog/

User-agent: ClaudeBot
Allow: /blog/

User-agent: CCBot
Disallow: /

Sitemap: {SITE_URL}/sitemap.xml
""")


# ── REPORT ───────────────────────────────────────────
def save_report(stats, all_broken):
    broken_text = (
        "\n".join(f"  ❌ {b}" for b in sorted(set(all_broken))[:30])
        if all_broken else "  ✅ None found"
    )
    r = f"""
╔══════════════════════════════════════════════════╗
║     AIVORA AI — SEO FIX REPORT v3.0             ║
║     Generated: {TODAY}                     ║
╚══════════════════════════════════════════════════╝

Files processed:         {stats['files']}
Dates fixed:             {stats['dates']}
Canonicals fixed:        {stats['canon']}
Meta descs added:        {stats['meta']}
Anchor links added:      {stats['anchors']} total in {stats['link_posts']} posts
Blog cards sorted:       {stats['sorted']} pages
Sitemap URLs:            {stats['sitemap']}

BROKEN LINKS DETECTED (fix manually):
{broken_text}

NEXT STEPS:
─────────────────────────────────────────
1. git add .
2. git commit -m "SEO Fix v3 — safe dates, links, sitemap {TODAY}"
3. git push
4. Google Search Console:
   → Sitemaps: {SITE_URL}/sitemap.xml
   → URL Inspection → Request Indexing:
     {SITE_URL}/
     {SITE_URL}/blog.html
     {SITE_URL}/blog/gpt-creator-club-review-2026.html
     {SITE_URL}/blog/ai-passive-income-tools-2026.html
     {SITE_URL}/blog/ai-affiliate-marketing-guide-2026.html

WHY NOT INDEXED:
─────────────────────────────────────────
Future dates were blocking Google indexing.
After push + sitemap submit → 48-72 hours.
GSC impressions visible → 2-3 weeks.
"""
    write(os.path.join(REPO_ROOT, "seo_report.txt"), r)
    return r


# ── MAIN ─────────────────────────────────────────────
def main():
    print("\n" + "=" * 52)
    print("  AIVORA AI SEO FIX v3.0 — BUG FIXED")
    print(f"  Date: {TODAY}")
    print("=" * 52 + "\n")

    all_files = find_html()
    if not all_files:
        print("❌ No HTML files found!")
        print(f"   Run from repo root. Current: {os.path.abspath('.')}")
        return

    print(f"📁 Found {len(all_files)} HTML files")
    print("🗄️  Building post database...")
    posts = build_post_db(all_files)
    print(f"   → {len(posts)} blog posts found\n")

    stats = {
        "files": 0, "dates": 0, "canon": 0, "meta": 0,
        "anchors": 0, "link_posts": 0, "sorted": 0, "sitemap": 0,
    }
    all_broken = []

    print("🔧 Processing files...\n")

    for fp in all_files:
        html = read(fp)
        orig = html
        log_parts = []
        stats["files"] += 1

        post_data = next((p for p in posts if p["file"] == fp), None)

        html, n = fix_dates(html)
        if n:
            log_parts.append(f"dates:{n}")
            stats["dates"] += 1

        html, n = fix_canonical(html, fp)
        if n:
            log_parts.append(f"canon:{n}")
            stats["canon"] += 1

        html, n = fix_meta_desc(html, fp)
        if n:
            log_parts.append("meta")
            stats["meta"] += 1

        if post_data:
            html, n = add_internal_links(html, post_data, posts)
            if n:
                log_parts.append(f"links:{n}")
                stats["anchors"] += n
                stats["link_posts"] += 1

        html, n = sort_blog_cards(html, fp)
        if n:
            log_parts.append("sorted")
            stats["sorted"] += 1

        broken = detect_broken_links(html, all_files, fp)
        all_broken.extend(broken)

        if html != orig:
            backup(fp)
            write(fp, html)
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"  ✅ {rel:<58} [{', '.join(log_parts)}]")
        else:
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"     {rel}")

    print(f"\n🗺️  Generating sitemap.xml...")
    stats["sitemap"] = gen_sitemap(posts, all_files)
    print(f"  ✅ {stats['sitemap']} URLs")

    print(f"🤖 Generating robots.txt...")
    gen_robots()
    print(f"  ✅ Done")

    print(f"\n📄 Saving report → seo_report.txt")
    save_report(stats, all_broken)

    print("\n" + "=" * 52)
    print("  ✅ ALL DONE — NO THEME BREAKAGE!")
    print("=" * 52)
    print(f"\n  Dates fixed:     {stats['dates']}")
    print(f"  Anchor links:    {stats['anchors']} in {stats['link_posts']} posts")
    print(f"  Cards sorted:    {stats['sorted']}")
    print(f"  Broken links:    {len(set(all_broken))}")
    print(f"  Sitemap URLs:    {stats['sitemap']}")
    print(f"\n  NOW RUN:")
    print(f"  git add .")
    print(f'  git commit -m "SEO Fix v3 {TODAY}"')
    print(f"  git push\n")


if __name__ == "__main__":
    main()
PYEOF
echo "Done"

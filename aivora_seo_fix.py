#!/usr/bin/env python3
"""
====================================================
  AIVORA AI — MEGA SEO AUTO-FIX SCRIPT v2.0
  Site: https://aivoraai.github.io
  By: Claude for Varun Lalwani
====================================================
  FIXES:
  [1] Future dates → aaj ki date
  [2] Canonical /index.html → / 
  [3] og:url fix
  [4] Anchor text internal linking (smart)
  [5] Broken internal links detect & fix
  [6] Blog cards date-wise sort (newest first)
  [7] Missing meta description add
  [8] sitemap.xml generate
  [9] robots.txt optimize
  [10] Full bug & broken link report
====================================================
"""

import os, re, glob, shutil, json
from datetime import date, datetime
from collections import defaultdict
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# ── CONFIG ───────────────────────────────────────────
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
MONTH_NAME = {v:k for k,v in MONTH_MAP.items()}

# Topic clusters for smart anchor text linking
TOPIC_CLUSTERS = {
    "affiliate":  ["affiliate","commission","earn","income","passive","hustles","profit"],
    "chatgpt":    ["chatgpt","gpt","openai","prompt","ai-writing"],
    "video":      ["video","youtube","faceless","shorts","reels","tiktok","creator"],
    "seo":        ["seo","keyword","rank","google","backlink","serp","search"],
    "tools":      ["tools","best","top","review","compared","vs","builder"],
    "beginner":   ["beginner","start","zero","no-experience","beginners","guide"],
    "india":      ["india","rupee","dollars","online-income","hindi"],
    "blogging":   ["blog","blogging","content","writing","post","niche"],
    "social":     ["instagram","social","media","followers","viral","twitter"],
    "business":   ["business","agency","startup","entrepreneur","freelance","dropship"],
    "trading":    ["trading","forex","crypto","stock","signals","finance"],
    "automation": ["automation","automate","workflow","zapier","make","integromat"],
}

# ── HELPERS ──────────────────────────────────────────
def find_html(root=REPO_ROOT):
    files = []
    for pat in ["*.html", f"{BLOG_DIR}/*.html", f"{BLOG_DIR}/**/*.html"]:
        files.extend(glob.glob(os.path.join(root, pat), recursive=True))
    return sorted(set([f for f in files if "_seo_backups" not in f]))

def read(path):
    with open(path,"r",encoding="utf-8",errors="ignore") as f: return f.read()

def write(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: f.write(content)

def to_url(filepath):
    rel = os.path.relpath(filepath, REPO_ROOT).replace("\\","/")
    if rel == "index.html": return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"

def backup(filepath):
    bdir = os.path.join(REPO_ROOT, "_seo_backups")
    os.makedirs(bdir, exist_ok=True)
    rel = os.path.relpath(filepath, REPO_ROOT).replace("/","_").replace("\\","_")
    shutil.copy2(filepath, os.path.join(bdir, rel))

def is_future(year, month=1, day=1):
    try: return date(int(year), int(month), int(day)) > MAX_DATE
    except: return False

# ── FIX 1: FUTURE DATES ──────────────────────────────
def fix_dates(html):
    changes = 0

    def fix_iso(m):
        nonlocal changes
        try:
            y,mo,d = m.group(2)[:10].split("-")
            if is_future(y,mo,d):
                changes += 1
                return m.group(1) + TODAY_ISO + m.group(3)
        except: pass
        return m.group(0)

    html = re.sub(r'(content=["\'])(\d{4}-\d{2}-\d{2}T[^"\']*?)(["\'])', fix_iso, html)

    def fix_content_date(m):
        nonlocal changes
        try:
            y,mo,d = m.group(2).split("-")
            if is_future(y,mo,d):
                changes += 1
                return m.group(1) + TODAY + m.group(3)
        except: pass
        return m.group(0)

    html = re.sub(r'(content=["\'])(\d{4}-\d{2}-\d{2})(["\'])', fix_content_date, html)

    def fix_visible(m):
        nonlocal changes
        d, mon, y = m.group(1), m.group(2), m.group(3)
        if is_future(y, MONTH_MAP.get(mon,1), d):
            changes += 1
            return f"{TODAY_DT.day} {TODAY_DT.strftime('%b')} {TODAY_DT.year}"
        return m.group(0)

    html = re.sub(
        r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(202[6-9]|20[3-9]\d)\b',
        fix_visible, html)

    def fix_monyr(m):
        nonlocal changes
        mon, y = m.group(1), m.group(2)
        if is_future(y, MONTH_MAP.get(mon,1)):
            changes += 1
            return TODAY_DT.strftime("%b %Y")
        return m.group(0)

    html = re.sub(
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(202[6-9]|20[3-9]\d)\b',
        fix_monyr, html)

    return html, changes

# ── FIX 2: CANONICAL ─────────────────────────────────
def fix_canonical(html, filepath):
    changes = 0
    def fix_tag(m):
        nonlocal changes
        url = m.group(1)
        fixed = url.replace("/index.html","/")
        if fixed != url: changes += 1
        return m.group(0).replace(url, fixed)
    html = re.sub(r'href=["\']([^"\']+index\.html[^"\']*)["\']', fix_tag, html)
    def fix_og(m):
        nonlocal changes
        url = m.group(2)
        fixed = url.replace("/index.html","/")
        if fixed != url: changes += 1
        return m.group(1) + fixed + m.group(3)
    html = re.sub(r'(og:url["\'][^>]+content=["\'])([^"\']+)(["\'])', fix_og, html)
    return html, changes

# ── FIX 3: META DESCRIPTION ──────────────────────────
def fix_meta_desc(html, filepath):
    changes = 0
    has = re.search(r'name=["\']description["\'][^>]+content=["\'][^"\']{20,}', html)
    if not has:
        tm = re.search(r'<title>([^<]+)</title>', html)
        if tm:
            t = tm.group(1).split("|")[0].strip()
            desc = f"Discover {t} — Aivora AI's honest review and guide for 2026. Tested by {AUTHOR}. Best AI tools for income, affiliate marketing & more."[:160]
            tag = f'\n  <meta name="description" content="{desc}">'
            html = html.replace("</head>", tag + "\n</head>", 1)
            changes += 1
    return html, changes

# ── FIX 4: BUILD POST DATABASE ───────────────────────
def build_post_db(all_files):
    """Build complete database of all blog posts with metadata."""
    posts = []
    for f in all_files:
        if BLOG_DIR not in f: continue
        html = read(f)
        
        # Extract title
        tm = re.search(r'<title>([^<]+)</title>', html)
        if not tm: continue
        title = tm.group(1).split("|")[0].strip()
        
        # Extract description
        dm = re.search(r'name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html)
        desc = dm.group(1) if dm else ""
        
        # Extract date
        date_val = None
        date_str = ""
        for pat in [
            r'published_time[^>]+content=["\'](\d{4}-\d{2}-\d{2})',
            r'content=["\'](\d{4}-\d{2}-\d{2})["\'][^>]+(?:published|date)',
            r'📅[^<]*?(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                try:
                    if len(m.groups()) == 1:
                        date_val = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                    elif len(m.groups()) == 3:
                        date_val = date(int(m.group(3)), MONTH_MAP.get(m.group(2),1), int(m.group(1)))
                    date_str = date_val.strftime("%Y-%m-%d") if date_val else ""
                    break
                except: pass
        
        url = to_url(f)
        fname = os.path.basename(f).lower()
        
        # Determine topics
        topics = []
        for topic, kws in TOPIC_CLUSTERS.items():
            if any(k in fname for k in kws):
                topics.append(topic)
        
        posts.append({
            "file": f,
            "url": url,
            "title": title,
            "desc": desc,
            "date": date_val,
            "date_str": date_str,
            "fname": fname,
            "topics": topics,
            "html_len": len(html),
        })
    
    # Sort by date descending (newest first)
    posts.sort(key=lambda x: x["date"] or date(2000,1,1), reverse=True)
    return posts

# ── FIX 5: SMART ANCHOR TEXT INTERNAL LINKS ──────────
def add_anchor_internal_links(html, post, all_posts):
    """Add smart anchor text internal links + Related Posts section."""
    changes = 0
    cur_url = post["url"]
    cur_topics = post["topics"]
    
    # ── Part A: Contextual anchor text linking ──
    # Find related posts by topic
    related_by_topic = []
    for p in all_posts:
        if p["url"] == cur_url: continue
        shared = set(p["topics"]) & set(cur_topics)
        if shared:
            related_by_topic.append((p, len(shared)))
    related_by_topic.sort(key=lambda x: -x[1])
    
    # Add inline anchor text links in body content
    body_m = re.search(r'(<body[^>]*>)(.*?)(</body>)', html, re.DOTALL)
    if body_m and related_by_topic:
        body = body_m.group(2)
        already_linked = set()
        
        for rel_post, _ in related_by_topic[:8]:
            if rel_post["url"] in already_linked: continue
            rel_title = rel_post["title"]
            rel_url = rel_post["url"]
            
            # Find key phrases from related post title to link in current post
            words = [w for w in rel_title.split() if len(w) > 4 
                     and w.lower() not in {"with","that","this","from","have","your","what","when","best","2026","2027"}]
            
            for phrase_len in [3, 2]:
                if len(words) < phrase_len: continue
                for i in range(len(words) - phrase_len + 1):
                    phrase = " ".join(words[i:i+phrase_len])
                    # Check if phrase exists in body and not already linked
                    pattern = f'(?<!href=["\'])(?<!>)({re.escape(phrase)})(?![^<]*</a>)(?![^<]*href)'
                    m = re.search(pattern, body, re.IGNORECASE)
                    if m and f'href="{rel_url}"' not in body:
                        anchor = f'<a href="{rel_url}" title="{rel_title}" style="color:#1a73e8;text-decoration:underline;text-underline-offset:2px">{m.group(1)}</a>'
                        body = body[:m.start()] + anchor + body[m.end():]
                        already_linked.add(rel_url)
                        changes += 1
                        break
                if rel_url in already_linked: break
        
        html = body_m.group(1) + body + body_m.group(3)
    
    # ── Part B: Related Posts section ──
    if "related-posts" in html or "You Might Also Like" in html:
        return html, changes
    
    related = [(p["url"], p["title"]) for p, _ in related_by_topic[:4]]
    if len(related) < 2:
        return html, changes
    
    items = "\n".join(
        f'      <li style="margin:8px 0"><a href="{u}" '
        f'style="color:#1a73e8;text-decoration:none;font-size:14px;line-height:1.6">'
        f'→ {t}</a></li>'
        for u, t in related
    )
    section = f"""
<section class="related-posts" style="margin:2.5rem 0;padding:1.5rem 2rem;background:linear-gradient(135deg,#f0f4ff,#e8f5e9);border-radius:12px;border-left:4px solid #1a73e8">
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

# ── FIX 6: BROKEN LINKS ──────────────────────────────
def find_and_fix_broken_links(html, all_urls, filepath):
    """Find broken internal links and fix or flag them."""
    changes = 0
    broken = []
    
    # Find all internal links
    links = re.findall(r'href=["\'](' + re.escape(SITE_URL) + r'[^"\']+)["\']', html)
    links += re.findall(r'href=["\'](/[^"\']+)["\']', html)
    
    for link in links:
        full = link if link.startswith("http") else SITE_URL + link
        # Check if it exists in our file list
        rel_path = full.replace(SITE_URL + "/", "").replace(SITE_URL, "")
        local = os.path.join(REPO_ROOT, rel_path.lstrip("/"))
        
        if not os.path.exists(local) and not rel_path.endswith(("/", "")):
            # Try common fixes
            fixed = None
            # Fix space in URL
            if "%20" in link or " " in link:
                fixed = link.replace(" ", "-").replace("%20", "-")
                html = html.replace(f'href="{link}"', f'href="{fixed}"')
                html = html.replace(f"href='{link}'", f"href='{fixed}'")
                changes += 1
            else:
                broken.append(full)
    
    return html, changes, broken

# ── FIX 7: SORT BLOG CARDS BY DATE ───────────────────
def sort_blog_cards_by_date(html, filepath):
    """Sort blog.html cards newest first."""
    if "blog.html" not in filepath and "blog/index" not in filepath:
        return html, 0
    
    # Find the blog cards container
    # Cards are typically in a grid/list — find individual card blocks
    # Pattern: each card starts with <a href="...blog/..." and ends with </a>
    
    card_pattern = r'(<a\s+href=["\']https://aivoraai\.github\.io/blog/[^"\']+["\'][^>]*>.*?</a>)'
    cards = re.findall(card_pattern, html, re.DOTALL)
    
    if len(cards) < 3:
        return html, 0
    
    def extract_date_from_card(card):
        # Try ISO date
        m = re.search(r'(\d{4}-\d{2}-\d{2})', card)
        if m:
            try: return datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except: pass
        # Try "Apr 2026", "Jun 2026"
        m = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', card)
        if m:
            try: return date(int(m.group(3)), MONTH_MAP.get(m.group(2),1), int(m.group(1)))
            except: pass
        m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', card)
        if m:
            try: return date(int(m.group(2)), MONTH_MAP.get(m.group(1),1), 1)
            except: pass
        return date(2000,1,1)
    
    dated_cards = [(extract_date_from_card(c), c) for c in cards]
    sorted_cards = sorted(dated_cards, key=lambda x: x[0], reverse=True)
    
    # Check if already sorted
    if dated_cards == sorted_cards:
        return html, 0
    
    # Replace cards in HTML in sorted order
    new_html = html
    positions = []
    search_html = html
    offset = 0
    for card in cards:
        idx = search_html.find(card)
        if idx >= 0:
            positions.append(idx + offset)
            offset += idx + len(card)
            search_html = search_html[idx + len(card):]
    
    if len(positions) == len(cards):
        # Rebuild HTML with sorted cards
        result = list(html)
        for i, (pos, old_card) in enumerate(zip(positions, cards)):
            new_card = sorted_cards[i][1]
            # Simple replacement approach
        
        # Rebuild using split approach
        parts = re.split(card_pattern, html, flags=re.DOTALL)
        new_parts = []
        card_idx = 0
        for part in parts:
            if re.match(card_pattern, part, re.DOTALL):
                new_parts.append(sorted_cards[card_idx][1])
                card_idx += 1
            else:
                new_parts.append(part)
        
        new_html = "".join(new_parts)
        return new_html, 1
    
    return html, 0

# ── FIX 8: SITEMAP ───────────────────────────────────
def gen_sitemap(posts, all_files):
    entries = []
    seen = set()
    
    # Blog posts first (sorted by date, newest first)
    for p in posts:
        url = p["url"]
        if url in seen: continue
        seen.add(url)
        d = p["date_str"] or TODAY
        # Don't include future-dated posts
        if p["date"] and p["date"] > MAX_DATE:
            d = TODAY
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{d}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
    
    # Other pages
    for f in all_files:
        url = to_url(f)
        if url in seen or BLOG_DIR in f: continue
        seen.add(url)
        pri = "1.0" if "index.html" in f else "0.6"
        freq = "daily" if "index.html" in f else "monthly"
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""")
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(entries)}
</urlset>
"""
    write(os.path.join(REPO_ROOT, "sitemap.xml"), xml)
    return len(entries)

# ── FIX 9: ROBOTS ────────────────────────────────────
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
def save_report(stats, broken_links):
    broken_text = "\n".join(f"  ❌ {b}" for b in broken_links[:30]) if broken_links else "  ✅ None found!"
    
    report = f"""
╔══════════════════════════════════════════════════╗
║      AIVORA AI — SEO MEGA FIX REPORT v2.0       ║
║      Generated: {TODAY}                    ║
╚══════════════════════════════════════════════════╝

FILES PROCESSED:         {stats['files']}
DATES FIXED:             {stats['dates']}
CANONICALS FIXED:        {stats['canon']}
META DESCS ADDED:        {stats['meta']}
INTERNAL LINKS ADDED:    {stats['links']}
ANCHOR LINKS ADDED:      {stats['anchors']}
BROKEN LINKS FIXED:      {stats['broken_fixed']}
BLOG CARDS SORTED:       {stats['sorted']} pages
SITEMAP URLs:            {stats['sitemap']}

BROKEN LINKS FOUND (manual fix needed):
{broken_text}

══════════════════════════════════════════════════
  NEXT STEPS — DO THIS NOW!
══════════════════════════════════════════════════

1. git add .
2. git commit -m "🤖 SEO Mega Fix v2: dates, links, sitemap, sort — {TODAY}"
3. git push

4. GOOGLE SEARCH CONSOLE:
   a) Sitemaps → Submit: {SITE_URL}/sitemap.xml
   b) URL Inspection → Request Indexing:
      {SITE_URL}/
      {SITE_URL}/blog.html
      {SITE_URL}/blog/gpt-creator-club-review-2026.html
      {SITE_URL}/blog/ai-passive-income-tools-2026.html
      {SITE_URL}/blog/ai-affiliate-marketing-guide-2026.html
      {SITE_URL}/blog/sam-altman-ai-predictions-2026.html
      {SITE_URL}/blog/vip-indicators-review-2026.html

5. Wait 48–72 hours → check GSC for indexing

WHY NOT INDEXED YET?
══════════════════════════════════════════════════
• Future dates were telling Google "not published yet"
• This script fixes all future dates → Google can now index
• After git push + sitemap submit → 48–72 hours
• Impressions visible in GSC → 2–3 weeks

INDEXING TIMELINE:
• Homepage:     24–48 hours after Request Indexing
• Blog posts:   3–7 days after sitemap submit
• Impressions:  2–4 weeks in GSC Performance report
"""
    write(os.path.join(REPO_ROOT, "seo_report.txt"), report)
    return report

# ── MAIN ─────────────────────────────────────────────
def main():
    print("\n" + "="*52)
    print("  AIVORA AI SEO MEGA FIX v2.0")
    print(f"  Date: {TODAY} | Site: {SITE_URL}")
    print("="*52 + "\n")

    all_files = find_html()
    if not all_files:
        print("❌ No HTML files found! Run from repo root folder.")
        print(f"   Current dir: {os.path.abspath('.')}")
        return

    print(f"📁 Found {len(all_files)} HTML files")
    print("🗄️  Building post database...")
    posts = build_post_db(all_files)
    print(f"   → {len(posts)} blog posts indexed")
    all_urls = set(to_url(f) for f in all_files)

    stats = {
        "files":0,"dates":0,"canon":0,"meta":0,
        "links":0,"anchors":0,"broken_fixed":0,"sorted":0,"sitemap":0
    }
    all_broken = []

    print("\n🔧 Processing HTML files...\n")

    for fp in all_files:
        html = read(fp)
        orig = html
        log = []
        stats["files"] += 1
        
        # Get post data for this file
        post_data = next((p for p in posts if p["file"]==fp), None)

        html, n = fix_dates(html)
        if n: log.append(f"dates:{n}"); stats["dates"]+=1

        html, n = fix_canonical(html, fp)
        if n: log.append(f"canon:{n}"); stats["canon"]+=1

        html, n = fix_meta_desc(html, fp)
        if n: log.append("meta"); stats["meta"]+=1

        html, n, broken = find_and_fix_broken_links(html, all_urls, fp)
        if n: log.append(f"broken_fixed:{n}"); stats["broken_fixed"]+=n
        all_broken.extend(broken)

        if post_data:
            html, n = add_anchor_internal_links(html, post_data, posts)
            if n: log.append(f"links:{n}"); stats["links"]+=1; stats["anchors"]+=n

        html, n = sort_blog_cards_by_date(html, fp)
        if n: log.append("sorted"); stats["sorted"]+=1

        if html != orig:
            backup(fp)
            write(fp, html)
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"  ✅ {rel:<58} [{', '.join(log)}]")
        else:
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"     {rel}")

    print(f"\n🗺️  Generating sitemap.xml...")
    stats["sitemap"] = gen_sitemap(posts, all_files)
    print(f"  ✅ {stats['sitemap']} URLs")

    print(f"🤖 Generating robots.txt...")
    gen_robots()
    print(f"  ✅ Done")

    print(f"\n📊 Saving report → seo_report.txt")
    report = save_report(stats, list(set(all_broken)))

    print("\n" + "="*52)
    print("  ✅ ALL DONE!")
    print("="*52)
    print(f"\n  Dates fixed:          {stats['dates']}")
    print(f"  Internal links added: {stats['links']} posts")
    print(f"  Anchor links added:   {stats['anchors']} total")
    print(f"  Blog cards sorted:    {stats['sorted']} pages")
    print(f"  Broken links found:   {len(set(all_broken))}")
    print(f"  Sitemap URLs:         {stats['sitemap']}")
    print(f"\n  Ab yeh run karo:")
    print(f"  git add .")
    print(f'  git commit -m "SEO Mega Fix {TODAY}"')
    print(f"  git push\n")

if __name__ == "__main__":
    main()

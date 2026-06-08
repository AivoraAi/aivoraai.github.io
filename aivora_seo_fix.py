#!/usr/bin/env python3
"""
====================================================
  AIVORA AI — SEO AUTO-FIX SCRIPT
  Site: https://aivoraai.github.io
  By: Claude for Varun Lalwani
====================================================
  YEH SCRIPT AUTOMATICALLY FIX KARTA HAI:
  [1] Future dates → aaj ki date se replace
  [2] Canonical /index.html → / fix
  [3] og:url mismatch fix
  [4] Internal links — Related Posts add
  [5] Missing meta description add
  [6] sitemap.xml generate — sab URLs
  [7] robots.txt optimize
====================================================
"""

import os, re, glob, shutil
from datetime import date, datetime
from pathlib import Path
from collections import defaultdict

# ── CONFIG ───────────────────────────────────────────
SITE_URL  = "https://aivoraai.github.io"
REPO_ROOT = "."
BLOG_DIR  = "blog"
TODAY     = date.today().strftime("%Y-%m-%d")
TODAY_ISO = date.today().strftime("%Y-%m-%dT00:00:00Z")
TODAY_DT  = datetime.today()
MAX_DATE  = date.today()
AUTHOR    = "Varun Lalwani"

TOPIC_CLUSTERS = {
    "affiliate": ["affiliate","commission","earn","income","passive"],
    "chatgpt":   ["chatgpt","gpt","openai","prompt"],
    "video":     ["video","youtube","faceless","shorts","reels","tiktok"],
    "seo":       ["seo","keyword","rank","google","backlink","serp"],
    "tools":     ["tools","best","top","review","compared","vs"],
    "beginner":  ["beginner","start","zero","no-experience","beginners"],
    "india":     ["india","rupee","dollars","online-income"],
    "blogging":  ["blog","blogging","content","writing","post"],
    "social":    ["instagram","social","media","followers","viral"],
    "business":  ["business","agency","startup","entrepreneur","freelance"],
}

# ── HELPERS ──────────────────────────────────────────

def find_html(root=REPO_ROOT):
    files = []
    for pat in ["*.html", f"{BLOG_DIR}/*.html", f"{BLOG_DIR}/**/*.html"]:
        files.extend(glob.glob(os.path.join(root, pat), recursive=True))
    # Exclude backup folder
    files = [f for f in files if "_seo_backups" not in f]
    return sorted(set(files))

def read(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def to_url(filepath):
    rel = os.path.relpath(filepath, REPO_ROOT).replace("\\", "/")
    if rel in ("index.html",):
        return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"

def backup(filepath):
    bdir = os.path.join(REPO_ROOT, "_seo_backups")
    os.makedirs(bdir, exist_ok=True)
    rel = os.path.relpath(filepath, REPO_ROOT).replace("/","_").replace("\\","_")
    shutil.copy2(filepath, os.path.join(bdir, rel))

# ── FIX 1: FUTURE DATES ──────────────────────────────

MONTH_MAP = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
             "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

def is_future(year, month=1, day=1):
    try:
        return date(int(year), int(month), int(day)) > MAX_DATE
    except:
        return False

def fix_dates(html):
    changes = 0

    # ISO meta dates: 2026-09-01T...
    def fix_iso(m):
        nonlocal changes
        ds = m.group(2)[:10]
        try:
            y,mo,d = ds.split("-")
            if is_future(y, mo, d):
                changes += 1
                return m.group(1) + TODAY_ISO + m.group(3)
        except: pass
        return m.group(0)

    html = re.sub(
        r'(content=["\'])(\d{4}-\d{2}-\d{2}T[^"\']*?)(["\'])',
        fix_iso, html)

    # Visible dates: "15 Jul 2026", "10 Sep 2026"
    def fix_visible(m):
        nonlocal changes
        d, mon, y = m.group(1), m.group(2), m.group(3)
        if is_future(y, MONTH_MAP.get(mon,1), d):
            changes += 1
            return TODAY_DT.strftime("%-d %b %Y") if os.name!='nt' else f"{TODAY_DT.day} {TODAY_DT.strftime('%b %Y')}"
        return m.group(0)

    html = re.sub(
        r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(202[6-9]|20[3-9]\d)\b',
        fix_visible, html)

    # Month year only: "Sep 2026", "Jul 2027"
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

    # Date in content attribute: content="2026-09-10"
    def fix_content_date(m):
        nonlocal changes
        ds = m.group(2)
        try:
            y,mo,d = ds.split("-")
            if is_future(y,mo,d):
                changes += 1
                return m.group(1) + TODAY + m.group(3)
        except: pass
        return m.group(0)

    html = re.sub(
        r'(content=["\'])(\d{4}-\d{2}-\d{2})(["\'])',
        fix_content_date, html)

    return html, changes

# ── FIX 2: CANONICAL ─────────────────────────────────

def fix_canonical(html, filepath):
    changes = 0
    correct = to_url(filepath)

    def fix_tag(m):
        nonlocal changes
        url = m.group(1)
        fixed = url.replace("/index.html", "/")
        if fixed != url:
            changes += 1
        return m.group(0).replace(url, fixed)

    # <link rel="canonical" href="...">
    html = re.sub(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
                  fix_tag, html)
    html = re.sub(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',
                  fix_tag, html)

    # og:url
    def fix_og(m):
        nonlocal changes
        url = m.group(2)
        fixed = url.replace("/index.html", "/")
        if fixed != url:
            changes += 1
        return m.group(1) + fixed + m.group(3)

    html = re.sub(
        r'(property=["\']og:url["\'][^>]+content=["\'])([^"\']+)(["\'])',
        fix_og, html)
    html = re.sub(
        r'(content=["\'])([^"\']+)(["\'][^>]+property=["\']og:url["\'])',
        fix_og, html)

    return html, changes

# ── FIX 3: META DESCRIPTION ──────────────────────────

def fix_meta_desc(html, filepath):
    changes = 0
    has = re.search(r'name=["\']description["\'][^>]+content=["\'][^"\']{20,}', html)
    if not has:
        tm = re.search(r'<title>([^<]+)</title>', html)
        if tm:
            t = tm.group(1).split("|")[0].strip()
            desc = f"Discover {t} — Aivora AI's honest review and guide for 2026. Tested by {AUTHOR}. Best AI tools for income, affiliate marketing & more."
            desc = desc[:160]
            tag = f'\n  <meta name="description" content="{desc}">'
            html = html.replace("</head>", tag + "\n</head>", 1)
            changes += 1
    return html, changes

# ── FIX 4: INTERNAL LINKS ────────────────────────────

def build_link_map(all_files):
    lmap = defaultdict(list)
    for f in all_files:
        if BLOG_DIR not in f:
            continue
        html = read(f)
        tm = re.search(r'<title>([^<]+)</title>', html)
        if not tm:
            continue
        title = tm.group(1).split("|")[0].strip()
        url = to_url(f)
        fname = os.path.basename(f).lower()
        for topic, kws in TOPIC_CLUSTERS.items():
            if any(k in fname for k in kws):
                lmap[topic].append((url, title, f))
    return lmap

def add_internal_links(html, filepath, lmap):
    changes = 0
    if BLOG_DIR not in filepath:
        return html, changes
    if "related-posts" in html or "Related Posts" in html or "You might also like" in html:
        return html, changes

    fname = os.path.basename(filepath).lower()
    cur_url = to_url(filepath)
    related = []

    for topic, kws in TOPIC_CLUSTERS.items():
        if any(k in fname for k in kws):
            for url, title, fpath in lmap.get(topic, []):
                if url != cur_url and (url, title) not in related and len(related) < 5:
                    related.append((url, title))

    if len(related) < 2:
        return html, changes

    items = "\n".join(
        f'      <li style="margin:6px 0"><a href="{u}" style="color:#1a73e8;text-decoration:none;font-size:14px">{t}</a></li>'
        for u, t in related[:4]
    )

    section = f"""
<section class="related-posts" style="margin:2.5rem 0;padding:1.5rem;background:#f0f4ff;border-radius:10px;border-left:4px solid #1a73e8">
  <h3 style="margin:0 0 .75rem;font-size:1rem;color:#1a0a2e;font-weight:600">You Might Also Like</h3>
  <ul style="margin:0;padding-left:1.25rem;line-height:1.8">
{items}
  </ul>
</section>
"""
    for tag in ["</article>", "</main>", "<footer", "</body>"]:
        if tag in html:
            html = html.replace(tag, section + "\n" + tag, 1)
            changes += 1
            break

    return html, changes

# ── FIX 5: SITEMAP ───────────────────────────────────

def gen_sitemap(all_files):
    entries = []
    for f in sorted(all_files):
        url = to_url(f)
        if BLOG_DIR in f:
            pri, freq = "0.8", "weekly"
        elif f.endswith("index.html"):
            pri, freq = "1.0", "daily"
        else:
            pri, freq = "0.6", "monthly"

        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(entries)}
</urlset>
"""
    path = os.path.join(REPO_ROOT, "sitemap.xml")
    write(path, xml)
    return len(entries)

# ── FIX 6: ROBOTS.TXT ────────────────────────────────

def gen_robots():
    content = f"""# robots.txt — Aivora AI
# {SITE_URL}
# Auto-generated: {TODAY}

User-agent: *
Allow: /
Disallow: /assets/private/
Disallow: /tmp/
Disallow: /drafts/
Disallow: /_seo_backups/

User-agent: Googlebot
Allow: /
Disallow: /assets/private/

User-agent: GPTBot
Allow: /blog/
Allow: /about.html
Allow: /contact.html
Disallow: /assets/private/

User-agent: Google-Extended
Allow: /blog/
Allow: /about.html

User-agent: ClaudeBot
Allow: /blog/

User-agent: anthropic-ai
Allow: /blog/

User-agent: CCBot
Disallow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    write(os.path.join(REPO_ROOT, "robots.txt"), content)

# ── REPORT ───────────────────────────────────────────

def save_report(stats):
    r = f"""AIVORA AI — SEO AUTO-FIX REPORT
Generated: {TODAY}
{"="*45}

Files processed:       {stats['files']}
Dates fixed:           {stats['dates']}
Canonicals fixed:      {stats['canon']}
Meta descs added:      {stats['meta']}
Internal links added:  {stats['links']}
Sitemap URLs:          {stats['sitemap']}

NEXT STEPS:
{"─"*45}
1. git add .
2. git commit -m "SEO auto-fix {TODAY}"
3. git push

4. Google Search Console:
   → Sitemaps: {SITE_URL}/sitemap.xml
   → URL Inspection → Request Indexing:
     {SITE_URL}/
     {SITE_URL}/blog.html
     {SITE_URL}/blog/gpt-creator-club-review-2026.html
"""
    write(os.path.join(REPO_ROOT, "seo_report.txt"), r)
    print(r)

# ── MAIN ─────────────────────────────────────────────

def main():
    print("=" * 50)
    print("  AIVORA AI SEO AUTO-FIX")
    print(f"  Date: {TODAY}")
    print("=" * 50)

    all_files = find_html()
    print(f"\n📁 Found {len(all_files)} HTML files\n")

    if not all_files:
        print("❌ No HTML files found!")
        print(f"   Run from repo root. Current dir: {os.path.abspath('.')}")
        return

    # Build internal link map
    print("🔗 Building internal link map...")
    lmap = build_link_map(all_files)

    stats = {"files": len(all_files), "dates": 0, "canon": 0,
             "meta": 0, "links": 0, "sitemap": 0}

    print("🔧 Fixing HTML files...\n")

    for fp in all_files:
        html = read(fp)
        orig = html
        log = []

        html, n = fix_dates(html);             n and log.append(f"dates:{n}")   or None; stats["dates"] += (1 if n else 0)
        html, n = fix_canonical(html, fp);     n and log.append(f"canon:{n}")   or None; stats["canon"] += (1 if n else 0)
        html, n = fix_meta_desc(html, fp);     n and log.append("meta")         or None; stats["meta"]  += (1 if n else 0)
        html, n = add_internal_links(html, fp, lmap); n and log.append("links") or None; stats["links"] += (1 if n else 0)

        if html != orig:
            backup(fp)
            write(fp, html)
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"  ✅ {rel:<55} [{', '.join(log)}]")

    print(f"\n🗺️  Generating sitemap.xml...")
    stats["sitemap"] = gen_sitemap(all_files)
    print(f"  ✅ {stats['sitemap']} URLs added")

    print(f"\n🤖 Generating robots.txt...")
    gen_robots()
    print(f"  ✅ Done")

    print(f"\n📄 Saving report...")
    save_report(stats)

    print("\n" + "=" * 50)
    print("  ALL DONE! ✅")
    print("=" * 50)
    print("\n  Ab yeh run karo:")
    print("  git add .")
    print(f'  git commit -m "SEO auto-fix {TODAY}"')
    print("  git push\n")

if __name__ == "__main__":
    main()

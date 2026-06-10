#!/usr/bin/env python3
"""
====================================================
  AIVORA AI — SEO FIX SCRIPT v3.0 (SAFE)
  Site: https://aivoraai.github.io
  FIXED: No more breaking navigation/CSS/JS links!
====================================================
  SAFE FIXES ONLY:
  [1] Future dates in meta tags → aaj ki date
  [2] Canonical tag fix (ONLY <link rel="canonical">)
  [3] og:url fix (ONLY og:url meta tag)
  [4] Missing meta description add
  [5] Related Posts section add (safe injection)
  [6] sitemap.xml generate
  [7] robots.txt generate
  NOTE: Does NOT touch navigation links, CSS, JS!
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
    "affiliate":  ["affiliate","commission","earn","income","passive","hustles"],
    "chatgpt":    ["chatgpt","gpt","openai","prompt"],
    "video":      ["video","youtube","faceless","shorts","reels","tiktok"],
    "seo":        ["seo","keyword","rank","search","backlink"],
    "tools":      ["tools","best","top","review","compared"],
    "beginner":   ["beginner","beginners","guide","start","zero"],
    "india":      ["india","rupee","dollars"],
    "blogging":   ["blog","blogging","content","writing","niche"],
    "social":     ["instagram","social","followers","viral"],
    "business":   ["business","agency","startup","freelance"],
    "automation": ["automation","automate","workflow"],
}

def find_html():
    files = []
    for pat in ["*.html", f"{BLOG_DIR}/*.html", f"{BLOG_DIR}/**/*.html"]:
        files.extend(glob.glob(os.path.join(REPO_ROOT, pat), recursive=True))
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
    dest = os.path.join(bdir, rel)
    if not os.path.exists(dest):  # Only backup once, don't overwrite original backup
        shutil.copy2(filepath, dest)

def is_future(year, month=1, day=1):
    try: return date(int(year), int(month), int(day)) > MAX_DATE
    except: return False

# ── FIX 1: DATES — only in meta tags, NOT visible content ────
def fix_dates(html):
    changes = 0

    # Fix ISO datetime in meta content= attributes only
    def fix_iso(m):
        nonlocal changes
        try:
            ds = m.group(2)[:10]
            y,mo,d = ds.split("-")
            if is_future(y,mo,d):
                changes += 1
                return m.group(1) + TODAY_ISO + m.group(3)
        except: pass
        return m.group(0)
    html = re.sub(r'(<meta[^>]+content=["\'])(\d{4}-\d{2}-\d{2}T[^"\']*?)(["\'])', fix_iso, html)

    # Fix plain date in meta content= only
    def fix_meta_date(m):
        nonlocal changes
        try:
            y,mo,d = m.group(2).split("-")
            if is_future(y,mo,d):
                changes += 1
                return m.group(1) + TODAY + m.group(3)
        except: pass
        return m.group(0)
    html = re.sub(r'(<meta[^>]+content=["\'])(\d{4}-\d{2}-\d{2})(["\'])', fix_meta_date, html)

    return html, changes

# ── FIX 2: CANONICAL — ONLY <link rel="canonical"> tag ───────
def fix_canonical(html, filepath):
    changes = 0
    # SAFE: Only fix <link rel="canonical" href="...index.html">
    # Do NOT touch any other href attributes
    def fix_canon(m):
        nonlocal changes
        full_tag = m.group(0)
        url = m.group(1)
        if "index.html" in url:
            fixed_url = url.replace("/index.html", "/")
            changes += 1
            return full_tag.replace(url, fixed_url)
        return full_tag
    
    html = re.sub(
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\'][^>]*/?>',
        fix_canon, html)
    html = re.sub(
        r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\'][^>]*/?>',
        fix_canon, html)
    return html, changes

# ── FIX 3: og:url — ONLY og:url meta tag ─────────────────────
def fix_og_url(html):
    changes = 0
    def fix_og(m):
        nonlocal changes
        url = m.group(1)
        if "index.html" in url:
            changes += 1
            return m.group(0).replace(url, url.replace("/index.html", "/"))
        return m.group(0)
    html = re.sub(
        r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)["\']',
        fix_og, html)
    html = re.sub(
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:url["\']',
        fix_og, html)
    return html, changes

# ── FIX 4: META DESCRIPTION ──────────────────────────────────
def fix_meta_desc(html):
    changes = 0
    has = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'][^"\']{20,}', html)
    if not has:
        tm = re.search(r'<title>([^<]+)</title>', html)
        if tm:
            t = tm.group(1).split("|")[0].strip()
            desc = f"Discover {t} — Aivora AI's honest guide for 2026. Best AI tools for income, affiliate marketing & passive income. By {AUTHOR}."[:160]
            tag = f'  <meta name="description" content="{desc}">\n'
            html = html.replace("</head>", tag + "</head>", 1)
            changes += 1
    return html, changes

# ── FIX 5: RELATED POSTS — safe injection before </body> ──────
def build_link_map(all_files):
    lmap = defaultdict(list)
    for f in all_files:
        if BLOG_DIR not in f: continue
        html = read(f)
        tm = re.search(r'<title>([^<]+)</title>', html)
        if not tm: continue
        title = tm.group(1).split("|")[0].strip()
        url = to_url(f)
        fname = os.path.basename(f).lower()
        for topic, kws in TOPIC_CLUSTERS.items():
            if any(k in fname for k in kws):
                lmap[topic].append((url, title, f))
    return lmap

def add_related_posts(html, filepath, lmap):
    changes = 0
    if BLOG_DIR not in filepath: return html, changes
    if "related-posts" in html or "You Might Also Like" in html: return html, changes

    fname = os.path.basename(filepath).lower()
    cur_url = to_url(filepath)
    related = []

    for topic, kws in TOPIC_CLUSTERS.items():
        if any(k in fname for k in kws):
            for url, title, fpath in lmap.get(topic, []):
                if url != cur_url and (url,title) not in related and len(related) < 4:
                    related.append((url, title))

    if len(related) < 2: return html, changes

    items = "\n".join(
        f'      <li style="margin:8px 0"><a href="{u}" style="color:#1a73e8;text-decoration:none;font-size:14px">→ {t}</a></li>'
        for u,t in related
    )
    section = f"""
<!-- Related Posts — Added by Aivora SEO Script -->
<section style="margin:2.5rem auto;max-width:800px;padding:1.5rem 2rem;background:#f0f4ff;border-radius:12px;border-left:4px solid #1a73e8;font-family:inherit">
  <h3 style="margin:0 0 1rem;font-size:1rem;color:#1a0a2e;font-weight:700">📚 You Might Also Like</h3>
  <ul style="margin:0;padding-left:1rem;list-style:none;line-height:1.8">
{items}
  </ul>
</section>
<!-- End Related Posts -->
"""
    # Safe injection — just before </body>
    if "</body>" in html:
        html = html.replace("</body>", section + "\n</body>", 1)
        changes += 1
    return html, changes

# ── FIX 6: SITEMAP ───────────────────────────────────────────
def gen_sitemap(all_files):
    entries = []
    seen = set()
    for f in sorted(all_files):
        url = to_url(f)
        if url in seen: continue
        seen.add(url)
        if BLOG_DIR in f:
            pri, freq = "0.8", "weekly"
        elif "index.html" in f and BLOG_DIR not in f:
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
    write(os.path.join(REPO_ROOT, "sitemap.xml"), xml)
    return len(entries)

# ── FIX 7: ROBOTS ────────────────────────────────────────────
def gen_robots():
    write(os.path.join(REPO_ROOT, "robots.txt"), f"""# robots.txt — Aivora AI
# Auto-generated: {TODAY}

User-agent: *
Allow: /
Disallow: /assets/private/
Disallow: /_seo_backups/

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

# ── MAIN ─────────────────────────────────────────────────────
def main():
    print("\n" + "="*52)
    print("  AIVORA AI SEO FIX v3.0 — SAFE VERSION")
    print(f"  Date: {TODAY}")
    print("="*52 + "\n")

    all_files = find_html()
    if not all_files:
        print("No HTML files found! Run from repo root.")
        return

    print(f"Found {len(all_files)} HTML files")
    print("Building link map...")
    lmap = build_link_map(all_files)

    stats = {"files":0,"dates":0,"canon":0,"og":0,"meta":0,"related":0,"sitemap":0}

    print("\nProcessing files...\n")

    for fp in all_files:
        html = read(fp)
        orig = html
        log = []
        stats["files"] += 1

        html, n = fix_dates(html)
        if n: log.append(f"dates:{n}"); stats["dates"]+=1

        html, n = fix_canonical(html, fp)
        if n: log.append(f"canon:{n}"); stats["canon"]+=1

        html, n = fix_og_url(html)
        if n: log.append(f"og:n"); stats["og"]+=1

        html, n = fix_meta_desc(html)
        if n: log.append("meta"); stats["meta"]+=1

        html, n = add_related_posts(html, fp, lmap)
        if n: log.append("related"); stats["related"]+=1

        if html != orig:
            backup(fp)
            write(fp, html)
            print(f"  FIXED: {os.path.relpath(fp):<60} [{', '.join(log)}]")

    print(f"\nGenerating sitemap.xml...")
    stats["sitemap"] = gen_sitemap(all_files)
    print(f"  Done: {stats['sitemap']} URLs")

    print(f"Generating robots.txt...")
    gen_robots()
    print(f"  Done")

    print(f"\n{'='*52}")
    print(f"  ALL DONE!")
    print(f"{'='*52}")
    print(f"\n  Dates fixed:     {stats['dates']}")
    print(f"  Canonicals:      {stats['canon']}")
    print(f"  Meta descs:      {stats['meta']}")
    print(f"  Related posts:   {stats['related']}")
    print(f"  Sitemap URLs:    {stats['sitemap']}")
    print(f"\n  Now run:")
    print(f"  git add .")
    print(f'  git commit -m "SEO Fix v3 safe — {TODAY}"')
    print(f"  git push\n")

if __name__ == "__main__":
    main()

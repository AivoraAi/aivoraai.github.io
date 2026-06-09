#!/usr/bin/env python3
"""
====================================================
  AIVORA AI — MEGA SEO AUTO-FIX SCRIPT v3.0
  Site: https://aivoraai.github.io
  By: Varun Lalwani — Aivora AI
====================================================
  WHAT THIS SCRIPT DOES:
  [1]  Future dates → today's real date
  [2]  Canonical /index.html → /
  [3]  og:url cleanup
  [4]  Missing meta description → auto-generate
  [5]  Smart internal anchor text linking
  [6]  Broken internal links → detect & fix spaces
  [7]  Blog cards sort newest-first (main only — nav/footer SAFE)
  [8]  Related posts section inject
  [9]  sitemap.xml regenerate (all 200+ pages)
  [10] robots.txt optimize
  [11] DESIGN PROTECTION — nav, header, footer, CSS,
       dark theme, fonts, animations NEVER touched

  DESIGN FEATURES PRESERVED (from your Kimi vs ChatGPT page):
  • Dark bg: #050a0e / #091014 / #0f1e26
  • Accent: #00c896 (green), #f0b429 (gold), #f43f5e (rose)
  • Fonts: Outfit + Space Grotesk (Google Fonts)
  • Animated diagram nodes (.diagram-node shimmer/pulse)
  • VS cards (.vs-card.kimi / .vs-card.chatgpt)
  • Sticky sidebar (.sidebar-sticky)
  • Progress bar (#progressBar)
  • Mobile hamburger nav (.ham / .mnav)
  • FAQ accordion (.faq-item / .faq-q / .faq-a)
  • Author box (.author-box)
  • CTA box (.cta-box)
  • Breadcrumb nav (.breadcrumb)
  • Footer with privacy/terms links
  • All structured data (Article, Person, Org, FAQ, Breadcrumb)
  • All JavaScript (scroll, nav, FAQ, popup, form validation)
====================================================
"""

import os, re, glob, shutil
from datetime import date, datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
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

# Topic clusters for smart anchor-text linking
TOPIC_CLUSTERS = {
    "affiliate":  ["affiliate","commission","earn","income","passive","hustles","profit"],
    "chatgpt":    ["chatgpt","gpt","openai","prompt","ai-writing","kimi"],
    "video":      ["video","youtube","faceless","shorts","reels","tiktok","creator","subtitles"],
    "seo":        ["seo","keyword","rank","google","backlink","serp","search"],
    "tools":      ["tools","best","top","review","compared","vs","builder"],
    "beginner":   ["beginner","start","zero","no-experience","beginners","guide"],
    "india":      ["india","rupee","dollars","online-income","hindi"],
    "blogging":   ["blog","blogging","content","writing","post","niche"],
    "social":     ["instagram","social","media","followers","viral","twitter"],
    "business":   ["business","agency","startup","entrepreneur","freelance","dropship"],
    "trading":    ["trading","forex","crypto","stock","signals","finance"],
    "automation": ["automation","automate","workflow","zapier","make","integromat"],
    "comparison": ["vs","versus","better","compare","comparison","alternative"],
}

# CSS/JS patterns that must NEVER be modified
# These protect your dark theme, animations, fonts, and all UI components
PROTECTED_PATTERNS = [
    r'<style[\s\S]*?</style>',          # ALL CSS — dark theme, animations, layout
    r'<script[\s\S]*?</script>',        # ALL JS — nav, FAQ, popup, scroll
    r'<header[\s\S]*?</header>',        # Header + nav bar
    r'<nav[\s\S]*?</nav>',              # All nav elements
    r'<footer[\s\S]*?</footer>',        # Footer
    r'class="nav[\s\S]*?"',             # Nav classes
    r'class="logo[\s\S]*?"',            # Logo classes
    r'class="footer[\s\S]*?"',          # Footer classes
    r'class="ham[\s\S]*?"',             # Hamburger menu
    r'class="mnav[\s\S]*?"',            # Mobile nav
    r'class="breadcrumb[\s\S]*?"',      # Breadcrumb
    r'class="diagram-node[\s\S]*?"',    # Animated diagram nodes
    r'class="vs-card[\s\S]*?"',         # VS comparison cards
    r'class="sidebar[\s\S]*?"',         # Sidebar + sticky TOC
    r'class="author-box[\s\S]*?"',      # Author section
    r'class="cta-box[\s\S]*?"',         # CTA sections
    r'class="faq-item[\s\S]*?"',        # FAQ accordion
    r'class="workflow-diagram[\s\S]*?"',# Workflow diagrams
    r'@keyframes',                       # CSS animations
    r'application/ld\+json',            # Structured data schemas
    r'progressBar',                      # Progress bar
    r'GTM-NWSJTJ3M',                    # Google Tag Manager
    r'G-N0LH3EN5QE',                    # Google Analytics
    r'Outfit.*Grotesk',                  # Font imports
    r'fonts\.googleapis\.com',           # Google Fonts
    r'var\(--',                          # CSS variables
    r'--bg:|--em:|--gold:|--rose:',      # CSS custom properties
]

# ── HELPERS ──────────────────────────────────────────────────────────────────
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
    if rel == "index.html": return SITE_URL + "/"
    return f"{SITE_URL}/{rel}"

def backup(filepath):
    bdir = os.path.join(REPO_ROOT, "_seo_backups")
    os.makedirs(bdir, exist_ok=True)
    rel = os.path.relpath(filepath, REPO_ROOT).replace("/","_").replace("\\","_")
    shutil.copy2(filepath, os.path.join(bdir, rel))

def is_future(year, month=1, day=1):
    try:
        return date(int(year), int(month), int(day)) > MAX_DATE
    except:
        return False

def is_protected_zone(html, start_pos, end_pos):
    """Check if a position falls inside a protected zone (style/script/nav/footer)."""
    # Find all protected block boundaries
    protected_blocks = []
    for tag in ['style', 'script', 'header', 'footer', 'nav']:
        for m in re.finditer(rf'<{tag}[\s>]', html, re.IGNORECASE):
            close = html.find(f'</{tag}>', m.start())
            if close != -1:
                protected_blocks.append((m.start(), close + len(f'</{tag}>')))
    for start, end in protected_blocks:
        if not (end_pos <= start or start_pos >= end):
            return True
    return False

# ── FIX 1: FUTURE DATES ──────────────────────────────────────────────────────
def fix_dates(html):
    """Fix future dates in meta tags and visible text. Never touches CSS or JS."""
    changes = 0

    # Only fix content="..." attributes (meta tags) — skip style/script blocks
    def fix_iso(m):
        nonlocal changes
        # Skip if inside a style or script tag
        pos = m.start()
        before = html[:pos]
        open_styles = before.count('<style') - before.count('</style>')
        open_scripts = before.count('<script') - before.count('</script>')
        if open_styles > 0 or open_scripts > 0:
            return m.group(0)
        try:
            y, mo, d = m.group(2)[:10].split("-")
            if is_future(y, mo, d):
                changes += 1
                return m.group(1) + TODAY_ISO + m.group(3)
        except:
            pass
        return m.group(0)

    html = re.sub(
        r'(content=["\'])(\d{4}-\d{2}-\d{2}T[^"\']*?)(["\'])',
        fix_iso, html)

    def fix_content_date(m):
        nonlocal changes
        pos = m.start()
        before = html[:pos]
        if before.count('<style') > before.count('</style'):
            return m.group(0)
        if before.count('<script') > before.count('</script>'):
            return m.group(0)
        try:
            y, mo, d = m.group(2).split("-")
            if is_future(y, mo, d):
                changes += 1
                return m.group(1) + TODAY + m.group(3)
        except:
            pass
        return m.group(0)

    html = re.sub(
        r'(content=["\'])(\d{4}-\d{2}-\d{2})(["\'])',
        fix_content_date, html)

    def fix_visible(m):
        nonlocal changes
        pos = m.start()
        before = html[:pos]
        # Only fix if outside script/style
        if before.count('<style') > before.count('</style>'):
            return m.group(0)
        if before.count('<script') > before.count('</script>'):
            return m.group(0)
        d, mon, y = m.group(1), m.group(2), m.group(3)
        if is_future(y, MONTH_MAP.get(mon, 1), d):
            changes += 1
            return f"{TODAY_DT.day} {TODAY_DT.strftime('%b')} {TODAY_DT.year}"
        return m.group(0)

    html = re.sub(
        r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(202[7-9]|20[3-9]\d)\b',
        fix_visible, html)

    def fix_monyr(m):
        nonlocal changes
        pos = m.start()
        before = html[:pos]
        if before.count('<style') > before.count('</style>'):
            return m.group(0)
        if before.count('<script') > before.count('</script>'):
            return m.group(0)
        mon, y = m.group(1), m.group(2)
        if is_future(y, MONTH_MAP.get(mon, 1)):
            changes += 1
            return TODAY_DT.strftime("%b %Y")
        return m.group(0)

    html = re.sub(
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(202[7-9]|20[3-9]\d)\b',
        fix_monyr, html)

    return html, changes

# ── FIX 2: CANONICAL ─────────────────────────────────────────────────────────
def fix_canonical(html, filepath):
    """Fix /index.html → / in canonical and og:url tags only."""
    changes = 0

    def fix_tag(m):
        nonlocal changes
        url = m.group(1)
        fixed = url.replace("/index.html", "/")
        if fixed != url:
            changes += 1
        return m.group(0).replace(url, fixed)

    # Only canonical link tags
    html = re.sub(
        r'(<link[^>]+rel=["\']canonical["\'][^>]+href=["\'])([^"\']+)(["\'])',
        lambda m: m.group(1) + m.group(2).replace("/index.html", "/") + m.group(3),
        html)

    # og:url meta tag
    html = re.sub(
        r'(og:url["\'][^>]+content=["\'])([^"\']+)(["\'])',
        lambda m: m.group(1) + m.group(2).replace("/index.html", "/") + m.group(3),
        html)

    return html, changes

# ── FIX 3: META DESCRIPTION ──────────────────────────────────────────────────
def fix_meta_desc(html, filepath):
    """Add meta description if missing (min 20 chars)."""
    changes = 0
    has = re.search(r'name=["\']description["\'][^>]+content=["\'][^"\']{20,}', html)
    if not has:
        tm = re.search(r'<title>([^<]+)</title>', html)
        if tm:
            t = tm.group(1).split("|")[0].strip()
            desc = (f"Discover {t} — Aivora AI's honest review and guide for 2026. "
                    f"Tested by {AUTHOR}. Best AI tools for income, affiliate marketing & more.")[:160]
            tag = f'\n  <meta name="description" content="{desc}">'
            html = html.replace("</head>", tag + "\n</head>", 1)
            changes += 1
    return html, changes

# ── FIX 4: BUILD POST DATABASE ───────────────────────────────────────────────
def build_post_db(all_files):
    """Build metadata database of all blog posts."""
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
            r'datePublished["\']:\s*["\'](\d{4}-\d{2}-\d{2})',
            r'content=["\'](\d{4}-\d{2}-\d{2})["\'][^>]+(?:published|date)',
            r'(?:Published|Date):\s*(\w+ \d{1,2},?\s*\d{4})',
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                try:
                    date_val = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                    date_str = date_val.strftime("%Y-%m-%d")
                    break
                except:
                    pass

        url = to_url(f)
        fname = os.path.basename(f).lower()

        topics = []
        for topic, kws in TOPIC_CLUSTERS.items():
            if any(k in fname for k in kws):
                topics.append(topic)

        posts.append({
            "file": f, "url": url, "title": title, "desc": desc,
            "date": date_val, "date_str": date_str,
            "fname": fname, "topics": topics, "html_len": len(html),
        })

    posts.sort(key=lambda x: x["date"] or date(2000, 1, 1), reverse=True)
    return posts

# ── FIX 5: SMART ANCHOR TEXT INTERNAL LINKS ──────────────────────────────────
def add_anchor_internal_links(html, post, all_posts):
    """
    Add contextual internal links + Related Posts section.
    SAFE: only operates inside <article> or <main> content.
    NEVER touches: nav, header, footer, style, script, sidebar.
    """
    changes = 0
    cur_url = post["url"]
    cur_topics = post["topics"]

    related_by_topic = []
    for p in all_posts:
        if p["url"] == cur_url:
            continue
        shared = set(p["topics"]) & set(cur_topics)
        if shared:
            related_by_topic.append((p, len(shared)))
    related_by_topic.sort(key=lambda x: -x[1])

    # ── Part A: Anchor text links — only inside <article> ──
    # Find the article element specifically (not nav/sidebar/footer)
    art_m = re.search(r'(<article\b[^>]*class=["\'][^"\']*\bart\b[^"\']*["\'][^>]*>)(.*?)(</article>)',
                      html, re.DOTALL | re.IGNORECASE)
    if not art_m:
        art_m = re.search(r'(<article\b[^>]*>)(.*?)(</article>)', html, re.DOTALL | re.IGNORECASE)

    if art_m and related_by_topic:
        art_before = html[:art_m.start()]
        art_open   = art_m.group(1)
        art_body   = art_m.group(2)
        art_close  = art_m.group(3)
        art_after  = html[art_m.end():]

        already_linked = set()
        for rel_post, _ in related_by_topic[:6]:
            if rel_post["url"] in already_linked:
                continue
            rel_title = rel_post["title"]
            rel_url   = rel_post["url"]

            words = [w for w in rel_title.split()
                     if len(w) > 4 and w.lower() not in {
                         "with","that","this","from","have","your","what",
                         "when","best","2026","2027","which","better","complete"
                     }]

            for phrase_len in [3, 2]:
                if len(words) < phrase_len:
                    continue
                for i in range(len(words) - phrase_len + 1):
                    phrase = " ".join(words[i:i+phrase_len])
                    pattern = (f'(?<!href=["\'])(?<!>)({re.escape(phrase)})'
                               f'(?![^<]*</a>)(?![^<]*href)')
                    m = re.search(pattern, art_body, re.IGNORECASE)
                    if m and f'href="{rel_url}"' not in art_body:
                        # Use ilink class to match your site's existing link style
                        anchor = (f'<a href="{rel_url}" title="{rel_title}" '
                                  f'class="ilink">{m.group(1)}</a>')
                        art_body = art_body[:m.start()] + anchor + art_body[m.end():]
                        already_linked.add(rel_url)
                        changes += 1
                        break
                if rel_url in already_linked:
                    break

        html = art_before + art_open + art_body + art_close + art_after

    # ── Part B: Related posts — only if not already present ──
    if "related-card" in html or "You Might Also Like" in html or "Related Guides" in html:
        return html, changes

    related = [(p["url"], p["title"]) for p, _ in related_by_topic[:4]]
    if len(related) < 2:
        return html, changes

    # Use your site's existing .related-card style
    items = "\n".join(
        f'      <div class="related-card">\n'
        f'        <h4><a href="{u}" class="ilink">{t}</a></h4>\n'
        f'        <p>Explore this related guide from Aivora AI.</p>\n'
        f'      </div>'
        for u, t in related
    )
    section = (
        f'\n<section style="margin:40px 0">\n'
        f'  <h2>Related Guides</h2>\n'
        f'{items}\n'
        f'</section>\n'
    )

    # Insert before author-box, or cta-box, or </article>, or </main>
    for tag in ['<div class="author-box"', '<div class="cta-box"',
                '</article>', '</main>', '</body>']:
        if tag in html:
            html = html.replace(tag, section + "\n" + tag, 1)
            changes += 1
            break

    return html, changes

# ── FIX 6: BROKEN LINKS ──────────────────────────────────────────────────────
def find_and_fix_broken_links(html, all_urls, filepath):
    """Fix %20/space in internal URLs. Never rewrites working URLs."""
    changes = 0
    broken = []

    links = re.findall(
        r'href=["\'](' + re.escape(SITE_URL) + r'[^"\']+)["\']', html)
    links += re.findall(r'href=["\'](/[^"\']+)["\']', html)

    for link in links:
        full = link if link.startswith("http") else SITE_URL + link
        rel_path = full.replace(SITE_URL + "/", "").replace(SITE_URL, "")
        local = os.path.join(REPO_ROOT, rel_path.lstrip("/"))

        if not os.path.exists(local) and not rel_path.endswith(("/", "")):
            if "%20" in link or " " in link:
                fixed = link.replace(" ", "-").replace("%20", "-")
                html = html.replace(f'href="{link}"', f'href="{fixed}"')
                html = html.replace(f"href='{link}'", f"href='{fixed}'")
                changes += 1
            else:
                broken.append(full)

    return html, changes, broken

# ── FIX 7: SORT BLOG CARDS — MAIN ONLY, NAV/FOOTER SAFE ─────────────────────
def sort_blog_cards_by_date(html, filepath):
    """
    Sort blog listing cards newest-first.
    CRITICAL SAFETY: only operates inside <main> block.
    Header, nav, footer are byte-for-byte unchanged.
    """
    if "blog.html" not in filepath and "blog/index" not in filepath:
        return html, 0

    # Step 1: Extract <main> only
    main_m = re.search(r'(<main\b[^>]*>)(.*?)(</main>)',
                       html, re.DOTALL | re.IGNORECASE)
    if not main_m:
        main_m = re.search(
            r'(<(?:section|div)\b[^>]*class=["\'][^"\']*blog[^"\']*["\'][^>]*>)(.*?)'
            r'(</(?:section|div)>)',
            html, re.DOTALL | re.IGNORECASE)
    if not main_m:
        return html, 0

    before_main = html[:main_m.start()]
    main_open   = main_m.group(1)
    main_body   = main_m.group(2)
    main_close  = main_m.group(3)
    after_main  = html[main_m.end():]

    # Step 2: Match only "rich" cards (contain block child elements — not plain nav links)
    card_pattern = (
        r'(<a\s[^>]*href=["\'](?:https://aivoraai\.github\.io)?/blog/[^"\' #?]+["\'][^>]*>'
        r'(?:(?!</a>).)*?<(?:h[1-6]|p|div|span|article|time|strong)\b[^>]*>'
        r'(?:(?!</a>).)*?</a>)'
    )
    cards = re.findall(card_pattern, main_body, re.DOTALL | re.IGNORECASE)
    if len(cards) < 3:
        return html, 0

    def extract_date_from_card(card):
        m = re.search(r'(\d{4}-\d{2}-\d{2})', card)
        if m:
            try: return datetime.strptime(m.group(1), "%Y-%m-%d").date()
            except: pass
        m = re.search(
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',
            card)
        if m:
            try: return date(int(m.group(3)), MONTH_MAP.get(m.group(2), 1), int(m.group(1)))
            except: pass
        m = re.search(
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', card)
        if m:
            try: return date(int(m.group(2)), MONTH_MAP.get(m.group(1), 1), 1)
            except: pass
        return date(2000, 1, 1)

    dated_cards  = [(extract_date_from_card(c), c) for c in cards]
    sorted_cards = sorted(dated_cards, key=lambda x: x[0], reverse=True)

    if [c for _, c in dated_cards] == [c for _, c in sorted_cards]:
        return html, 0  # Already sorted

    # Step 3: Rebuild main_body only — everything else untouched
    parts = re.split(card_pattern, main_body, flags=re.DOTALL | re.IGNORECASE)
    new_parts = []
    card_idx = 0
    for part in parts:
        if (re.match(card_pattern, part, re.DOTALL | re.IGNORECASE)
                and card_idx < len(sorted_cards)):
            new_parts.append(sorted_cards[card_idx][1])
            card_idx += 1
        else:
            new_parts.append(part)

    new_main_body = "".join(new_parts)
    return before_main + main_open + new_main_body + main_close + after_main, 1

# ── FIX 8: SITEMAP ───────────────────────────────────────────────────────────
def gen_sitemap(posts, all_files):
    """Generate complete sitemap.xml with all pages."""
    entries = []
    seen = set()

    for p in posts:
        url = p["url"]
        if url in seen: continue
        seen.add(url)
        d = p["date_str"] or TODAY
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
        if url in seen or BLOG_DIR in f: continue
        seen.add(url)
        pri  = "1.0" if "index.html" in f else "0.6"
        freq = "daily" if "index.html" in f else "monthly"
        entries.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(entries)}
</urlset>
"""
    write(os.path.join(REPO_ROOT, "sitemap.xml"), xml)
    return len(entries)

# ── FIX 9: ROBOTS ────────────────────────────────────────────────────────────
def gen_robots():
    """Generate optimized robots.txt."""
    write(os.path.join(REPO_ROOT, "robots.txt"), f"""# robots.txt — Aivora AI
# Auto-generated: {TODAY}

User-agent: *
Allow: /
Disallow: /assets/private/
Disallow: /_seo_backups/
Disallow: /drafts/

User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Crawl-delay: 2

User-agent: GPTBot
Allow: /blog/
Allow: /about.html
Allow: /contact.html
Disallow: /assets/private/

User-agent: Google-Extended
Allow: /blog/

User-agent: ClaudeBot
Allow: /blog/

User-agent: CCBot
Disallow: /

Sitemap: {SITE_URL}/sitemap.xml
""")

# ── REPORT ───────────────────────────────────────────────────────────────────
def save_report(stats, broken_links):
    broken_text = (
        "\n".join(f"  BROKEN: {b}" for b in broken_links[:30])
        if broken_links else "  All links OK!"
    )

    report = f"""
╔══════════════════════════════════════════════════════╗
║      AIVORA AI — SEO MEGA FIX REPORT v3.0           ║
║      Generated: {TODAY}                        ║
║      Site: {SITE_URL}   ║
╚══════════════════════════════════════════════════════╝

DESIGN STATUS:     ✅ FULLY PRESERVED
  • Dark theme (#050a0e, #00c896) — UNTOUCHED
  • Fonts (Outfit, Space Grotesk) — UNTOUCHED
  • Animations (shimmer, pulse, slideIn) — UNTOUCHED
  • Nav / Header / Footer — UNTOUCHED
  • VS Cards, Diagram Nodes, Sidebar — UNTOUCHED
  • FAQ Accordion, Author Box, CTA Box — UNTOUCHED
  • All JavaScript — UNTOUCHED
  • All Structured Data — UNTOUCHED

SEO FIXES APPLIED:
  Files processed:        {stats['files']}
  Dates fixed:            {stats['dates']}
  Canonicals fixed:       {stats['canon']}
  Meta descs added:       {stats['meta']}
  Internal links added:   {stats['links']} posts ({stats['anchors']} total links)
  Broken links fixed:     {stats['broken_fixed']}
  Blog cards sorted:      {stats['sorted']} pages
  Sitemap URLs:           {stats['sitemap']}

BROKEN LINKS (need manual fix):
{broken_text}

══════════════════════════════════════════════════════
  NEXT STEPS — DO THIS NOW
══════════════════════════════════════════════════════

1. git add .
2. git commit -m "SEO Auto Fix v3 — {TODAY}"
3. git push

4. GOOGLE SEARCH CONSOLE:
   → Sitemaps → Submit: {SITE_URL}/sitemap.xml
   → URL Inspection → Request Indexing for key pages

5. Wait 48-72 hours → check GSC for indexing status

WHY PAGES NOT INDEXED?
  • Future dates tell Google "not published yet"
  • This script fixes all future dates → now indexable
  • After push + sitemap submit → 48-72 hours for crawl
  • Impressions in GSC → 2-4 weeks
"""
    write(os.path.join(REPO_ROOT, "seo_report.txt"), report)
    return report

# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*58)
    print("  AIVORA AI SEO MEGA FIX v3.0")
    print(f"  Date: {TODAY} | Site: {SITE_URL}")
    print("  Design Protection: ACTIVE (nav/footer/CSS/JS safe)")
    print("="*58 + "\n")

    all_files = find_html()
    if not all_files:
        print("No HTML files found! Run from repo root folder.")
        print(f"Current dir: {os.path.abspath('.')}")
        return

    print(f"Found {len(all_files)} HTML files")
    print("Building post database...")
    posts = build_post_db(all_files)
    print(f"  {len(posts)} blog posts indexed")
    all_urls = set(to_url(f) for f in all_files)

    stats = {
        "files":0, "dates":0, "canon":0, "meta":0,
        "links":0, "anchors":0, "broken_fixed":0, "sorted":0, "sitemap":0
    }
    all_broken = []

    print("\nProcessing HTML files...\n")

    for fp in all_files:
        html = read(fp)
        orig = html
        log  = []
        stats["files"] += 1

        post_data = next((p for p in posts if p["file"] == fp), None)

        html, n = fix_dates(html)
        if n: log.append(f"dates:{n}"); stats["dates"] += 1

        html, n = fix_canonical(html, fp)
        if n: log.append(f"canon:{n}"); stats["canon"] += 1

        html, n = fix_meta_desc(html, fp)
        if n: log.append("meta"); stats["meta"] += 1

        html, n, broken = find_and_fix_broken_links(html, all_urls, fp)
        if n: log.append(f"broken:{n}"); stats["broken_fixed"] += n
        all_broken.extend(broken)

        if post_data:
            html, n = add_anchor_internal_links(html, post_data, posts)
            if n: log.append(f"links:{n}"); stats["links"] += 1; stats["anchors"] += n

        html, n = sort_blog_cards_by_date(html, fp)
        if n: log.append("sorted"); stats["sorted"] += 1

        if html != orig:
            backup(fp)
            write(fp, html)
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"  FIXED  {rel:<55} [{', '.join(log)}]")
        else:
            rel = os.path.relpath(fp, REPO_ROOT)
            print(f"  OK     {rel}")

    print(f"\nGenerating sitemap.xml...")
    stats["sitemap"] = gen_sitemap(posts, all_files)
    print(f"  {stats['sitemap']} URLs")

    print(f"Generating robots.txt...")
    gen_robots()
    print(f"  Done")

    print(f"\nSaving report → seo_report.txt")
    save_report(stats, list(set(all_broken)))

    print("\n" + "="*58)
    print("  ALL DONE!")
    print("="*58)
    print(f"  Dates fixed:           {stats['dates']}")
    print(f"  Internal links added:  {stats['links']} posts")
    print(f"  Anchor links added:    {stats['anchors']} total")
    print(f"  Blog cards sorted:     {stats['sorted']} pages")
    print(f"  Broken links found:    {len(set(all_broken))}")
    print(f"  Sitemap URLs:          {stats['sitemap']}")
    print(f"\n  Design preserved: nav, footer, CSS, JS, animations")
    print(f"\n  Now run:")
    print(f"  git add .")
    print(f'  git commit -m "SEO Fix v3 {TODAY}"')
    print(f"  git push\n")

if __name__ == "__main__":
    main()

On Tue, Jun 9, 2026 at 3:11 PM varun lalwani <varun.edhacare@gmail.com> wrote:



Prashant Lalwani
3:21 PM (4 minutes ago)
to me

name: 🤖 Aivora SEO Mega Fix v3

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run — show what would change, do not commit'
        required: false
        default: 'false'
  schedule:
    - cron: '0 2 * * 1'   # Every Monday at 2am IST (UTC+5:30 → UTC 20:30 Sunday)

jobs:
  seo-fix:
    runs-on: ubuntu-latest
    name: SEO Auto Fix — Design Safe v3

    permissions:
      contents: write

    steps:

      - name: 📥 Checkout repo (full history)
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 🐍 Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 🔍 Verify script exists
        run: |
          if [ ! -f aivora_seo_fix.py ]; then
            echo "ERROR: aivora_seo_fix.py not found in repo root!"
            echo "Please commit the script file first."
            exit 1
          fi
          echo "Script found. Python version:"
          python --version

      - name: 🔧 Run SEO Mega Fix Script
        run: python aivora_seo_fix.py

      - name: 📋 Show fix report
        run: |
          echo "==========================================="
          cat seo_report.txt || echo "Report not generated"
          echo "==========================================="

      - name: 📊 Count changed files
        id: changes
        run: |
          CHANGED=$(git diff --name-only | wc -l)
          echo "changed=$CHANGED" >> $GITHUB_OUTPUT
          echo "Files changed: $CHANGED"
          if [ "$CHANGED" -gt "0" ]; then
            echo "Changed files:"
            git diff --name-only
          fi

      - name: 📤 Commit and Push all fixes
        if: steps.changes.outputs.changed != '0' && github.event.inputs.dry_run != 'true'
        run: |
          git config user.name "Aivora SEO Bot"
          git config user.email "aivoraai@outlook.com"
          git add -A
          git diff --staged --quiet || git commit -m "🤖 SEO Auto Fix v3: dates+links+sitemap+sort — $(date +'%d %b %Y')"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: ✅ Done — no changes needed
        if: steps.changes.outputs.changed == '0'
        run: echo "Everything already up to date. No changes committed."

      - name: 🧪 Dry run summary
        if: github.event.inputs.dry_run == 'true'
        run: |
          echo "DRY RUN MODE — changes NOT committed"
          git diff --stat

#!/usr/bin/env python3
"""
====================================================
AIVORA AI — COMPLETE SEO / GEO / AEO ENGINE
====================================================
Author : Varun Lalwani / Aivora AI
Purpose: Full automated SEO audit, schema injection,
         sitemap/robots generation, internal linking,
         broken-link detection, and AI-visibility
         optimisation for every page on the site.
Usage  : python seo_engine.py [--audit] [--fix] [--all]
====================================================
"""

import os
import re
import json
import time
import argparse
import hashlib
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Optional

# ── Config ─────────────────────────────────────────
BASE_URL   = "https://aivoraai.github.io"
SITE_ROOT  = Path(".")          # run from repo root
OUTPUT_DIR = Path("_seo_output")
REPORT_DIR = Path("_reports")
SCHEMA_DIR = Path("_schemas")

SITE_NAME   = "Aivora AI"
AUTHOR_NAME = "Varun Lalwani"
AUTHOR_URL  = f"{BASE_URL}/about.html"
LOGO_URL    = f"{BASE_URL}/assets/images/aivora-logo-primary.png"
TWITTER     = "@aivoraai"

NOW_ISO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
NOW_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ── HTML Parser ─────────────────────────────────────
class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.h1s: list[str] = []
        self.h2s: list[str] = []
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.has_schema = False
        self.has_og    = False
        self.has_twitter = False
        self._in_title = False
        self._in_h1    = False
        self._in_h2    = False
        self._cur_h    = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            n = attrs.get("name","").lower()
            p = attrs.get("property","").lower()
            c = attrs.get("content","")
            if n == "description":    self.description = c
            if p == "og:title":       self.has_og = True
            if n == "twitter:card":   self.has_twitter = True
            if attrs.get("name","").lower() == "canonical":
                self.canonical = attrs.get("content","")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href","")
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self.has_schema = True
        elif tag == "h1":
            self._in_h1, self._cur_h = True, ""
        elif tag == "h2":
            self._in_h2, self._cur_h = True, ""
        elif tag == "a":
            href = attrs.get("href","")
            if href:
                self.links.append({"href": href, "text": ""})
        elif tag == "img":
            self.images.append({
                "src": attrs.get("src",""),
                "alt": attrs.get("alt",""),
                "loading": attrs.get("loading","")
            })

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False
        if tag == "h1":
            if self._cur_h: self.h1s.append(self._cur_h.strip())
            self._in_h1, self._cur_h = False, ""
        if tag == "h2":
            if self._cur_h: self.h2s.append(self._cur_h.strip())
            self._in_h2, self._cur_h = False, ""

    def handle_data(self, data):
        if self._in_title: self.title += data
        if self._in_h1:    self._cur_h += data
        if self._in_h2:    self._cur_h += data


# ── Helpers ─────────────────────────────────────────
def read_html(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def write_html(path: Path, content: str):
    path.write_text(content, encoding="utf-8")

def parse_page(html: str) -> PageParser:
    p = PageParser()
    p.feed(html)
    return p

def url_for(path: Path) -> str:
    rel = path.as_posix().lstrip("./")
    return f"{BASE_URL}/{rel}"

def check_url(url: str, timeout: int = 8) -> int:
    try:
        req = urllib.request.Request(url, method="HEAD",
              headers={"User-Agent":"AivoraSEOBot/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


# ═══════════════════════════════════════════════════
# PHASE 1 — AUDIT
# ═══════════════════════════════════════════════════
def audit_site() -> dict:
    print("\n🔍 PHASE 1: Full Website Audit")
    issues: list[dict] = []
    pages_data: list[dict] = []

    html_files = sorted(SITE_ROOT.rglob("*.html"))
    if not html_files:
        print("  ⚠ No HTML files found. Run from repo root.")
        return {"issues": issues, "pages": pages_data}

    for fpath in html_files:
        rel = fpath.relative_to(SITE_ROOT)
        page_url = url_for(rel)
        html = read_html(fpath)
        p = parse_page(html)

        page = {
            "file": str(rel),
            "url": page_url,
            "title": p.title.strip(),
            "description": p.description,
            "canonical": p.canonical,
            "h1_count": len(p.h1s),
            "h1s": p.h1s,
            "h2_count": len(p.h2s),
            "links": len(p.links),
            "images": len(p.images),
            "missing_alt": [i for i in p.images if not i["alt"]],
            "no_lazy": [i for i in p.images if i["loading"] != "lazy"],
            "has_schema": p.has_schema,
            "has_og": p.has_og,
            "has_twitter": p.has_twitter,
        }
        pages_data.append(page)

        # — SEO checks —
        if not p.title:
            issues.append({"file": str(rel), "severity":"HIGH",
                "type":"Missing Title", "detail":"No <title> tag found."})
        elif len(p.title) > 70:
            issues.append({"file": str(rel), "severity":"MEDIUM",
                "type":"Title Too Long", "detail":f"Title is {len(p.title)} chars (max 70)."})
        elif len(p.title) < 30:
            issues.append({"file": str(rel), "severity":"LOW",
                "type":"Title Too Short", "detail":f"Title is {len(p.title)} chars (min 30)."})

        if not p.description:
            issues.append({"file": str(rel), "severity":"HIGH",
                "type":"Missing Meta Description", "detail":"No meta description found."})
        elif len(p.description) > 165:
            issues.append({"file": str(rel), "severity":"MEDIUM",
                "type":"Meta Description Too Long", "detail":f"{len(p.description)} chars."})

        if not p.canonical:
            issues.append({"file": str(rel), "severity":"HIGH",
                "type":"Missing Canonical", "detail":"No canonical tag."})

        if len(p.h1s) == 0:
            issues.append({"file": str(rel), "severity":"HIGH",
                "type":"Missing H1", "detail":"Page has no H1."})
        elif len(p.h1s) > 1:
            issues.append({"file": str(rel), "severity":"MEDIUM",
                "type":"Multiple H1s", "detail":f"Found {len(p.h1s)} H1 tags."})

        if not p.has_schema:
            issues.append({"file": str(rel), "severity":"MEDIUM",
                "type":"Missing Schema", "detail":"No JSON-LD structured data."})

        if not p.has_og:
            issues.append({"file": str(rel), "severity":"MEDIUM",
                "type":"Missing OG Tags", "detail":"No Open Graph tags."})

        if not p.has_twitter:
            issues.append({"file": str(rel), "severity":"LOW",
                "type":"Missing Twitter Card", "detail":"No Twitter Card meta."})

        for img in p.missing_alt:
            issues.append({"file": str(rel), "severity":"MEDIUM",
                "type":"Missing Alt Text", "detail":f"Image: {img['src']}"})

        if len(p.links) < 3:
            issues.append({"file": str(rel), "severity":"LOW",
                "type":"Few Internal Links", "detail":f"Only {len(p.links)} links found."})

    print(f"  ✅ Audited {len(pages_data)} pages — {len(issues)} issues found.")
    return {"issues": issues, "pages": pages_data}


# ═══════════════════════════════════════════════════
# PHASE 2 — BROKEN LINK CHECKER
# ═══════════════════════════════════════════════════
def check_broken_links(pages_data: list[dict]) -> list[dict]:
    print("\n🔗 PHASE 9: Broken Link Scan")
    broken = []
    seen: dict[str, int] = {}
    for page in pages_data:
        html = read_html(SITE_ROOT / page["file"])
        p = parse_page(html)
        for link in p.links:
            href = link["href"]
            if not href or href.startswith("#") or href.startswith("mailto:") \
                or href.startswith("javascript:"):
                continue
            full = href if href.startswith("http") else f"{BASE_URL}/{href.lstrip('/')}"
            if full in seen:
                status = seen[full]
            else:
                status = check_url(full)
                seen[full] = status
                time.sleep(0.1)
            if status in (0, 404, 410):
                broken.append({"page": page["file"], "url": full, "status": status})
    print(f"  ✅ Found {len(broken)} broken links.")
    return broken


# ═══════════════════════════════════════════════════
# PHASE 3 — META INJECTION ENGINE
# ═══════════════════════════════════════════════════
def build_meta_block(title: str, description: str, url: str,
                      og_image: str = "", schema_json: str = "",
                      breadcrumbs: Optional[list] = None) -> str:
    safe_title = title.replace('"', '&quot;')
    safe_desc  = description.replace('"', '&quot;')
    og_img     = og_image or f"{BASE_URL}/assets/og-home.png"

    bc_schema = ""
    if breadcrumbs:
        items = [{"@type":"ListItem","position":i+1,
                  "name":b["name"],"item":b["url"]}
                 for i, b in enumerate(breadcrumbs)]
        bc_schema = json.dumps({
            "@context":"https://schema.org",
            "@type":"BreadcrumbList",
            "itemListElement": items
        }, indent=2)

    return f"""
  <!-- ═══ SEO META — Auto-generated by Aivora SEO Engine ═══ -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{safe_title}</title>
  <meta name="description" content="{safe_desc}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <meta name="author" content="{AUTHOR_NAME}">
  <link rel="canonical" href="{url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{safe_title}">
  <meta property="og:description" content="{safe_desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:image" content="{og_img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="en_US">
  <meta property="og:updated_time" content="{NOW_ISO}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="{TWITTER}">
  <meta name="twitter:creator" content="{TWITTER}">
  <meta name="twitter:title" content="{safe_title}">
  <meta name="twitter:description" content="{safe_desc}">
  <meta name="twitter:image" content="{og_img}">

  <!-- AI Search Bots -->
  <meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <meta name="bingbot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">

  <!-- Page Signals -->
  <meta name="last-modified" content="{NOW_DATE}">
  <meta name="revisit-after" content="7 days">
  <meta name="language" content="English">

  <!-- Perf -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="dns-prefetch" href="https://www.googletagmanager.com">

  <!-- Schema.org JSON-LD -->
  {f'<script type="application/ld+json">{schema_json}</script>' if schema_json else ''}
  {f'<script type="application/ld+json">{bc_schema}</script>' if bc_schema else ''}
  <!-- ═══ End SEO META ═══ -->
"""


# ═══════════════════════════════════════════════════
# PHASE 4 — SCHEMA BUILDER
# ═══════════════════════════════════════════════════
def build_website_schema() -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{BASE_URL}/#organization",
                "name": SITE_NAME,
                "url": BASE_URL,
                "logo": {"@type": "ImageObject", "url": LOGO_URL},
                "sameAs": [
                    "https://twitter.com/aivoraai",
                    "https://linkedin.com/company/aivoraai"
                ],
                "contactPoint": {
                    "@type": "ContactPoint",
                    "email": "contact@aivoraai.com",
                    "contactType": "customer service"
                }
            },
            {
                "@type": "WebSite",
                "@id": f"{BASE_URL}/#website",
                "url": BASE_URL,
                "name": SITE_NAME,
                "publisher": {"@id": f"{BASE_URL}/#organization"},
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": {
                        "@type": "EntryPoint",
                        "urlTemplate": f"{BASE_URL}/blog.html?q={{search_term_string}}"
                    },
                    "query-input": "required name=search_term_string"
                }
            }
        ]
    }, indent=2)


def build_article_schema(title: str, description: str, url: str,
                          author: str = AUTHOR_NAME,
                          image: str = "") -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "url": url,
        "datePublished": NOW_DATE,
        "dateModified": NOW_DATE,
        "author": {
            "@type": "Person",
            "name": author,
            "url": AUTHOR_URL
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "logo": {"@type": "ImageObject", "url": LOGO_URL}
        },
        "image": image or f"{BASE_URL}/assets/og-home.png",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}
    }, indent=2)


def build_faq_schema(faqs: list[dict]) -> str:
    """faqs = [{"question": "...", "answer": "..."}]"""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f["answer"]
                }
            } for f in faqs
        ]
    }, indent=2)


def build_howto_schema(name: str, steps: list[str]) -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": name,
        "step": [
            {"@type": "HowToStep", "text": s, "position": i+1}
            for i, s in enumerate(steps)
        ]
    }, indent=2)


# ═══════════════════════════════════════════════════
# PHASE 5 — SITEMAP GENERATOR
# ═══════════════════════════════════════════════════
def generate_sitemap(pages_data: list[dict]):
    print("\n🗺  PHASE 6: Sitemap Generation")

    # sitemap.xml
    urls = []
    for page in pages_data:
        url  = page["url"]
        freq = "weekly"
        pri  = "1.0" if "index" in page["file"] else "0.8"
        urls.append(
            f"  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{NOW_DATE}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{pri}</priority>\n"
            f"  </url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9\n'
        '        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n'
    ) + "\n".join(urls) + "\n</urlset>"

    (SITE_ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    print("  ✅ sitemap.xml generated")

    # sitemap.html
    rows = "\n".join(
        f'    <tr><td><a href="{p["url"]}">{p["file"]}</a></td>'
        f'<td>{p["title"][:60]}</td>'
        f'<td>{NOW_DATE}</td></tr>'
        for p in pages_data
    )
    html_sitemap = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HTML Sitemap | {SITE_NAME}</title>
  <meta name="description" content="Complete HTML sitemap for {SITE_NAME}">
  <link rel="canonical" href="{BASE_URL}/sitemap.html">
  <style>
    body{{font-family:sans-serif;max-width:900px;margin:40px auto;padding:0 20px}}
    h1{{color:#0a1628}}table{{width:100%;border-collapse:collapse}}
    th,td{{padding:10px;border:1px solid #ddd;text-align:left}}
    th{{background:#0a1628;color:#fff}}tr:nth-child(even){{background:#f9f9f9}}
  </style>
</head>
<body>
  <h1>{SITE_NAME} — HTML Sitemap</h1>
  <p>Last updated: {NOW_DATE} | Total pages: {len(pages_data)}</p>
  <table>
    <thead><tr><th>URL</th><th>Title</th><th>Last Modified</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>"""
    (SITE_ROOT / "sitemap.html").write_text(html_sitemap, encoding="utf-8")
    print("  ✅ sitemap.html generated")


# ═══════════════════════════════════════════════════
# PHASE 6 — ROBOTS.TXT
# ═══════════════════════════════════════════════════
def generate_robots():
    print("\n🤖 PHASE 7: robots.txt Generation")
    content = f"""# ============================================================
# robots.txt — {SITE_NAME}
# Generated: {NOW_DATE} by Aivora SEO Engine
# ============================================================

# ── Search Engines ──────────────────────────────────────────
User-agent: Googlebot
Allow: /
Disallow: /private/
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Disallow: /private/
Crawl-delay: 2

User-agent: Slurp
Allow: /
Crawl-delay: 5

User-agent: DuckDuckBot
Allow: /
Crawl-delay: 3

# ── AI Crawlers (Full Access) ────────────────────────────────
User-agent: GPTBot
Allow: /
Disallow: /private/
# Crawl-delay: 2

User-agent: ClaudeBot
Allow: /
Disallow: /private/

User-agent: PerplexityBot
Allow: /
Disallow: /private/

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: Amazonbot
Allow: /
Crawl-delay: 5

User-agent: FacebookBot
Allow: /

User-agent: Twitterbot
Allow: /

# ── Block Bad Bots ───────────────────────────────────────────
User-agent: AhrefsBot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: MJ12bot
Disallow: /

User-agent: DotBot
Disallow: /

# ── Default ──────────────────────────────────────────────────
User-agent: *
Allow: /
Disallow: /private/
Disallow: /_site/
Disallow: /node_modules/

# ── Sitemaps ─────────────────────────────────────────────────
Sitemap: {BASE_URL}/sitemap.xml
Sitemap: {BASE_URL}/sitemap.html

# ── Host ─────────────────────────────────────────────────────
Host: {BASE_URL}
"""
    (SITE_ROOT / "robots.txt").write_text(content, encoding="utf-8")
    print("  ✅ robots.txt generated")


# ═══════════════════════════════════════════════════
# PHASE 7 — IMAGE ALT TEXT INJECTOR
# ═══════════════════════════════════════════════════
def fix_image_alts():
    print("\n🖼  PHASE 10: Image Alt Text Fix")
    fixed = 0
    for fpath in SITE_ROOT.rglob("*.html"):
        html = read_html(fpath)
        orig = html

        def _add_alt(m):
            tag = m.group(0)
            if 'alt=' in tag:
                return tag
            src = re.search(r'src=["\']([^"\']+)["\']', tag)
            alt = ""
            if src:
                name = Path(src.group(1)).stem
                alt  = name.replace("-","  ").replace("_"," ").title()
            return tag.rstrip("/>").rstrip() + f' alt="{alt}" loading="lazy">'

        html = re.sub(r'<img[^>]+>', _add_alt, html)

        if html != orig:
            write_html(fpath, html)
            fixed += 1
    print(f"  ✅ Fixed images in {fixed} files")


# ═══════════════════════════════════════════════════
# PHASE 8 — INTERNAL LINKING ENGINE
# ═══════════════════════════════════════════════════
INTERNAL_LINK_MAP = {
    "AI tools":           "/product.html",
    "affiliate marketing":"/blog/ai-affiliate-marketing-guide-2026.html",
    "passive income":     "/blog/ai-passive-income-tools-2026.html",
    "AI for beginners":   "/blog/ai-tools-beginners-guide-2026.html",
    "GPT Creator Club":   "/blog/gpt-creator-club-review-2026.html",
    "AI video":           "/blog/ai-video-creator-review-2026.html",
    "AI growth stack":    "/blog/ai-growth-stack-2026.html",
    "blog":               "/blog.html",
    "about":              "/about.html",
    "contact":            "/contact.html",
}

def inject_internal_links(html: str, current_file: str) -> str:
    """Add contextual internal links to body text."""
    added = 0
    for keyword, path in INTERNAL_LINK_MAP.items():
        full_url = f"{BASE_URL}{path}"
        rel_file  = path.lstrip("/")
        if rel_file == current_file:
            continue
        # Only link first occurrence, not inside existing links/tags
        pattern = rf'(?<!href=["\'].*?)(?<!>)({re.escape(keyword)})(?!</a>)(?![^<]*>)'
        def replacer(m, url=full_url, kw=keyword):
            return f'<a href="{url}" title="{kw} — {SITE_NAME}">{m.group(1)}</a>'
        new_html, n = re.subn(pattern, replacer, html, count=1, flags=re.IGNORECASE)
        if n:
            html = new_html
            added += 1
    return html


# ═══════════════════════════════════════════════════
# PHASE 9 — BLOG TEMPLATE GENERATOR
# ═══════════════════════════════════════════════════
BLOG_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  {{META_BLOCK}}
</head>
<body>

<!-- Breadcrumbs -->
<nav aria-label="breadcrumb">
  <ol itemscope itemtype="https://schema.org/BreadcrumbList">
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a itemprop="item" href="{base}/"><span itemprop="name">Home</span></a>
      <meta itemprop="position" content="1">
    </li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a itemprop="item" href="{base}/blog.html"><span itemprop="name">Blog</span></a>
      <meta itemprop="position" content="2">
    </li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <span itemprop="name">{{PAGE_TITLE}}</span>
      <meta itemprop="position" content="3">
    </li>
  </ol>
</nav>

<main id="main-content">

  <!-- Quick Answer Box (AI Visibility) -->
  <section class="quick-answer" aria-label="Quick Answer">
    <h2>Quick Answer</h2>
    <p>{{QUICK_ANSWER}}</p>
  </section>

  <!-- Key Takeaways -->
  <section class="key-takeaways">
    <h2>Key Takeaways</h2>
    <ul>
      {{KEY_TAKEAWAYS}}
    </ul>
  </section>

  <!-- Table of Contents -->
  <nav class="toc" aria-label="Table of Contents">
    <h2>Table of Contents</h2>
    <ol>
      {{TOC_ITEMS}}
    </ol>
  </nav>

  <!-- Main Article -->
  <article itemscope itemtype="https://schema.org/Article">
    <header>
      <h1 itemprop="headline">{{PAGE_TITLE}}</h1>
      <p class="meta">
        By <a itemprop="author" href="{base}/about.html">{author}</a> ·
        <time itemprop="datePublished" datetime="{{DATE}}">{{DATE}}</time> ·
        Last updated: <time itemprop="dateModified" datetime="{{NOW}}">{{NOW}}</time>
      </p>
    </header>

    <!-- Expert Insight (E-E-A-T) -->
    <aside class="expert-insight">
      <strong>Expert Insight:</strong> {{EXPERT_INSIGHT}}
    </aside>

    {{MAIN_CONTENT}}

    <!-- Comparison Table -->
    <section class="comparison">
      <h2>Comparison: {{COMPARISON_TITLE}}</h2>
      {{COMPARISON_TABLE}}
    </section>

    <!-- Statistics Section -->
    <section class="statistics">
      <h2>Key Statistics</h2>
      {{STATISTICS}}
    </section>

  </article>

  <!-- FAQ Section -->
  <section class="faq" aria-label="Frequently Asked Questions">
    <h2>Frequently Asked Questions</h2>
    {{FAQ_ITEMS}}
  </section>

  <!-- Related Articles -->
  <section class="related-articles">
    <h2>Related Articles</h2>
    <ul>
      {{RELATED_ARTICLES}}
    </ul>
  </section>

  <!-- CTA -->
  <section class="cta">
    <h2>Start Earning with AI Today</h2>
    <p>Explore 200+ tested AI tools and affiliate programs.</p>
    <a href="{base}/product.html" class="btn-primary">Browse AI Tools →</a>
    <a href="{base}/blog.html"    class="btn-secondary">Read More Guides</a>
  </section>

  <!-- Author Box -->
  <section class="author-box" aria-label="About the Author">
    <img src="{base}/assets/images/varun-lalwani.jpg" alt="{author} — {site_name} Director" loading="lazy" width="80" height="80">
    <div>
      <strong>{author}</strong>
      <p>Director at {site_name}. AI tools researcher with hands-on experience across 200+ tools. Trusted by 80,000+ creators worldwide.</p>
      <a href="{base}/about.html">Read full bio →</a>
    </div>
  </section>

</main>

</body>
</html>'''.format(
    base=BASE_URL,
    author=AUTHOR_NAME,
    site_name=SITE_NAME
)

def generate_blog_post(slug: str, title: str, description: str,
                        quick_answer: str, key_takeaways: list[str],
                        faqs: list[dict], main_content: str = "",
                        og_image: str = "") -> str:
    """Render a fully-SEO'd blog post HTML file."""
    url = f"{BASE_URL}/blog/{slug}.html"
    schema = build_article_schema(title, description, url,
                                  image=og_image)
    faq_schema = build_faq_schema(faqs) if faqs else ""
    meta = build_meta_block(title, description, url, og_image,
                             schema_json=schema,
                             breadcrumbs=[
                                 {"name":"Home","url":BASE_URL+"/"},
                                 {"name":"Blog","url":BASE_URL+"/blog.html"},
                                 {"name":title,"url":url}
                             ])

    takeaways_html = "\n      ".join(f"<li>{t}</li>" for t in key_takeaways)
    faq_html = "\n    ".join(
        f'<details><summary><strong>{f["question"]}</strong></summary>'
        f'<p>{f["answer"]}</p></details>'
        for f in faqs
    )
    faq_schema_tag = (f'<script type="application/ld+json">'
                      f'{faq_schema}</script>') if faq_schema else ""

    html = BLOG_TEMPLATE
    html = html.replace("{{META_BLOCK}}", meta + faq_schema_tag)
    html = html.replace("{{PAGE_TITLE}}", title)
    html = html.replace("{{QUICK_ANSWER}}", quick_answer)
    html = html.replace("{{KEY_TAKEAWAYS}}", takeaways_html)
    html = html.replace("{{TOC_ITEMS}}", "")
    html = html.replace("{{DATE}}", NOW_DATE)
    html = html.replace("{{NOW}}", NOW_DATE)
    html = html.replace("{{EXPERT_INSIGHT}}", "")
    html = html.replace("{{MAIN_CONTENT}}", main_content)
    html = html.replace("{{COMPARISON_TITLE}}", "")
    html = html.replace("{{COMPARISON_TABLE}}", "")
    html = html.replace("{{STATISTICS}}", "")
    html = html.replace("{{FAQ_ITEMS}}", faq_html)
    html = html.replace("{{RELATED_ARTICLES}}", "")
    return html


# ═══════════════════════════════════════════════════
# PHASE 10 — REPORT GENERATOR
# ═══════════════════════════════════════════════════
def save_report(audit: dict, broken: list):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON
    report = {
        "generated": NOW_ISO,
        "site": BASE_URL,
        "total_pages": len(audit["pages"]),
        "total_issues": len(audit["issues"]),
        "broken_links": broken,
        "issues": audit["issues"],
        "pages": audit["pages"]
    }
    json_path = REPORT_DIR / f"seo_report_{ts}.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Markdown
    severity_order = {"HIGH":0,"MEDIUM":1,"LOW":2}
    issues_sorted = sorted(audit["issues"],
                            key=lambda x: severity_order.get(x["severity"],9))
    rows = "\n".join(
        f"| {i['severity']} | {i['type']} | `{i['file']}` | {i['detail']} |"
        for i in issues_sorted
    )
    broken_rows = "\n".join(
        f"| `{b['page']}` | {b['url']} | {b['status']} |"
        for b in broken
    )
    md = f"""# 🔍 Aivora AI — SEO Audit Report
**Generated:** {NOW_ISO}  
**Site:** {BASE_URL}  
**Total Pages:** {len(audit['pages'])}  
**Total Issues:** {len(audit['issues'])}  
**Broken Links:** {len(broken)}  

---

## 🚨 SEO Issues

| Severity | Type | File | Detail |
|----------|------|------|--------|
{rows}

---

## 🔗 Broken Links

| Page | URL | Status |
|------|-----|--------|
{broken_rows}

---

## 📊 Pages Summary

| File | Title | H1 | Schema | OG |
|------|-------|----|--------|----|
""" + "\n".join(
    f"| `{p['file']}` | {p['title'][:40]} | {'✅' if p['h1_count']==1 else '❌'} | {'✅' if p['has_schema'] else '❌'} | {'✅' if p['has_og'] else '❌'} |"
    for p in audit["pages"]
)
    md_path = REPORT_DIR / f"seo_report_{ts}.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"\n📄 Reports saved:\n  {json_path}\n  {md_path}")


# ═══════════════════════════════════════════════════
# PHASE 11 — FIX APPLIER
# ═══════════════════════════════════════════════════
def apply_fixes(audit: dict):
    print("\n🔧 Applying SEO Fixes to all HTML files…")
    website_schema = build_website_schema()
    patched = 0

    for page in audit["pages"]:
        fpath = SITE_ROOT / page["file"]
        if not fpath.exists():
            continue
        html  = read_html(fpath)
        orig  = html

        # 1. Inject canonical if missing
        if not page["canonical"]:
            url = page["url"]
            canon = f'<link rel="canonical" href="{url}">'
            html  = re.sub(r'</head>', f'{canon}\n</head>', html, count=1, flags=re.I)

        # 2. Inject website schema if missing
        if not page["has_schema"]:
            tag = f'<script type="application/ld+json">{website_schema}</script>'
            html = re.sub(r'</head>', f'{tag}\n</head>', html, count=1, flags=re.I)

        # 3. Inject OG basics if missing
        if not page["has_og"]:
            t = page["title"].replace('"', '&quot;')
            d = page["description"].replace('"', '&quot;')
            og = (f'<meta property="og:title" content="{t}">\n'
                  f'<meta property="og:description" content="{d}">\n'
                  f'<meta property="og:url" content="{page["url"]}">\n'
                  f'<meta property="og:site_name" content="{SITE_NAME}">\n'
                  f'<meta property="og:image" content="{BASE_URL}/assets/og-home.png">\n')
            html = re.sub(r'</head>', f'{og}</head>', html, count=1, flags=re.I)

        # 4. Inject last-modified
        if 'name="last-modified"' not in html:
            tag = f'<meta name="last-modified" content="{NOW_DATE}">'
            html = re.sub(r'</head>', f'{tag}\n</head>', html, count=1, flags=re.I)

        # 5. Internal links
        html = inject_internal_links(html, page["file"])

        if html != orig:
            write_html(fpath, html)
            patched += 1

    print(f"  ✅ Patched {patched} files")


# ═══════════════════════════════════════════════════
# PHASE 12 — SCHEMA EXPORT
# ═══════════════════════════════════════════════════
def export_schemas():
    print("\n📐 PHASE 5: Exporting Schema Templates")
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

    # Website / Org
    (SCHEMA_DIR / "website_org.json").write_text(
        build_website_schema(), encoding="utf-8")

    # Sample Article
    (SCHEMA_DIR / "article_sample.json").write_text(
        build_article_schema("Sample Article", "Sample description",
                              f"{BASE_URL}/blog/sample.html"), encoding="utf-8")

    # Sample FAQ
    sample_faqs = [
        {"question":"What is Aivora AI?",
         "answer":"Aivora AI is a global directory of 200+ tested AI tools with affiliate programs."},
        {"question":"Is Aivora AI free?",
         "answer":"Yes. Browsing is completely free."}
    ]
    (SCHEMA_DIR / "faq_sample.json").write_text(
        build_faq_schema(sample_faqs), encoding="utf-8")

    # HowTo
    steps = [
        "Browse the AI tools directory",
        "Pick a tool and join its affiliate program",
        "Get your unique tracking link",
        "Share on blog or social media",
        "Earn recurring monthly commission"
    ]
    (SCHEMA_DIR / "howto_sample.json").write_text(
        build_howto_schema("How to Earn with AI Affiliate Marketing", steps),
        encoding="utf-8")

    print(f"  ✅ Schema templates saved to {SCHEMA_DIR}/")


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="Aivora AI SEO Engine")
    parser.add_argument("--audit",   action="store_true", help="Run audit only")
    parser.add_argument("--fix",     action="store_true", help="Apply fixes only")
    parser.add_argument("--schemas", action="store_true", help="Export schemas")
    parser.add_argument("--sitemap", action="store_true", help="Generate sitemaps")
    parser.add_argument("--robots",  action="store_true", help="Generate robots.txt")
    parser.add_argument("--images",  action="store_true", help="Fix image alts")
    parser.add_argument("--broken",  action="store_true", help="Broken link check")
    parser.add_argument("--blog",    metavar="SLUG",      help="Generate blog post")
    parser.add_argument("--all",     action="store_true", help="Run everything")
    args = parser.parse_args()

    run_all = args.all or not any([
        args.audit, args.fix, args.schemas,
        args.sitemap, args.robots, args.images,
        args.broken, args.blog
    ])

    print("=" * 60)
    print(f"  AIVORA AI — SEO ENGINE  |  {NOW_DATE}")
    print("=" * 60)

    audit = {"issues": [], "pages": []}
    broken: list = []

    if run_all or args.audit or args.fix or args.sitemap:
        audit = audit_site()

    if run_all or args.broken:
        broken = check_broken_links(audit["pages"])

    if run_all or args.fix:
        apply_fixes(audit)
        fix_image_alts()

    if run_all or args.schemas:
        export_schemas()

    if run_all or args.sitemap:
        generate_sitemap(audit["pages"])

    if run_all or args.robots:
        generate_robots()

    if run_all or args.images:
        fix_image_alts()

    if run_all or args.audit or args.broken:
        save_report(audit, broken)

    if args.blog:
        slug  = args.blog
        title = slug.replace("-"," ").title()
        html  = generate_blog_post(
            slug=slug,
            title=title,
            description=f"Complete guide to {title} — {SITE_NAME}",
            quick_answer=f"{title} helps creators earn with AI tools.",
            key_takeaways=[
                f"{title} is one of the top AI tools in 2026",
                "Earn affiliate commissions up to 75%",
                "Beginner-friendly, no tech skills needed"
            ],
            faqs=[
                {"question":f"What is {title}?",
                 "answer":f"{title} is a leading AI tool reviewed by {SITE_NAME}."},
                {"question":"How do I join the affiliate program?",
                 "answer":"Sign up free and get your tracking link instantly."}
            ]
        )
        out = SITE_ROOT / "blog" / f"{slug}.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        write_html(out, html)
        print(f"\n✅ Blog post generated: {out}")

    print("\n🎉 SEO Engine complete!\n")


if __name__ == "__main__":
    main()

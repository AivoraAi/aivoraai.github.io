/**
 * generate-sitemap.js
 * Scans all .html files in the repo and writes sitemap.xml
 * Run: node scripts/generate-sitemap.js
 */

const fs   = require('fs');
const path = require('path');

const BASE_URL    = 'https://aivoraai.github.io';
const ROOT        = path.resolve(__dirname, '..');
const OUTPUT_FILE = path.join(ROOT, 'sitemap.xml');

// Pages to exclude from sitemap
const EXCLUDE = new Set([
  'google7061fb8c95f025f1.html',
  '404.html',
]);

// Priority rules: path pattern → priority + changefreq
const RULES = [
  { test: p => p === 'index.html',        priority: '1.0', changefreq: 'daily'   },
  { test: p => p === 'blog.html',         priority: '0.9', changefreq: 'daily'   },
  { test: p => p === 'product.html',      priority: '0.9', changefreq: 'weekly'  },
  { test: p => p.startsWith('blog/'),     priority: '0.8', changefreq: 'monthly' },
  { test: () => true,                     priority: '0.6', changefreq: 'monthly' },
];

function getRule(relPath) {
  return RULES.find(r => r.test(relPath));
}

function toUrl(relPath) {
  // index.html → base url
  if (relPath === 'index.html') return BASE_URL + '/';
  return `${BASE_URL}/${relPath}`;
}

function getLastMod(absPath) {
  try {
    const stat = fs.statSync(absPath);
    return stat.mtime.toISOString().split('T')[0];
  } catch {
    return new Date().toISOString().split('T')[0];
  }
}

function walkHtml(dir, base = '') {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const urls = [];

  for (const entry of entries) {
    const abs = path.join(dir, entry.name);
    const rel = base ? `${base}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      // Skip hidden dirs and node_modules
      if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
        urls.push(...walkHtml(abs, rel));
      }
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      if (!EXCLUDE.has(rel)) {
        urls.push({ rel, abs });
      }
    }
  }

  return urls;
}

// ── Main ─────────────────────────────────────────────────────────────────────

const pages  = walkHtml(ROOT);
const today  = new Date().toISOString().split('T')[0];

const urlNodes = pages.map(({ rel, abs }) => {
  const rule    = getRule(rel);
  const lastmod = getLastMod(abs);
  return `  <url>
    <loc>${toUrl(rel)}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>${rule.changefreq}</changefreq>
    <priority>${rule.priority}</priority>
  </url>`;
}).join('\n');

const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset
  xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
    http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
${urlNodes}
</urlset>
`;

fs.writeFileSync(OUTPUT_FILE, xml, 'utf8');
console.log(`✅ sitemap.xml written — ${pages.length} URLs`);

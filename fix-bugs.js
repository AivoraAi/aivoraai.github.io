/**
 * fix-bugs.js
 * Fixes known HTML bugs across the site automatically on every push.
 *
 * Current fixes applied:
 *  1. Double style=" in bimg divs  (e.g.  style="style="...)
 *  2. Counter elements that display "0" — replaced with real counts from blogs.json
 *  3. Duplicate <link rel="icon"> tags
 *  4. Missing alt attributes on <img> tags with known src patterns
 *  5. Trailing whitespace in <title> tags
 */

const fs   = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');

// ─── Helper: load and save a file ────────────────────────────────────────────
function patch(filePath, fn) {
  if (!fs.existsSync(filePath)) return;
  const original = fs.readFileSync(filePath, 'utf8');
  const patched  = fn(original);
  if (patched !== original) {
    fs.writeFileSync(filePath, patched, 'utf8');
    console.log(`✅ Patched: ${path.relative(ROOT, filePath)}`);
  }
}

// ─── Fix 1: double style attribute  style="style="..." → style="..." ─────────
function fixDoubleStyle(html) {
  return html.replace(/style="style="([^"]+)"/g, 'style="$1"');
}

// ─── Fix 2: stat counters showing 0 ──────────────────────────────────────────
function fixCounters(html, count) {
  // Pattern: <span ...>0</span> near words like "tools reviewed", "reviews"
  html = html.replace(
    /(<[^>]*id=["']?stat-tools["']?[^>]*>)\s*0\s*(<\/[^>]+>)/gi,
    `$1${count}$2`
  );
  html = html.replace(
    /(<[^>]*id=["']?stat-reviews["']?[^>]*>)\s*0\s*(<\/[^>]+>)/gi,
    `$1${count}$2`
  );
  return html;
}

// ─── Fix 3: duplicate <link rel="icon"> — keep only first ────────────────────
function fixDuplicateIcons(html) {
  let count = 0;
  return html.replace(/<link\s+rel="icon"[^>]+>/gi, match => {
    count++;
    return count === 1 ? match : '';
  });
}

// ─── Fix 4: <img> missing alt attribute ──────────────────────────────────────
function fixMissingAlts(html) {
  // Add alt="" only if completely missing (not alt="...")
  return html.replace(/<img(?![^>]*\balt=)([^>]*)>/gi, '<img alt=""$1>');
}

// ─── Fix 5: trim whitespace in <title> ───────────────────────────────────────
function fixTitleWhitespace(html) {
  return html.replace(/<title>\s+/g, '<title>').replace(/\s+<\/title>/g, '</title>');
}

// ─── Get blog count ───────────────────────────────────────────────────────────
let blogCount = 244; // fallback
const dataFile = path.join(ROOT, 'scripts', 'blogs.json');
if (fs.existsSync(dataFile)) {
  try {
    blogCount = JSON.parse(fs.readFileSync(dataFile, 'utf8')).length;
  } catch {}
}

// ─── Apply fixes to all HTML files ───────────────────────────────────────────
function walk(dir) {
  fs.readdirSync(dir, { withFileTypes: true }).forEach(entry => {
    const abs = path.join(dir, entry.name);
    if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
      walk(abs);
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      patch(abs, html => {
        html = fixDoubleStyle(html);
        html = fixCounters(html, blogCount);
        html = fixDuplicateIcons(html);
        html = fixMissingAlts(html);
        html = fixTitleWhitespace(html);
        return html;
      });
    }
  });
}

walk(ROOT);
console.log('✅ Bug fixes complete');

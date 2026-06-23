/**
 * generate-blog.js
 * Reads blogs.json → renders blog cards → injects them into blog.html
 *
 * blog.html must contain exactly ONE pair of these markers:
 *   <!-- BLOG_CARDS_START -->
 *   <!-- BLOG_CARDS_END -->
 * Everything between them is replaced on each run.
 */

const fs   = require('fs');
const path = require('path');

const ROOT      = path.resolve(__dirname, '..');
const DATA_FILE = path.join(ROOT, 'scripts', 'blogs.json');
const HTML_FILE = path.join(ROOT, 'blog.html');

const START_MARKER = '<!-- BLOG_CARDS_START -->';
const END_MARKER   = '<!-- BLOG_CARDS_END -->';

// ── Category colour map ───────────────────────────────────────────────────────
const CAT_COLORS = {
  'affiliate':   'c-go',
  'review':      'c-pu',
  'income':      'c-go',
  'seo':         'c-em',
  'guide':       'c-bl',
  'video':       'c-ro',
  'trading':     'c-bl',
  'tools':       'c-em',
  'new':         'c-bl',
  'default':     'c-bl',
};

function catColor(tag) {
  const t = (tag || '').toLowerCase();
  return CAT_COLORS[t] || CAT_COLORS.default;
}

// ── Gradient palette cycling ──────────────────────────────────────────────────
const GRADIENTS = [
  'linear-gradient(135deg,#0a1628,#1a2744)',
  'linear-gradient(135deg,#1a0b2e,#2d1b4e)',
  'linear-gradient(135deg,#064e3b,#047857)',
  'linear-gradient(135deg,#1a1000,#382200)',
  'linear-gradient(135deg,#001a33,#004d99)',
  'linear-gradient(135deg,#1a0010,#3d0022)',
  'linear-gradient(135deg,#4c1d95,#7c3aed)',
];

const ICON_STROKES = ['#60a5fa','#a78bfa','#34d399','#fbbf24','#22d3ee','#f472b6','#c4b5fd'];

function cardGradient(index) {
  return GRADIENTS[index % GRADIENTS.length];
}
function iconColor(index) {
  return ICON_STROKES[index % ICON_STROKES.length];
}

// ── SVG icon generator (generic document icon) ───────────────────────────────
function svgIcon(color) {
  return `<svg style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:80px;height:80px;opacity:0.1;" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="1.5">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>`;
}

// ── Badge HTML ────────────────────────────────────────────────────────────────
function badgeHtml(badge) {
  if (!badge) return '';
  const map = {
    'NEW':     '<span class="bnew">NEW</span>',
    'HOT':     '<span class="bhot">HOT</span>',
    'UPDATED': '<span class="bupdated">UPDATED</span>',
  };
  return map[badge.toUpperCase()] || '';
}

// ── Render a single card ──────────────────────────────────────────────────────
function renderCard(post, index) {
  const delay   = (index % 8) + 1;
  const grad    = cardGradient(index);
  const icon    = post.emoji
    ? `<span style="font-size:2.5rem;position:relative;z-index:1;">${post.emoji}</span>`
    : svgIcon(iconColor(index));
  const badge   = badgeHtml(post.badge || 'NEW');
  const tagHtml = post.tag
    ? `<span class="btag">${post.tag}</span>`
    : '';
  const cc      = catColor(post.category);
  const cats    = (post.cats || []).join(' ');

  return `<a href="${post.url}" class="bc delay-${delay}" data-cats="${cats}">
  <div class="bimg" style="background:${grad};position:relative;overflow:hidden;">
    ${icon}
    ${badge}
    ${tagHtml}
  </div>
  <div class="bbody">
    <span class="bcat ${cc}">${post.category || 'AI Tools'}</span>
    <h3>${post.title}</h3>
    <p>${post.excerpt}</p>
    <div class="bfoot">
      <span>${post.date}</span>
      <span class="bread">Read →</span>
    </div>
  </div>
</a>`;
}

// ── Main ──────────────────────────────────────────────────────────────────────
if (!fs.existsSync(DATA_FILE)) {
  console.warn('⚠️  blogs.json not found — skipping blog card generation.');
  process.exit(0);
}

const posts    = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
const cards    = posts.map((post, i) => renderCard(post, i)).join('\n\n');
const injected = `${START_MARKER}\n${cards}\n${END_MARKER}`;

let html = fs.readFileSync(HTML_FILE, 'utf8');

const startIdx = html.indexOf(START_MARKER);
const endIdx   = html.indexOf(END_MARKER);

if (startIdx === -1 || endIdx === -1) {
  // Markers not yet in file — append before closing </main>
  html = html.replace('</main>', `${injected}\n</main>`);
  console.log('ℹ️  Markers not found — appended cards before </main>');
} else {
  html = html.slice(0, startIdx) + injected + html.slice(endIdx + END_MARKER.length);
  console.log('✅ Blog cards injected between markers');
}

// Update total article count in header chips
const total = posts.length;
html = html.replace(
  /(\d+)\+?\s*Articles/,
  `${total}+ Articles`
);
html = html.replace(
  /(\d+)\+\s*AI Guides/,
  `${total}+ AI Guides`
);

fs.writeFileSync(HTML_FILE, html, 'utf8');
console.log(`✅ blog.html updated — ${total} cards rendered`);

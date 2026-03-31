/* ==============================================
   AIVORA – script.js
   Handles: navbar scroll, mobile menu,
   category filters, search, newsletter toast
   ============================================== */

// ── Navbar scroll effect ──
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 30);
  });
}

// ── Mobile hamburger menu ──
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    // Animate hamburger → X
    const spans = hamburger.querySelectorAll('span');
    hamburger.classList.toggle('active');
    if (hamburger.classList.contains('active')) {
      spans[0].style.cssText = 'transform:translateY(7px) rotate(45deg)';
      spans[1].style.cssText = 'opacity:0';
      spans[2].style.cssText = 'transform:translateY(-7px) rotate(-45deg)';
    } else {
      spans.forEach(s => s.style.cssText = '');
    }
  });
  // Close on nav link click
  navLinks.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      hamburger.classList.remove('active');
      hamburger.querySelectorAll('span').forEach(s => s.style.cssText = '');
    });
  });
}

// ── Category filter (products grid) ──
function initFilters(filterSelector, gridSelector, dataAttr) {
  const buttons = document.querySelectorAll(filterSelector);
  const cards   = document.querySelectorAll(gridSelector);
  if (!buttons.length || !cards.length) return;

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter || 'all';

      cards.forEach((card, i) => {
        const cats = card.dataset.category || '';
        const show = filter === 'all' || cats.includes(filter);
        card.style.display = show ? '' : 'none';
        if (show) {
          // stagger-animate visible cards
          card.style.animation = 'none';
          card.offsetHeight; // reflow
          card.style.animation = `fadeInCard 0.4s ${i * 0.06}s ease both`;
        }
      });
    });
  });
}

// Products grid filters
initFilters('#filterBar .filter-btn', '#productsGrid .product-card', 'data-category');

// Hero chip filters (mirror products grid)
document.querySelectorAll('.hero-filters .filter-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.hero-filters .filter-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    // Sync with filter bar and trigger
    const filter = chip.dataset.filter;
    const matchBtn = document.querySelector(`#filterBar [data-filter="${filter}"]`);
    if (matchBtn) {
      matchBtn.click();
      // Smooth scroll to products section
      const section = document.getElementById('tools');
      if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── Search functionality ──
function handleSearch() {
  const query = (document.getElementById('heroSearch')?.value || '').toLowerCase().trim();
  const cards  = document.querySelectorAll('#productsGrid .product-card');

  if (!query) {
    cards.forEach(c => c.style.display = '');
    return;
  }

  cards.forEach(card => {
    const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
    const desc  = card.querySelector('.card-desc')?.textContent.toLowerCase() || '';
    const cat   = card.querySelector('.tag-cat')?.textContent.toLowerCase() || '';
    const match = title.includes(query) || desc.includes(query) || cat.includes(query);
    card.style.display = match ? '' : 'none';
  });

  // Scroll to products section
  const section = document.getElementById('tools');
  if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Trigger search on Enter key
const heroInput = document.getElementById('heroSearch');
if (heroInput) {
  heroInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') handleSearch();
  });
}

// ── Toast notification ──
function showToast(message, duration = 3000) {
  let toast = document.getElementById('globalToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'globalToast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Newsletter signup ──
function handleNewsletter(e) {
  if (e) e.preventDefault();
  const input = e?.target?.querySelector('input[type="email"]');
  if (input?.value) {
    showToast('🎉 You\'re subscribed! Check your inbox soon.');
    input.value = '';
  }
}

// Also handle all newsletter forms on the page
document.querySelectorAll('.nl-form').forEach(form => {
  form.addEventListener('submit', handleNewsletter);
});

// ── Contact form ──
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', e => {
    e.preventDefault();
    const btn = contactForm.querySelector('button[type="submit"]');
    const original = btn.textContent;
    btn.textContent = 'Sending…';
    btn.disabled = true;
    setTimeout(() => {
      showToast('✅ Message sent! We\'ll be in touch within 24 hours.');
      contactForm.reset();
      btn.textContent = original;
      btn.disabled = false;
    }, 1200);
  });
}

// ── Intersection Observer – fade-in on scroll ──
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -40px 0px'
};
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll(
  '.product-card, .service-card, .testi-card, .blog-card, .about-stat-box'
).forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(24px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// CSS class to trigger the transition
const style = document.createElement('style');
style.textContent = `.in-view { opacity: 1 !important; transform: translateY(0) !important; }`;
document.head.appendChild(style);

// ── Active nav link based on scroll ──
const sections  = document.querySelectorAll('section[id]');
const navAnchors = document.querySelectorAll('.nav-link');
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY + 100;
  sections.forEach(sec => {
    if (scrollY >= sec.offsetTop && scrollY < sec.offsetTop + sec.offsetHeight) {
      navAnchors.forEach(a => {
        a.classList.toggle('active', a.getAttribute('href') === `#${sec.id}` || a.getAttribute('href') === `index.html#${sec.id}`);
      });
    }
  });
}, { passive: true });

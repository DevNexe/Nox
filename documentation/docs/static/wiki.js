document.addEventListener("click", (e) => {
  const btn = e.target.closest(".copy");
  if (!btn) return;
  const block = btn.closest(".codeblock");
  if (!block) return;
  const code = block.querySelector("code");
  if (!code) return;
  const text = code.textContent || "";
  navigator.clipboard.writeText(text).then(() => {
    const old = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(() => (btn.textContent = old), 800);
  });
});

function markActiveNav(pathname) {
  // First, clear all active states on sections and links
  document.querySelectorAll(".nav-section.active").forEach((section) => {
    section.classList.remove("active");
  });
  document.querySelectorAll(".nav a.active").forEach((la) => {
    la.classList.remove("active");
  });
  // Then mark the matching link and its parent section
  document.querySelectorAll(".nav a").forEach((a) => {
    const href = a.getAttribute("href");
    if (!href) return;
    const pathOnly = href.split("?")[0].split("#")[0];
    if (pathOnly === pathname) {
      a.classList.add("active");
      const section = a.closest(".nav-section");
      if (section) {
        section.classList.add("active");
      }
    }
  });
}

markActiveNav(window.location.pathname);

// --- Documentation search (client-side index + simple substring matching)
(() => {
  let docsSearchIndex = null;

  async function buildSearchIndex() {
    if (docsSearchIndex) return docsSearchIndex;
    const links = Array.from(document.querySelectorAll('.nav a'))
      .map((a) => a.getAttribute('href'))
      .filter(Boolean);
    const unique = [...new Set(links)];
    const entries = [];
    for (const href of unique) {
      if (!href || href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('#')) continue;
      try {
        const res = await fetch(href, { credentials: 'same-origin' });
        if (!res.ok) continue;
        const text = await res.text();
        const doc = new DOMParser().parseFromString(text, 'text/html');
        const title = doc.querySelector('title')?.textContent || href;
        const content = (doc.getElementById('page-content')?.textContent || doc.body.textContent || '').replace(/\s+/g, ' ');
        entries.push({ href, title, content });
      } catch (e) {
        // ignore fetch errors for specific pages
      }
    }
    docsSearchIndex = entries;
    return docsSearchIndex;
  }

  function escapeHtml(s) {
    return (s || '').replace(/[&<>\"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  const input = document.getElementById('docs-search-top');
  const resultsEl = document.getElementById('search-popup');
  if (!input || !resultsEl) return;
  let debounce = null;

  input.addEventListener('input', (e) => {
    const q = (input.value || '').trim().toLowerCase();
    clearTimeout(debounce);
    debounce = setTimeout(async () => {
      if (!q || q.length < 2) {
        resultsEl.hidden = true;
        resultsEl.innerHTML = '';
        return;
      }
      resultsEl.hidden = false;
      const params = new URLSearchParams(window.location.search);
      const lang = params.get('lang') || localStorage.getItem('nox_lang') || 'en';
      const loadingText = lang === 'ru' ? 'Поиск…' : 'Searching…';
      resultsEl.innerHTML = `<div class="search-loading">${loadingText}</div>`;
      const idx = await buildSearchIndex();
      const matches = idx
        .map((entry) => {
          const t = (entry.title || '').toLowerCase();
          const c = (entry.content || '').toLowerCase();
          let score = 0;
          if (t.includes(q)) score += 30;
          const pos = c.indexOf(q);
          if (pos >= 0) score += Math.max(10, 20 - Math.floor(pos / 100));
          return { entry, score, pos };
        })
        .filter((m) => m.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 20);

      if (matches.length === 0) {
        const params = new URLSearchParams(window.location.search);
        const lang = params.get('lang') || localStorage.getItem('nox_lang') || 'en';
        const noResultsText = lang === 'ru' ? 'Нет результатов' : 'No results';
        resultsEl.innerHTML = `<div class="search-none">${noResultsText}</div>`;
        return;
      }

      resultsEl.innerHTML = matches
        .map((m) => {
          const e = m.entry;
          const pos = (e.content || '').toLowerCase().indexOf(q);
          const snippet = pos >= 0 ? ('...' + (e.content || '').substr(Math.max(0, pos - 60), 160) + '...') : '';
          return `<a class="search-item" href="${e.href}"><div class="search-title">${escapeHtml(e.title)}</div><div class="search-snippet">${escapeHtml(snippet)}</div></a>`;
        })
        .join('');

      attachLangToLinks(resultsEl);
    }, 180);
  });

  // Hide results when clicking outside
  document.addEventListener('click', (ev) => {
    if (ev.target.closest && (ev.target.closest('#docs-search-top') || ev.target.closest('#search-popup'))) return;
    resultsEl.hidden = true;
  });
})();

// Navigation section toggle - using event delegation
document.addEventListener("click", (e) => {
  const toggle = e.target.closest(".nav-toggle");
  if (!toggle) return;
  
  e.preventDefault();
  e.stopImmediatePropagation();
  
  const section = toggle.closest(".nav-section");
  const group = section.closest(".nav-section-group");
  const items = group.querySelector(".nav-items");
  
  if (!items) return;
  
  items.classList.toggle("open");
  toggle.classList.toggle("is-open");
  // if opening this group, close others (exclusive open)
  if (items.classList.contains('open')) {
    document.querySelectorAll('.nav-section-group').forEach((g) => {
      const otherItems = g.querySelector('.nav-items');
      const otherToggle = g.querySelector('.nav-toggle');
      if (otherItems && otherItems !== items) otherItems.classList.remove('open');
      if (otherToggle && otherToggle !== toggle) otherToggle.classList.remove('is-open');
    });
  }
  // persist open state
  try { saveNavState(); } catch (e) {}
}, false);

// Initialize open state for active items on full page load
document.addEventListener("DOMContentLoaded", () => {
  try { initNavToggles(); } catch (e) {}
  try { updateLangButtons(); } catch (e) {}
});

// Re-initialize for dynamically loaded content
function initNavToggles() {
  // Restore saved open groups, then ensure active group is opened
  try { restoreNavState(); } catch (e) {}
  document.querySelectorAll(".nav-items").forEach((items) => {
    const hasActive = items.querySelector(".nav-section.active");
    if (hasActive) {
      items.classList.add("open");
      const toggle = items.closest(".nav-section-group").querySelector(".nav-toggle");
      if (toggle) toggle.classList.add("is-open");
    }
  });
}

// Sidebar toggle - mobile and desktop
(() => {
  const btn = document.getElementById("sidebar-toggle");
  const sidebar = document.querySelector(".sidebar");
  const layout = document.querySelector(".layout");
  const topbarBurger = document.getElementById("topbar-burger");
  if (!sidebar) return;

  // Check if mobile (only on mobile, use sidebar toggle for menu)
  const isMobile = () => window.innerWidth <= 767;

  if (btn) {
    btn.addEventListener("click", () => {
      if (!isMobile()) {
        // Desktop compact mode
        layout.classList.toggle("compact");
        localStorage.setItem("sidebar-compact", layout.classList.contains("compact") ? "1" : "0");
      }
    });
  }

  if (topbarBurger) {
    topbarBurger.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      document.documentElement.classList.toggle("sidebar-open", sidebar.classList.contains("open"));
    });
  }

  // Close sidebar when clicking on a link (mobile)
  sidebar.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => {
      if (isMobile()) {
        sidebar.classList.remove("open");
        document.documentElement.classList.remove("sidebar-open");
      }
    });
  });

  // Close sidebar when clicking outside (mobile)
  document.addEventListener("click", (e) => {
    if (!isMobile()) return;
    if (e.target.closest(".sidebar") || e.target.closest(".topbar-burger")) return;
    sidebar.classList.remove("open");
    document.documentElement.classList.remove("sidebar-open");
  });

  // Restore compact state on desktop
  if (!isMobile()) {
    const saved = localStorage.getItem("sidebar-compact");
    if (saved === null || saved === "1") {
      layout.classList.add("compact");
    }
  }

  // Update on resize
  window.addEventListener("resize", () => {
    if (!isMobile()) {
      const saved = localStorage.getItem("sidebar-compact");
      if (saved === null || saved === "1") {
        layout.classList.add("compact");
      }
    }
  });
})();

// Language switcher
(() => {
  const wrap = document.getElementById("lang-switch");
  const trigger = document.getElementById("lang-trigger");
  const currentEl = document.getElementById("lang-current");
  const menu = document.getElementById("lang-menu");
  if (!wrap || !trigger || !currentEl || !menu) return;
  const params = new URLSearchParams(window.location.search);
  const stored = localStorage.getItem("nox_lang");
  const current = params.get("lang") || stored || "en";
  if (!params.get("lang") && stored) {
    params.set("lang", stored);
    window.location.search = params.toString();
    return;
  }
  if (!params.get("lang")) {
    params.set("lang", current);
    const url = window.location.pathname + "?" + params.toString();
    history.replaceState({}, "", url);
  }
  localStorage.setItem("nox_lang", current);
  currentEl.textContent = current.toUpperCase();
  menu.querySelectorAll(".lang-item").forEach((item) => {
    item.classList.toggle("active", item.getAttribute("data-lang") === current);
  });

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    wrap.classList.toggle("open");
    trigger.setAttribute("aria-expanded", wrap.classList.contains("open") ? "true" : "false");
  });

  menu.querySelectorAll(".lang-item").forEach((item) => {
    item.addEventListener("click", () => {
      const lang = item.getAttribute("data-lang");
      localStorage.setItem("nox_lang", lang);
      params.set("lang", lang);
      window.location.search = params.toString();
    });
  });

  document.addEventListener("click", () => {
    wrap.classList.remove("open");
    trigger.setAttribute("aria-expanded", "false");
  });
})();

// Keep lang param across internal links
(() => {
  const params = new URLSearchParams(window.location.search);
  const current = params.get("lang") || localStorage.getItem("nox_lang") || "en";
  document.querySelectorAll("a[href]").forEach((a) => {
    const href = a.getAttribute("href");
    if (!href) return;
    if (href.startsWith("http:") || href.startsWith("https:")) return;
    if (href.startsWith("#")) return;
    if (href.includes("lang=")) return;
    if (href.startsWith("mailto:")) return;
    if (href.startsWith("tel:")) return;
    const join = href.includes("?") ? "&" : "?";
    a.setAttribute("href", href + join + "lang=" + encodeURIComponent(current));
  });
})();

function updateLangButtons() {
  const wrap = document.getElementById("lang-switch");
  const currentEl = document.getElementById("lang-current");
  const menu = document.getElementById("lang-menu");
  if (!wrap || !currentEl || !menu) return;
  const params = new URLSearchParams(window.location.search);
  const current = params.get("lang") || localStorage.getItem("nox_lang") || "en";
  currentEl.textContent = current.toUpperCase();
  menu.querySelectorAll(".lang-item").forEach((item) => {
    item.classList.toggle("active", item.getAttribute("data-lang") === current);
  });
  // Localize search input placeholder and aria-label
  try {
    const searchInput = document.getElementById('docs-search-top');
    if (searchInput) {
      if (current === 'ru') {
        searchInput.placeholder = 'Поиск в документации...';
        searchInput.setAttribute('aria-label', 'Поиск в документации');
      } else {
        searchInput.placeholder = 'Search documentation...';
        searchInput.setAttribute('aria-label', 'Search documentation');
      }
    }
  } catch (e) {}
}

function attachLangToLinks(root) {
  const params = new URLSearchParams(window.location.search);
  const current = params.get("lang") || localStorage.getItem("nox_lang") || "en";
  root.querySelectorAll("a[href]").forEach((a) => {
    const href = a.getAttribute("href");
    if (!href) return;
    if (href.startsWith("http:") || href.startsWith("https:")) return;
    if (href.startsWith("#")) return;
    if (href.includes("lang=")) return;
    if (href.startsWith("mailto:")) return;
    if (href.startsWith("tel:")) return;
    const join = href.includes("?") ? "&" : "?";
    a.setAttribute("href", href + join + "lang=" + encodeURIComponent(current));
  });
}

// Helpers to persist which nav groups are open across PJAX swaps
function _getGroupId(group) {
  if (!group) return null;
  const a = group.querySelector('.nav-section > a');
  if (a) return a.getAttribute('href')?.split('?')[0].split('#')[0] || null;
  const title = group.querySelector('.nav-section-title');
  return title ? title.textContent.trim() : null;
}

function saveNavState() {
  try {
    const open = [];
    document.querySelectorAll('.nav-section-group').forEach((g) => {
      const items = g.querySelector('.nav-items');
      if (items && items.classList.contains('open')) {
        const id = _getGroupId(g);
        if (id) open.push(id);
      }
    });
    localStorage.setItem('nox_nav_open', JSON.stringify(open));
  } catch (e) {}
}

function restoreNavState() {
  try {
    const raw = localStorage.getItem('nox_nav_open');
    if (!raw) return;
    const open = JSON.parse(raw || '[]');
    document.querySelectorAll('.nav-section-group').forEach((g) => {
        const id = _getGroupId(g);
        const items = g.querySelector('.nav-items');
        const toggle = g.querySelector('.nav-toggle');
        if (!items) return;
        // Only restore open state for this group if it contains an active link
        const hasActiveLink = !!items.querySelector('a.active');
        if (id && open.includes(id) && hasActiveLink) {
          items.classList.add('open');
          if (toggle) toggle.classList.add('is-open');
        } else {
          items.classList.remove('open');
          if (toggle) toggle.classList.remove('is-open');
        }
    });
  } catch (e) {}
}

function swapPageFromHTML(html, url) {
  const doc = new DOMParser().parseFromString(html, "text/html");
  const nextNav = doc.getElementById("sidebar-nav");
  const nextContent = doc.getElementById("page-content");
  if (!nextNav || !nextContent) {
    window.location.href = url;
    return;
  }

  const nav = document.getElementById("sidebar-nav");
  const content = document.getElementById("page-content");
  if (!nav || !content) {
    window.location.href = url;
    return;
  }

  document.title = doc.title;
  nav.innerHTML = nextNav.innerHTML;
  content.innerHTML = nextContent.innerHTML;
  content.scrollTop = 0;

  attachLangToLinks(document);
  markActiveNav(new URL(url, window.location.origin).pathname);
  updateLangButtons();
  initNavToggles();
}

function smoothNavigate(url, push) {
  const content = document.getElementById("page-content");
  if (content) content.classList.add("is-loading");
  const finish = (html) => {
    const wait = content ? 200 : 0;
    setTimeout(() => {
      swapPageFromHTML(html, url);
      if (push) history.pushState({}, "", url);
      if (content) {
        requestAnimationFrame(() => {
          content.classList.remove("is-loading");
        });
      }
    }, wait);
  };

  fetch(url, { credentials: "same-origin" })
    .then((r) => (r.ok ? r.text() : Promise.reject(r.status)))
    .then(finish)
    .catch(() => {
      window.location.href = url;
    });
}

document.addEventListener("click", (e) => {
  // Skip if clicking on nav toggle
  if (e.target.closest(".nav-toggle")) return;
  
  const link = e.target.closest("a[href]");
  if (!link) return;
  if (link.target && link.target !== "_self") return;
  if (link.hasAttribute("download")) return;
  const href = link.getAttribute("href");
  if (!href) return;
  if (href.startsWith("http:") || href.startsWith("https:")) return;
  if (href.startsWith("#")) return;
  if (href.startsWith("mailto:") || href.startsWith("tel:")) return;

  // Note: opening/closing nav groups is handled only via the .nav-toggle click
  e.preventDefault();
  smoothNavigate(href, true);
});

window.addEventListener("popstate", () => {
  smoothNavigate(window.location.pathname + window.location.search, false);
});

// Theme toggle
(() => {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  const saved = localStorage.getItem("nox_theme") || "dark";
  if (saved === "light") {
    document.documentElement.setAttribute("data-theme", "light");
  }
  btn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
    const next = current === "light" ? "dark" : "light";
    if (next === "light") {
      document.documentElement.setAttribute("data-theme", "light");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
    localStorage.setItem("nox_theme", next);
  });
})();

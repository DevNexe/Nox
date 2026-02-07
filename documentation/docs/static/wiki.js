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
  document.querySelectorAll(".nav a").forEach((a) => {
    a.classList.remove("active");
    const href = a.getAttribute("href");
    if (!href) return;
    const pathOnly = href.split("?")[0].split("#")[0];
    if (pathOnly === pathname) {
      a.classList.add("active");
    }
  });
}

markActiveNav(window.location.pathname);

// Sidebar compact toggle
(() => {
  const btn = document.getElementById("sidebar-toggle");
  const layout = document.querySelector(".layout");
  if (!btn || !layout) return;
  const saved = localStorage.getItem("sidebar-compact");
  if (saved === null) {
    layout.classList.add("compact");
  } else if (saved === "1") {
    layout.classList.add("compact");
  }

  btn.addEventListener("click", () => {
    layout.classList.toggle("compact");
    localStorage.setItem("sidebar-compact", layout.classList.contains("compact") ? "1" : "0");
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
  const link = e.target.closest("a[href]");
  if (!link) return;
  if (link.target && link.target !== "_self") return;
  if (link.hasAttribute("download")) return;
  const href = link.getAttribute("href");
  if (!href) return;
  if (href.startsWith("http:") || href.startsWith("https:")) return;
  if (href.startsWith("#")) return;
  if (href.startsWith("mailto:") || href.startsWith("tel:")) return;
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

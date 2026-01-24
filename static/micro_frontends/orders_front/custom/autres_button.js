(function () {
  // ===== CONFIG =====
  const TARGET_URL = "/orders/export-excel";
  const ARIA_LABEL = "Exporter Excel";
  // ==================

  // Simple "export spreadsheet" icon (inline SVG, inherits color via currentColor)
  const EXCEL_SVG = `
    <svg xmlns="http://www.w3.org/2000/svg"
         viewBox="0 0 24 24"
         width="18" height="18"
         fill="none"
         stroke="currentColor"
         stroke-width="2"
         stroke-linecap="round"
         stroke-linejoin="round"
         aria-hidden="true"
         focusable="false">
      <!-- sheet -->
      <path d="M6 3h8l4 4v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
      <path d="M14 3v5h5"/>
      <!-- grid lines -->
      <path d="M7.5 11h7"/>
      <path d="M7.5 14h7"/>
      <path d="M7.5 17h4.5"/>
      <!-- export arrow (down) -->
      <path d="M19 11v6"/>
      <path d="M16.5 14.5 19 17l2.5-2.5"/>
      <path d="M14.5 20h9"/>
    </svg>
  `;

  function findAutresElement() {
    const candidates = document.querySelectorAll("button, a, [role='button'], div, span");
    for (const el of candidates) {
      const txt = (el.textContent || "").trim();
      if (txt === "Autres") return el;
    }
    return null;
  }

  function ensureButtonNextToAutres() {
    const autres = findAutresElement();
    if (!autres) return;

    const parent = autres.parentElement;
    if (!parent) return;

    // Avoid duplicates
    if (parent.querySelector('[data-lilium="autres-extra"]')) return;

    const cs = window.getComputedStyle(autres);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = autres.className || ""; // inherit same classes
    btn.setAttribute("data-lilium", "autres-extra");
    btn.setAttribute("aria-label", ARIA_LABEL);
    btn.setAttribute("title", ARIA_LABEL);

    // SVG icon only
    btn.innerHTML = EXCEL_SVG;

    // Make it align with the existing control
    btn.style.display = "inline-flex";
    btn.style.alignItems = "center";
    btn.style.justifyContent = "center";

    // Match spacing/typography as much as possible
    if (cs.padding) btn.style.padding = cs.padding;
    if (cs.fontSize) btn.style.fontSize = cs.fontSize;
    if (cs.lineHeight) btn.style.lineHeight = cs.lineHeight;
    if (cs.height && cs.height !== "auto") btn.style.height = cs.height;
    if (cs.borderRadius) btn.style.borderRadius = cs.borderRadius;

    // The top bar in your screenshot has no “gap”, so force a small separation
    btn.style.marginLeft = "8px";

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const qs = window.__orders_last_query__ || window.location.search || "";
      window.location.href = TARGET_URL + qs;
    });

    parent.insertBefore(btn, autres.nextSibling);
  }

  // React renders async; keep observing until "Autres" appears.
  const obs = new MutationObserver(() => ensureButtonNextToAutres());
  obs.observe(document.documentElement, { childList: true, subtree: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureButtonNextToAutres);
  } else {
    ensureButtonNextToAutres();
  }
})();

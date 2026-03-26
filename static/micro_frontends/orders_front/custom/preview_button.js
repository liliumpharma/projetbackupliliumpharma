(function () {
  // ===== CONFIG =====
  const TARGET_URL = "/orders/export/preview/";
  const ARIA_LABEL = "statistique des Commandes";
  // ==================

  // Static icon for preview
const PREVIEW_SVG = `
<img src="https://cdn-icons-png.flaticon.com/512/9646/9646351.png" alt="Preview Icon" width="32" height="32" aria-hidden="true" />
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
    if (parent.querySelector('[data-lilium="preview-extra"]')) return;

    // To place it NEXT to the Excel button, we look if the Excel button exists
    let insertBeforeEl = autres.nextSibling;
    
    // Check if the Excel button is already there, put this before or after it
    const excelBtn = parent.querySelector('[data-lilium="autres-extra"]');
    if (excelBtn) {
        insertBeforeEl = excelBtn.nextSibling;
    }

    const cs = window.getComputedStyle(autres);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = (autres.className || "").replace(/\bhidden\b/g, "").trim(); // inherit same classes but always visible
    btn.setAttribute("data-lilium", "preview-extra");
    btn.setAttribute("aria-label", ARIA_LABEL);
    btn.setAttribute("title", ARIA_LABEL);

    // SVG icon only
    btn.innerHTML = PREVIEW_SVG;

    // Make it align with the existing control
    btn.style.display = "inline-flex";
    btn.style.alignItems = "center";
    btn.style.justifyContent = "center";
    btn.style.cursor = "pointer";
    btn.style.verticalAlign = "middle";
    btn.style.position = "relative";

    // Move it up by 50% of its own height (centering tweak) 
    btn.style.top = "-15%";
    btn.style.transform = "translateY(15%)";


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
      // Open preview in a new tab instead of replacing the page so they don't lose the filtering view
      window.open(TARGET_URL + qs, "_blank");
    });

    parent.insertBefore(btn, insertBeforeEl);
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

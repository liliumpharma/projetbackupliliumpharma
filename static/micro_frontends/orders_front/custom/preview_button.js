(function () {
  // ===== CONFIG =====
  const TARGET_URL = "/orders/statistics/";
  const ARIA_LABEL = "statistique des Commandes";
  // ==================

  // Static icon for preview
const PREVIEW_SVG = `
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 508 508" aria-hidden="true">
  <circle style="fill:#0E0fFF;" cx="254" cy="254" r="254"></circle>
  <path style="fill:#E6E9EE;" d="M389.6,178v-7.6h-48.4v-52h-7.6v52h-60.4v-52h-7.6v52h-60.8v-52h-7.6v52h-55.6v7.6h55.6v60.4h-55.6v7.6h55.6v60.4h-55.6v7.6h55.6v52h7.6v-52h60.4v52h7.6v-52h60.4v52h7.6v-52h48.4v-7.6h-48V246h48.4v-7.6h-48.4V178H389.6z M204.8,178h60.4v60.4h-60.4V178z M204.8,306.8V246h60.4v60.4L204.8,306.8L204.8,306.8z M333.6,306.8h-60.4V246h60.4V306.8z M333.6,238.4h-60.4V178h60.4V238.4z"></path>
  <path style="fill:#FF7058;" d="M141.6,372.4c-0.8,0-1.6,0-2.8-0.4c-3.2-1.6-4.4-5.2-2.8-8.4l59.6-126.8c0.8-2,2.8-3.2,4.8-3.6c2-0.4,4,0.4,5.6,2l58,65.2l66.8-129.6c1.6-3.2,5.2-4.4,8.4-2.8c3.2,1.6,4.4,5.2,2.8,8.4l-70.8,138c-0.8,2-2.8,3.2-4.8,3.2c-2,0.4-4-0.4-5.6-2l-57.6-64.8l-55.6,118C146.4,371.2,144,372.4,141.6,372.4z"></path>
  <polygon style="fill:#4CDBC4;" points="141.6,366.4 141.6,118.4 118.4,118.4 118.4,389.6 389.6,389.6 389.6,366.4"></polygon>
  <circle style="fill:#FFD05B;" cx="202.4" cy="242.4" r="21.2"></circle>
  <circle style="fill:#FFD05B;" cx="265.6" cy="308" r="21.2"></circle>
  <circle style="fill:#FFD05B;" cx="336.4" cy="174" r="21.2"></circle>
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

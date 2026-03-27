// (function () {
//   // ===== CONFIG =====
//   const TARGET_URL = "/orders/export-excel";
//   const ARIA_LABEL = "Exporter Excel";
//   // ==================

//   // Simple "export spreadsheet" icon (inline SVG, inherits color via currentColor)
//   // Green Excel logo (inline SVG)
// const EXCEL_SVG = `
// <svg xmlns="http://www.w3.org/2000/svg"
//      viewBox="0 0 24 24"
//      width="30"
//      height="30"
//      aria-hidden="true"
//      focusable="false">
//   <!-- Background -->
//   <rect x="2" y="3" width="20" height="18" rx="2" ry="2" fill="#107C41"/>

//   <!-- Left darker strip -->
//   <rect x="2" y="3" width="6.5" height="18" fill="#0E6A38"/>

//   <!-- X letter -->
//   <path d="M6.5 9 L8.5 12 L6.5 15
//            M10.5 9 L8.5 12 L10.5 15"
//         stroke="#FFFFFF"
//         stroke-width="1.8"
//         stroke-linecap="round"
//         stroke-linejoin="round"/>

//   <!-- Sheet lines -->
//   <path d="M11.5 8h7M11.5 11h7M11.5 14h7M11.5 17h5"
//         stroke="#E6F4EA"
//         stroke-width="1.2"
//         stroke-linecap="round"/>
// </svg>
// `;


//   function findAutresElement() {
//     const candidates = document.querySelectorAll("button, a, [role='button'], div, span");
//     for (const el of candidates) {
//       const txt = (el.textContent || "").trim();
//       if (txt === "Autres") return el;
//     }
//     return null;
//   }

//   function ensureButtonNextToAutres() {
//     const autres = findAutresElement();
//     if (!autres) return;

//     const parent = autres.parentElement;
//     if (!parent) return;

//     // Avoid duplicates
//     if (parent.querySelector('[data-lilium="autres-extra"]')) return;

//     const cs = window.getComputedStyle(autres);

//     const btn = document.createElement("button");
//     btn.type = "button";
//     btn.className = autres.className || ""; // inherit same classes
//     btn.setAttribute("data-lilium", "autres-extra");
//     btn.setAttribute("aria-label", ARIA_LABEL);
//     btn.setAttribute("title", ARIA_LABEL);

//     // SVG icon only
//     btn.innerHTML = EXCEL_SVG;

//     // Make it align with the existing control
//     btn.style.display = "inline-flex";
//     btn.style.alignItems = "center";
//     btn.style.justifyContent = "center";
//     btn.style.cursor = "pointer";
//     // Keep it centered with neighboring controls
//     btn.style.verticalAlign = "middle";
//     btn.style.position = "relative";

//     // Move it up by 50% of its own height (centering tweak) 
//     btn.style.top = "-15%";
//     btn.style.transform = "translateY(15%)";


//     // Match spacing/typography as much as possible
//     if (cs.padding) btn.style.padding = cs.padding;
//     if (cs.fontSize) btn.style.fontSize = cs.fontSize;
//     if (cs.lineHeight) btn.style.lineHeight = cs.lineHeight;
//     if (cs.height && cs.height !== "auto") btn.style.height = cs.height;
//     if (cs.borderRadius) btn.style.borderRadius = cs.borderRadius;

//     // The top bar in your screenshot has no “gap”, so force a small separation
//     btn.style.marginLeft = "8px";

//     btn.addEventListener("click", (e) => {
//       e.preventDefault();
//       e.stopPropagation();
//       const qs = window.__orders_last_query__ || window.location.search || "";
//       window.location.href = TARGET_URL + qs;
//     });

//     parent.insertBefore(btn, autres.nextSibling);
//   }

//   // React renders async; keep observing until "Autres" appears.
//   const obs = new MutationObserver(() => ensureButtonNextToAutres());
//   obs.observe(document.documentElement, { childList: true, subtree: true });

//   if (document.readyState === "loading") {
//     document.addEventListener("DOMContentLoaded", ensureButtonNextToAutres);
//   } else {
//     ensureButtonNextToAutres();
//   }
// })();




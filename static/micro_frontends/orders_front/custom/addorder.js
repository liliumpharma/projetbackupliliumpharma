(function () {
  // ===== CONFIG =====
  const TARGET_URL = "/orders/addorder/"; 
  const BUTTON_TEXT = "Ajouter un bon";
  const ARIA_LABEL = "Ajouter un nouveau bon de commande";
  // ==================

  function findAutresElement() {
    const candidates = document.querySelectorAll("button, a, [role='button'], div, span");
    for (const el of candidates) {
      const txt = (el.textContent || "").trim();
      if (txt === "Autres") return el;
    }
    return null;
  }

  function ensureAddOrderButton() {
    const autres = findAutresElement();
    if (!autres) return;

    const parent = autres.parentElement;
    if (!parent) return;

    if (parent.querySelector('[data-lilium="add-order-btn"]')) return;

    let insertBeforeEl = autres.nextSibling;
    const previewBtn = parent.querySelector('[data-lilium="preview-extra"]');
    if (previewBtn) {
        insertBeforeEl = previewBtn.nextSibling;
    }

    const btn = document.createElement("button");
    btn.type = "button";
    btn.setAttribute("data-lilium", "add-order-btn");
    btn.setAttribute("aria-label", ARIA_LABEL);
    btn.setAttribute("title", ARIA_LABEL);
    btn.textContent = BUTTON_TEXT;

    // Use existing classes for base structure
    btn.className = (autres.className || "").replace(/\bhidden\b/g, "").trim();

    // ===== STABLE STYLING (No Jumping) =====
    Object.assign(btn.style, {
      backgroundColor: "#28a745",
      backgroundImage: "linear-gradient(180deg, #2ecc71 0%, #28a745 100%)",
      color: "white",
      fontWeight: "600",
      fontSize: "13px",
      border: "1px solid #218838",
      borderRadius: "6px",
      padding: "0 16px",
      height: "32px",                 // Fixed height to match filters
      marginLeft: "12px",
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
      transition: "background-color 0.2s", // Only transition color, not position
      
      // Alignment without transforms
      verticalAlign: "middle",
      position: "relative",
      marginTop: "12px",              // Increased from 16px to push it further down
      marginBottom: "0px"             // Manually push it down to match the row center
    });

    // Hover effects (Color only, no movement)
    btn.onmouseenter = () => {
      btn.style.backgroundColor = "#218838";
      btn.style.backgroundImage = "none";
    };
    
    btn.onmouseleave = () => {
      btn.style.backgroundColor = "#28a745";
      btn.style.backgroundImage = "linear-gradient(180deg, #2ecc71 0%, #28a745 100%)";
    };

    // Click effect (Scale only, no sliding)
    btn.onmousedown = () => {
      btn.style.transform = "scale(0.96)";
    };

    btn.onmouseup = () => {
      btn.style.transform = "scale(1)";
    };

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.href = TARGET_URL;
    });

    parent.insertBefore(btn, insertBeforeEl);
  }

  const obs = new MutationObserver(() => ensureAddOrderButton());
  obs.observe(document.documentElement, { childList: true, subtree: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureAddOrderButton);
  } else {
    ensureAddOrderButton();
  }
})();
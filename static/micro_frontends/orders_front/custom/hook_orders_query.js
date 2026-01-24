(function () {
  // Keep only the params that OrderSupervisor understands.
  const KEEP = [
    "min_date",
    "max_date",
    "produit",
    "status",
    "user",
    "keyword",
    "source",
    "client",
    "office",
    "attente",
    "flag",
  ];

  function storeQuery(url) {
    try {
      const u = new URL(url, window.location.origin);
      const out = new URLSearchParams();

      for (const k of KEEP) {
        const v = u.searchParams.get(k);
        if (v != null && String(v).trim() !== "") out.set(k, v);
      }

      // Store as "?a=b&c=d" or "".
      const qs = out.toString();
      window.__orders_last_query__ = qs ? "?" + qs : "";
    } catch (_) {
      // ignore
    }
  }

  // Hook fetch (if used)
  if (typeof window.fetch === "function") {
    const origFetch = window.fetch;
    window.fetch = function (input, init) {
      const url = typeof input === "string" ? input : (input && input.url) || "";
      if (url) storeQuery(url);
      return origFetch.apply(this, arguments);
    };
  }

  // Hook axios/XHR (very common in React apps)
  if (window.XMLHttpRequest && window.XMLHttpRequest.prototype) {
    const origOpen = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function (method, url) {
      if (url) storeQuery(url);
      return origOpen.apply(this, arguments);
    };
  }
})();

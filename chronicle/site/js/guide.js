/** Guide pages: table scroll hint + locale init. */
(function initGuidePage() {
  document.querySelectorAll(".guide-table-wrap").forEach((wrap) => {
    if (wrap.scrollWidth > wrap.clientWidth + 4) {
      wrap.setAttribute("data-scrollable", "true");
    }
  });

  document.querySelectorAll(".guide-etf-ticker, .guide-l2-jump-etfs").forEach((node) => {
    node.setAttribute("translate", "no");
  });

  if (globalThis.PLLocale) {
    globalThis.PLLocale.initGate(() => {
      if (typeof globalThis.refreshSocialDock === "function") {
        globalThis.refreshSocialDock();
      }
    });
  }
})();

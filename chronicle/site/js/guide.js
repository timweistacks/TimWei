/** Guide pages: locale init + shared horizontal scroll affordances. */
(function initGuidePage() {
  document.querySelectorAll(".guide-etf-ticker, .guide-l2-jump-etfs").forEach((node) => {
    node.setAttribute("translate", "no");
  });

  if (typeof globalThis.initHorizontalScrollAffordances === "function") {
    globalThis.initHorizontalScrollAffordances();
  }

  if (globalThis.PLLocale) {
    globalThis.PLLocale.initGate(() => {
      if (typeof globalThis.refreshSocialDock === "function") {
        globalThis.refreshSocialDock();
      }
      if (typeof globalThis.initHorizontalScrollAffordances === "function") {
        globalThis.initHorizontalScrollAffordances();
      }
    });
  }
})();

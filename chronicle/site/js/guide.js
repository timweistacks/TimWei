/** Guide pages: table scroll hint + locale init. */
(function initGuidePage() {
  document.querySelectorAll(".guide-table-wrap").forEach((wrap) => {
    if (wrap.scrollWidth > wrap.clientWidth + 4) {
      wrap.setAttribute("data-scrollable", "true");
    }
  });

  if (globalThis.PLLocale) {
    globalThis.PLLocale.initGate(() => {
      if (typeof globalThis.refreshSocialDock === "function") {
        globalThis.refreshSocialDock();
      }
    });
  }
})();

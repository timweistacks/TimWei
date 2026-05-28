(function initHorizontalScrollModule(global) {
  const MOBILE_MAX = 919;
  const SCROLL_PANEL_SELECTORS = [
    ".guide-l2-jump-track",
    ".guide-table-wrap",
    ".table-wrap",
    ".overview-pos-scroll",
    ".perf-metrics-table-wrap",
    ".portfolio-pos-shell",
    ".overview-table-card #overview-position-root > .overview-pos-scroll",
  ];

  function hintText() {
    if (global.PLLocale && typeof global.PLLocale.t === "function") {
      return global.PLLocale.t("ui.scroll_hint");
    }
    return "Swipe horizontally to see more columns";
  }

  function affordanceRoot(panel) {
    if (panel.matches(".guide-l2-jump-track")) {
      return panel.closest(".guide-l2-jump-nav") || panel;
    }
    if (panel.classList.contains("table-wrap") || panel.classList.contains("guide-table-wrap")) {
      return panel.closest(".card") || panel.parentElement || panel;
    }
    return panel.parentElement || panel;
  }

  function ensureHint(affordance, panel) {
    const anchor = panel.parentElement;
    const existing =
      (anchor && anchor.querySelector(":scope > .h-scroll-hint, :scope > .table-scroll-hint")) ||
      affordance.querySelector(".h-scroll-hint, .table-scroll-hint");
    if (existing) {
      existing.classList.add("h-scroll-hint");
      return existing;
    }
    const hint = document.createElement("p");
    hint.className = "h-scroll-hint table-scroll-hint";
    hint.setAttribute("aria-hidden", "true");
    hint.textContent = hintText();
    if (anchor) {
      anchor.insertBefore(hint, panel);
    } else {
      affordance.prepend(hint);
    }
    return hint;
  }

  function updateAffordance(affordance, panel) {
    const overflow = panel.scrollWidth > panel.clientWidth + 2;
    const mobile = global.innerWidth <= MOBILE_MAX;
    affordance.dataset.scrollable = overflow ? "true" : "false";
    affordance.dataset.scrollEnd =
      overflow && panel.scrollLeft + panel.clientWidth >= panel.scrollWidth - 2 ? "true" : "false";

    const hint = affordance.querySelector(".h-scroll-hint");
    if (hint) {
      hint.textContent = hintText();
      hint.hidden = !(overflow && mobile);
    }
  }

  function bindPanel(panel) {
    if (panel.dataset.hScrollBound === "1") {
      return;
    }
    try {
      panel.dataset.hScrollBound = "1";
      panel.classList.add("h-scroll-panel");

      const affordance = affordanceRoot(panel);
      affordance.classList.add("h-scroll-affordance");
      ensureHint(affordance, panel);

      const refresh = () => updateAffordance(affordance, panel);
      panel.addEventListener("scroll", refresh, { passive: true });
      global.addEventListener("resize", refresh, { passive: true });
      if (global.ResizeObserver) {
        const observer = new global.ResizeObserver(refresh);
        observer.observe(panel);
        if (affordance !== panel) {
          observer.observe(affordance);
        }
      }
      refresh();
    } catch (error) {
      panel.dataset.hScrollBound = "0";
      console.error("horizontal scroll affordance bind failed", error);
    }
  }

  function initHorizontalScrollAffordances() {
    const seen = new Set();
    SCROLL_PANEL_SELECTORS.forEach((selector) => {
      document.querySelectorAll(selector).forEach((panel) => {
        if (seen.has(panel)) {
          return;
        }
        seen.add(panel);
        bindPanel(panel);
      });
    });
  }

  global.initHorizontalScrollAffordances = initHorizontalScrollAffordances;
})(window);

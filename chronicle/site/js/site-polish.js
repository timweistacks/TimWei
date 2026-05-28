(function initSitePolish(global) {
  const BANNER_KEY = "chronicle-learn-banner-dismissed";

  function initLearnBanner() {
    const banner = document.getElementById("overview-learn-banner");
    if (!banner) {
      return;
    }
    if (global.localStorage.getItem(BANNER_KEY) === "1") {
      banner.hidden = true;
      banner.setAttribute("aria-hidden", "true");
      return;
    }
    const btn = banner.querySelector("[data-banner-dismiss]");
    if (!btn) {
      return;
    }
    btn.addEventListener("click", () => {
      banner.classList.add("is-dismissed");
      banner.setAttribute("aria-hidden", "true");
      global.setTimeout(() => {
        banner.hidden = true;
        global.localStorage.setItem(BANNER_KEY, "1");
      }, 280);
    });
  }

  function initReadProgress() {
    const bar = document.querySelector(".read-progress-bar");
    if (!bar) {
      return;
    }
    function update() {
      const doc = document.documentElement;
      const scrollTop = doc.scrollTop || document.body.scrollTop;
      const scrollHeight = doc.scrollHeight - doc.clientHeight;
      const pct = scrollHeight > 0 ? Math.min(100, (scrollTop / scrollHeight) * 100) : 0;
      bar.style.width = `${pct}%`;
    }
    update();
    global.addEventListener("scroll", update, { passive: true });
  }

  function boot() {
    initLearnBanner();
    initReadProgress();
    if (typeof global.initHorizontalScrollAffordances === "function") {
      global.initHorizontalScrollAffordances();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);

(function () {
  var cfg = window.PERSONAL_LEDGER_SITE || {};
  var siteUrl = String(cfg.siteUrl || "").trim().replace(/\/+$/, "");
  if (!siteUrl) {
    return;
  }

  var canonical = document.querySelector('link[rel="canonical"]');
  if (canonical && !canonical.getAttribute("href")) {
    var pagePath = window.location.pathname.replace(/\/index\.html$/, "/");
    canonical.setAttribute("href", siteUrl + pagePath);
  }
})();

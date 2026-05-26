(function () {
  var cfg = window.PERSONAL_LEDGER_SITE || {};
  var siteUrl = String(cfg.siteUrl || "").trim().replace(/\/+$/, "");
  if (!siteUrl) {
    return;
  }

  var pagePath = window.location.pathname.replace(/\/index\.html$/, "/");
  if (!pagePath.endsWith("/") && !/\.html$/i.test(pagePath.split("/").pop() || "")) {
    pagePath = pagePath.replace(/\/?$/, "/");
  }
  var canonicalHref = siteUrl + pagePath;

  var canonical = document.querySelector('link[rel="canonical"]');
  if (canonical && !canonical.getAttribute("href")) {
    canonical.setAttribute("href", canonicalHref);
  }

  var ogUrl = document.querySelector('meta[property="og:url"]');
  if (ogUrl && !ogUrl.getAttribute("content")) {
    ogUrl.setAttribute("content", canonicalHref);
  }
})();

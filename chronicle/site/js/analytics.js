(function () {
  var cfg = window.PERSONAL_LEDGER_SITE || {};
  var measurementId = String(cfg.gaMeasurementId || "").trim();
  if (!measurementId || measurementId.indexOf("G-") !== 0) {
    return;
  }

  var loader = document.createElement("script");
  loader.async = true;
  loader.src =
    "https://www.googletagmanager.com/gtag/js?id=" +
    encodeURIComponent(measurementId);
  document.head.appendChild(loader);

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", measurementId, { anonymize_ip: true });

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

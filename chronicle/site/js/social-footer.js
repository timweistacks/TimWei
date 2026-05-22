(function initSocialFooter(global) {
  var ICONS = {
    threads:
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M16.28 11.24c-.08 3.64-2.52 4.66-4.58 4.66-2.48 0-4.5-2.01-4.5-4.5s2.02-4.5 4.5-4.5c.99 0 1.92.32 2.68.86l1.2-1.38A6.9 6.9 0 0 0 11.7 4.5C7.36 4.5 3.82 8.04 3.82 12.4s3.54 7.9 7.88 7.9c4.82 0 7.98-3.36 7.98-9.08 0-.24-.02-.48-.05-.72H11.7v2.74h4.58z"/></svg>',
    instagram:
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5A5.5 5.5 0 1 1 6.5 13 5.51 5.51 0 0 1 12 7.5zm0 2A3.5 3.5 0 1 0 15.5 13 3.5 3.5 0 0 0 12 9.5zM17.8 6.3a1.1 1.1 0 1 1-1.1 1.1 1.1 1.1 0 0 1 1.1-1.1z"/></svg>',
    "facebook-profile":
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M13.5 8.5V6.8c0-.8.1-1.2 1-1.2h1.7V3.2h-2.4c-2.3 0-3.3 1.4-3.3 3.5v1.8H8.5V11h2V21h3V11h2.1l.4-2.5H13.5z"/></svg>',
    group:
      '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M9 11a3 3 0 1 0-3-3 3 3 0 0 0 3 3zm8 0a2.7 2.7 0 1 0-2.7-2.7A2.7 2.7 0 0 0 17 11zm-8 2c-2.67 0-8 1.34-8 4v2h8v-2c0-.92.28-1.77.76-2.5-1.04-.33-2.28-.5-3.76-.5zm8 0c-.55 0-1.07.04-1.57.11 1.05.72 1.77 1.74 1.77 3.02v1.87H24v-2c0-2.66-5.33-4-8-4z"/></svg>',
  };

  var LABELS = {
    group: { zh: "討論社團", en: "Discussion group" },
    threads: { zh: "Threads", en: "Threads" },
    instagram: { zh: "Instagram", en: "Instagram" },
    "facebook-profile": { zh: "Facebook", en: "Facebook" },
    note: {
      zh: "交流與討論（非投資建議）",
      en: "Community links (not investment advice)",
    },
  };

  function t(key) {
    var lang =
      global.PLLocale && global.PLLocale.getLang
        ? global.PLLocale.getLang()
        : "zh-Hant";
    var bucket = lang === "en" ? "en" : "zh";
    return (LABELS[key] && LABELS[key][bucket]) || key;
  }

  function iconLink(id, url) {
    return (
      '<a class="site-footer-icon" href="' +
      url +
      '" target="_blank" rel="noopener noreferrer" aria-label="' +
      t(id) +
      '">' +
      (ICONS[id] || "") +
      "</a>"
    );
  }

  function render() {
    var cfg = global.PERSONAL_LEDGER_SITE || {};
    var social = cfg.social || {};
    var mount = document.getElementById("site-footer");
    if (!mount || !social.group || !social.group.url) {
      return;
    }

    var icons = (social.links || [])
      .filter(function (item) {
        return item && item.url && ICONS[item.id];
      })
      .map(function (item) {
        return iconLink(item.id, item.url);
      })
      .join("");

    mount.innerHTML =
      '<div class="site-footer-inner">' +
      '<p class="site-footer-note">' +
      t("note") +
      "</p>" +
      '<div class="site-footer-row">' +
      '<a class="site-footer-group" href="' +
      social.group.url +
      '" target="_blank" rel="noopener noreferrer">' +
      '<span class="site-footer-group-icon" aria-hidden="true">' +
      ICONS.group +
      "</span>" +
      "<span>" +
      t("group") +
      "</span>" +
      "</a>" +
      (icons ? '<span class="site-footer-divider" aria-hidden="true"></span>' + icons : "") +
      "</div>" +
      "</div>";
    mount.hidden = false;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})(window);

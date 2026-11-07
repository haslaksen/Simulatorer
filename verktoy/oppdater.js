/* Oppdater-knapp (samme som i Verkstedhåndboka): når siden er endret på nettet, kommer
   «Ny versjon av siden er klar. Oppdater» nederst. Siden sjekkes når du kommer tilbake til den
   (ny fane, åpner PC-en igjen) og hvert 10. minutt mens den vises. Sjekken er en liten
   HEAD-forespørsel (bare overskrifter, ikke selve siden), så sidene blir ikke tregere. */
(function () {
  if (!/^https?:$/.test(location.protocol) || !window.fetch) return;
  var url = location.pathname + location.search, forrige = null, sist = 0, vist = false;
  function hent() {
    var o = { cache: "no-store", credentials: "same-origin" };
    return fetch(url, { method: "HEAD", cache: o.cache, credentials: o.credentials }).then(function (r) {
      if (!r.ok || r.redirected) return null;
      var m = r.headers.get("etag") || r.headers.get("last-modified");
      if (m) return m;
      // Ingen ETag: sammenlign innholdet (skjer bare om serveren ikke sender ETag).
      return fetch(url, o).then(function (r) { return r.ok && !r.redirected ? r.text() : null; }).then(function (t) {
        if (t == null) return null;
        for (var h = 0, i = 0; i < t.length; i++) h = (h * 31 + t.charCodeAt(i)) | 0;
        return "h" + h + "-" + t.length;
      });
    }).catch(function () { return null; });
  }
  function vis() {
    if (vist) return; vist = true;
    var st = document.createElement("style");
    st.textContent = ".pwa-toast{position:fixed;left:0;right:0;margin:0 auto;width:max-content;box-sizing:border-box;bottom:calc(20px + env(safe-area-inset-bottom,0px));z-index:2147483000;background:#1c2228;color:#fff;font:14px/1.3 system-ui,-apple-system,'Segoe UI',sans-serif;padding:10px 14px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.25);display:flex;gap:12px;align-items:center;max-width:calc(100vw - 32px)}" +
      ".pwa-toast button{font:inherit;font-weight:600;background:transparent;color:inherit;border:1px solid currentColor;border-radius:6px;padding:6px 10px;cursor:pointer}@media print{.pwa-toast{display:none!important}}";
    document.head.appendChild(st);
    var t = document.createElement("div"); t.className = "pwa-toast"; t.setAttribute("role", "status");
    t.innerHTML = '<span>Ny versjon av siden er klar.</span><button type="button">Oppdater</button>';
    t.querySelector("button").onclick = function () { location.reload(); };
    document.body.appendChild(t);
  }
  function sjekk() {
    if (vist || document.visibilityState === "hidden" || Date.now() - sist < 60000) return;
    sist = Date.now();
    hent().then(function (m) {
      if (!m) return;
      if (forrige === null) forrige = m; else if (m !== forrige) vis();
    });
  }
  // Første sjekk venter til siden er ferdig lastet, så den ikke tar tid fra innlastingen.
  window.addEventListener("load", function () {
    setTimeout(function () { sist = 0; sjekk(); }, 4000);
    document.addEventListener("visibilitychange", sjekk);
    window.addEventListener("focus", sjekk);
    setInterval(function () { sist = 0; sjekk(); }, 600000);
  });
})();

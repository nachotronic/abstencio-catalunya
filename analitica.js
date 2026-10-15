// Google Analytics 4 con consentimiento previo, para todas las páginas de mapaelectoral.es.
// Cloudflare Web Analytics sigue cargándose aparte: no usa cookies y no necesita aviso.
// GA solo se carga si el lector pulsa «Aceptar»; hasta entonces no se descarga nada de Google.
// Mientras GA_ID sea el marcador, este archivo no hace nada (ni muestra el aviso).
(function () {
  var GA_ID = 'G-XXXXXXXXXX';
  var CLAVE = 'me-cookies';  // 'si' | 'no'
  if (!/^G-[A-Z0-9]{6,}$/.test(GA_ID) || GA_ID === 'G-XXXXXXXXXX') return;

  var ca = (document.documentElement.lang || '').slice(0, 2) === 'ca';
  var T = ca ? {
    txt: 'Fem servir Google Analytics per saber quantes persones llegeixen el mapa i quines peces interessen. Només s’activa si ho acceptes.',
    si: 'Acceptar', no: 'Rebutjar', mas: 'Més informació', url: '/cookies.html#ca'
  } : {
    txt: 'Usamos Google Analytics para saber cuánta gente lee el mapa y qué piezas interesan. Solo se activa si lo aceptas.',
    si: 'Aceptar', no: 'Rechazar', mas: 'Más información', url: '/cookies.html'
  };

  function leer() { try { return localStorage.getItem(CLAVE); } catch (e) { return null; } }
  function guardar(v) { try { localStorage.setItem(CLAVE, v); } catch (e) {} }

  var cargado = false;
  function cargarGA() {
    if (cargado) return;
    cargado = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, { cookie_flags: 'SameSite=Lax;Secure' });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  function borrarCookiesGA() {
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (/^_ga/.test(n)) {
        ['', '; domain=.' + location.hostname.replace(/^www\./, '')].forEach(function (d) {
          document.cookie = n + '=; Max-Age=0; path=/' + d;
        });
      }
    });
  }

  function aviso() {
    if (document.getElementById('me-aviso-cookies')) return;
    var d = document.createElement('div');
    d.id = 'me-aviso-cookies';
    d.setAttribute('role', 'dialog');
    d.setAttribute('aria-label', 'Cookies');
    d.style.cssText = 'position:fixed;left:12px;right:12px;bottom:12px;z-index:2147483000;max-width:560px;margin:0 auto;' +
      'background:#fff;color:#222;border:1px solid #d6d6d6;border-radius:8px;box-shadow:0 4px 18px rgba(0,0,0,.18);' +
      'padding:12px 14px;font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif';
    var b = 'cursor:pointer;border-radius:6px;padding:6px 14px;font:inherit;font-weight:600;';
    d.innerHTML = '<p style="margin:0 0 10px">' + T.txt + ' <a href="' + T.url + '" style="color:inherit">' + T.mas + '</a></p>' +
      '<div style="display:flex;gap:8px;justify-content:flex-end">' +
      '<button type="button" data-v="no" style="' + b + 'background:#fff;color:#222;border:1px solid #888">' + T.no + '</button>' +
      '<button type="button" data-v="si" style="' + b + 'background:#222;color:#fff;border:1px solid #222">' + T.si + '</button></div>';
    d.addEventListener('click', function (ev) {
      var v = ev.target && ev.target.getAttribute && ev.target.getAttribute('data-v');
      if (!v) return;
      guardar(v);
      d.parentNode.removeChild(d);
      if (v === 'si') cargarGA(); else borrarCookiesGA();
    });
    (document.body || document.documentElement).appendChild(d);
  }

  // Para cambiar de opinión (enlace en /cookies.html): borra la elección y vuelve a preguntar.
  window.mapaCookies = function () {
    try { localStorage.removeItem(CLAVE); } catch (e) {}
    borrarCookiesGA();
    aviso();
  };

  var v = leer();
  if (v === 'si') cargarGA();
  else if (v !== 'no') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', aviso);
    else aviso();
  }
})();

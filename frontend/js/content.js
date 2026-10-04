/**
 * Uređivani sadržaj stranice (blokovi iz admin panela)
 *
 * Elementi označeni sa data-cms="ključ" zamjenjuju se sadržajem koji je admin
 * sačuvao u bazi. Ako za ključ nema izmjene, ostaje originalni sadržaj iz HTML-a.
 *
 * Upotreba: <script src="/js/content.js" data-page="index" defer></script>
 */
(function () {
  'use strict';

  const script = document.currentScript;
  const page = script && script.dataset.page;
  if (!page) return;

  const url = window.API_CONFIG
    ? window.API_CONFIG.getUrl('/api/content/' + encodeURIComponent(page))
    : '/api/content/' + encodeURIComponent(page);

  // Godine od osnivanja se racunaju same: <span data-years-since="1988" data-years-suffix="+">
  function fillYears() {
    const year = new Date().getFullYear();
    document.querySelectorAll('[data-years-since]').forEach((el) => {
      const since = parseInt(el.dataset.yearsSince, 10);
      if (since) el.textContent = (year - since) + (el.dataset.yearsSuffix || '');
    });
  }

  async function apply() {
    fillYears();
    let blocks;
    try {
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) return;
      const json = await res.json();
      blocks = (json.data && json.data.blocks) || {};
    } catch (e) {
      return; // bez mreže ostaje originalni sadržaj
    }

    let changed = false;
    document.querySelectorAll('[data-cms]').forEach((el) => {
      const html = blocks[el.dataset.cms];
      if (typeof html === 'string') {
        el.innerHTML = html;
        changed = true;
      }
    });

    if (changed) fillYears(); // sacuvani blokovi mogu sadrzavati data-years-since

    // Ako je korisnik izabrao ćirilicu, preslovi i novi sadržaj
    if (changed && typeof transliterator !== 'undefined' && transliterator.applyPreference) {
      transliterator.applyPreference();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply);
  } else {
    apply();
  }
})();

/**
 * "Dodaj na telefon / računar": uputstvo za instalaciju sajta kao aplikacije (PWA).
 *
 * Svaki element sa atributom data-install-open otvara prozor sa uputstvom za uređaj posjetioca.
 * Gdje preglednik podržava (Chrome/Edge/Android), nudi se i dugme "Instaliraj" koje pokreće instalaciju.
 * Ako je sajt već instaliran (otvoren kao aplikacija), linkovi se sakrivaju.
 */
(function () {
  'use strict';

  const TRIGGERS = () => document.querySelectorAll('[data-install-open]');

  const isStandalone =
    (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) || window.navigator.standalone === true;
  if (isStandalone) {
    document.addEventListener('DOMContentLoaded', () => TRIGGERS().forEach((el) => (el.closest('li') || el).remove()));
    return;
  }

  function detectPlatform() {
    const ua = navigator.userAgent || '';
    if (/iPhone|iPad|iPod/i.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)) return 'ios';
    if (/Android/i.test(ua)) return 'android';
    return 'desktop';
  }

  const GUIDES = {
    android: {
      title: 'Android (Chrome)',
      steps: [
        'Otvorite sajt u pregledniku <strong>Chrome</strong>.',
        'Dodirnite meni <strong>⋮</strong> (tri tačkice gore desno).',
        'Izaberite <strong>„Instaliraj aplikaciju“</strong> ili <strong>„Dodaj na početni ekran“</strong>.',
        'Potvrdite. Ikonica sa logom društva pojaviće se na početnom ekranu.',
      ],
    },
    ios: {
      title: 'iPhone i iPad (Safari)',
      steps: [
        'Otvorite sajt u pregledniku <strong>Safari</strong> (u drugim preglednicima ova opcija ne postoji).',
        'Dodirnite dugme za dijeljenje <strong>(kvadrat sa strelicom prema gore)</strong> u dnu ekrana.',
        'Pomjerite listu i izaberite <strong>„Dodaj na početni ekran“</strong>.',
        'Dodirnite <strong>„Dodaj“</strong>. Ikonica sa logom društva pojaviće se na početnom ekranu.',
      ],
    },
    desktop: {
      title: 'Računar (Chrome ili Edge)',
      steps: [
        'Otvorite sajt u pregledniku <strong>Chrome</strong> ili <strong>Edge</strong>.',
        'U adresnoj traci kliknite ikonicu za instalaciju <strong>(monitor sa strelicom)</strong>, ili otvorite meni <strong>⋮</strong> i izaberite <strong>„Instaliraj PED Majevica“</strong>.',
        'Potvrdite. Prečica sa logom društva pojaviće se na radnoj površini i u izborniku programa.',
        'Firefox na računaru ne podržava instalaciju sajtova; koristite Chrome ili Edge.',
      ],
    },
  };

  let deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault(); // sami biramo kad ponuditi instalaciju
    deferredPrompt = e;
  });
  window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    closeModal();
    TRIGGERS().forEach((el) => (el.closest('li') || el).remove());
  });

  let modal = null;
  let lastFocus = null;

  function guideHtml(key, open) {
    const g = GUIDES[key];
    const steps = g.steps.map((s) => '<li class="mb-2">' + s + '</li>').join('');
    return (
      '<h3 class="text-lg font-bold text-primary-blue mb-2">' + g.title + '</h3>' +
      '<ol class="list-decimal pl-6 text-gray-700 leading-relaxed">' + steps + '</ol>'
    );
  }

  function build() {
    const platform = detectPlatform();
    const others = Object.keys(GUIDES).filter((k) => k !== platform);

    modal = document.createElement('div');
    modal.id = 'installModal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'installModalTitle');
    modal.className = 'hidden fixed inset-0 z-[110] items-center justify-center p-4 bg-black/80 overscroll-contain';
    modal.innerHTML =
      '<div class="bg-white rounded-2xl max-w-lg w-full max-h-[90dvh] overflow-y-auto overscroll-contain shadow-2xl">' +
        '<div class="flex items-start justify-between gap-4 bg-primary-blue text-white px-6 py-4 rounded-t-2xl">' +
          '<h2 id="installModalTitle" class="text-xl font-bold">Dodajte PED Majevica na telefon ili računar</h2>' +
          '<button type="button" data-install-close aria-label="Zatvori" class="w-9 h-9 flex-shrink-0 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center">' +
            '<i class="fas fa-times" aria-hidden="true"></i></button>' +
        '</div>' +
        '<div class="p-6">' +
          '<p class="text-gray-600 mb-4">Ikonica sa logom društva otvara sajt jednim dodirom, kao aplikacija.</p>' +
          '<div id="installNative" class="hidden mb-5">' +
            '<button type="button" data-install-now class="w-full px-6 py-3 rounded-xl bg-primary-red hover:bg-red-dark text-white font-bold">' +
              '<i class="fas fa-download mr-2" aria-hidden="true"></i>Instaliraj sada</button>' +
          '</div>' +
          guideHtml(platform) +
          '<details class="mt-6 border-t border-gray-200 pt-4">' +
            '<summary class="cursor-pointer font-semibold text-primary-blue">Uputstvo za druge uređaje</summary>' +
            '<div class="mt-4 space-y-5">' + others.map((k) => '<div>' + guideHtml(k) + '</div>').join('') + '</div>' +
          '</details>' +
        '</div>' +
      '</div>';
    document.body.appendChild(modal);

    modal.addEventListener('click', (e) => {
      if (e.target === modal || e.target.closest('[data-install-close]')) closeModal();
    });
    modal.querySelector('[data-install-now]').addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      try { await deferredPrompt.userChoice; } catch (e) { /* ignorisi */ }
      deferredPrompt = null;
      closeModal();
    });
  }

  function openModal() {
    if (!modal) build();
    // dugme "Instaliraj sada" samo kad ga preglednik podrzava
    modal.querySelector('#installNative').classList.toggle('hidden', !deferredPrompt);
    lastFocus = document.activeElement;
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
    const closeBtn = modal.querySelector('[data-install-close]');
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && !modal.classList.contains('hidden')) closeModal();
  });

  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-install-open]')) {
      e.preventDefault();
      openModal();
    }
  });
})();

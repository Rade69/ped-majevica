/**
 * Admin: GPX fajl staze (sekcija u formi za stazu)
 *
 * GPX se dodaje uz postojeću stazu (izmjena staze): izaberite fajl i kliknite "Dodaj / zamijeni GPX".
 * Posjetioci ga preuzimaju dugmetom "Preuzmi GPX" na kartici staze.
 */
(function () {
  'use strict';

  const state = { trail: null };
  const $ = (id) => document.getElementById(id);

  function url(path) {
    return window.API_CONFIG ? window.API_CONFIG.getUrl(path) : path;
  }

  function setStatus(text, ok) {
    const el = $('gpxStatus');
    if (!el) return;
    el.textContent = text;
    el.className = 'text-sm mb-3 font-semibold ' + (ok === false ? 'text-red-600' : ok ? 'text-green-700' : '');
  }

  function render() {
    const box = $('gpxBox');
    if (!box) return;
    const t = state.trail;
    const active = !!t;
    $('gpxFile').disabled = !active;
    $('gpxUploadBtn').disabled = !active;
    $('gpxUploadBtn').classList.toggle('opacity-50', !active);
    $('gpxHint').classList.toggle('hidden', active);
    const hasGpx = active && t.has_gpx;
    $('gpxRemoveBtn').classList.toggle('hidden', !hasGpx);
    const dl = $('gpxDownload');
    dl.classList.toggle('hidden', !hasGpx);
    if (hasGpx) dl.href = url('/api/trails/' + t.id + '/gpx');
    if (!active) setStatus('Izaberite stazu za izmjenu (dugme „Izmijeni“ u listi), pa dodajte GPX.', null);
    else setStatus(hasGpx ? 'GPX fajl je dodat. Posjetioci ga mogu preuzeti.' : 'Ova staza još nema GPX fajl.', hasGpx ? true : null);
  }

  window.gpxOnEdit = function (trail) { state.trail = { id: trail.id, has_gpx: !!trail.has_gpx }; render(); };
  window.gpxOnClear = function () { state.trail = null; render(); };

  async function request(method, options) {
    const res = await fetch(url('/api/trails/' + state.trail.id + '/gpx'), { method, credentials: 'include', ...options });
    let json = null;
    try { json = await res.json(); } catch (e) { /* prazno tijelo */ }
    if (!res.ok || !json || json.success === false) {
      throw new Error((json && (json.message || json.error)) || 'Greška na serveru (' + res.status + ')');
    }
    return json.data || {};
  }

  window.gpxUpload = async function () {
    if (!state.trail) return;
    const file = $('gpxFile').files[0];
    if (!file) { setStatus('Prvo izaberite GPX fajl.', false); return; }
    const form = new FormData();
    form.append('file', file);
    const btn = $('gpxUploadBtn');
    btn.disabled = true;
    setStatus('Šaljem fajl…', null);
    try {
      const data = await request('POST', { body: form }); // Content-Type postavlja preglednik
      state.trail.has_gpx = true;
      $('gpxFile').value = '';
      render();
      setStatus('GPX dodat: ' + data.points + ' tačaka, ' + Math.max(1, Math.round(data.size / 1024)) + ' KB.', true);
      if (window.loadTrails) window.loadTrails(); // osvježi listu staza
    } catch (e) {
      setStatus('GPX nije sačuvan: ' + e.message, false);
    } finally {
      btn.disabled = !state.trail;
    }
  };

  window.gpxRemove = async function () {
    if (!state.trail || !confirm('Ukloniti GPX fajl ove staze?')) return;
    try {
      await request('DELETE', {});
      state.trail.has_gpx = false;
      render();
      setStatus('GPX je uklonjen.', null);
      if (window.loadTrails) window.loadTrails();
    } catch (e) {
      setStatus('Greška: ' + e.message, false);
    }
  };

  document.addEventListener('DOMContentLoaded', render);
})();

/**
 * Admin: uređivanje sadržaja stranica (tab "Sadržaj")
 *
 * Blokovi se otkrivaju iz HTML-a javne stranice (elementi sa data-cms="ključ").
 * Originalni sadržaj je onaj iz HTML fajla; izmjene se čuvaju u bazi (/api/content).
 */
(function () {
  'use strict';

  const PAGES = {
    index: { label: 'Početna', url: '/' },
    galerija: { label: 'Galerija', url: '/galerija' },
    'uclanite-se': { label: 'Učlanite se', url: '/uclanite-se' },
  };

  const state = { page: 'index', blocks: [], saved: {}, current: null, htmlMode: false, ready: false };

  const $ = (id) => document.getElementById(id);

  function apiUrl(path) {
    return window.API_CONFIG ? window.API_CONFIG.getUrl(path) : path;
  }

  function escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function plainText(html) {
    const doc = new DOMParser().parseFromString(html || '', 'text/html');
    return (doc.body.textContent || '').replace(/\s+/g, ' ').trim();
  }

  async function api(path, options = {}) {
    const res = await fetch(apiUrl(path), {
      credentials: 'include',
      ...options,
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    });
    let json = null;
    try { json = await res.json(); } catch (e) { /* prazno tijelo */ }
    if (!res.ok || !json || json.success === false) {
      throw new Error((json && (json.message || json.error)) || 'Greška na serveru (' + res.status + ')');
    }
    return json.data || {};
  }

  // ---------------------------------------------------------------- učitavanje

  async function discoverBlocks(page) {
    const res = await fetch(PAGES[page].url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error('Ne mogu učitati stranicu');
    const doc = new DOMParser().parseFromString(await res.text(), 'text/html');
    const seen = new Set();
    const blocks = [];
    doc.querySelectorAll('[data-cms]').forEach((el) => {
      const key = el.dataset.cms;
      if (seen.has(key)) return;
      seen.add(key);
      blocks.push({
        key,
        label: el.dataset.cmsLabel || key,
        type: el.dataset.cmsType === 'text' ? 'text' : 'html',
        original: el.innerHTML.trim(),
      });
    });
    return blocks;
  }

  async function loadPage(page) {
    state.page = page;
    state.current = null;
    renderEditor();
    $('cmsBlockList').textContent = 'Učitavanje…';
    try {
      const [blocks, data] = await Promise.all([
        discoverBlocks(page),
        api('/api/content/' + encodeURIComponent(page)),
      ]);
      state.blocks = blocks;
      state.saved = data.blocks || {};
      renderList();
    } catch (e) {
      $('cmsBlockList').textContent = 'Greška: ' + e.message;
    }
  }

  window.loadContentEditor = async function () {
    if (!state.ready) {
      const select = $('cmsPageSelect');
      Object.keys(PAGES).forEach((key) => {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = PAGES[key].label;
        select.appendChild(opt);
      });
      select.addEventListener('change', () => loadPage(select.value));
      state.ready = true;
    }
    await loadPage(state.page);
  };

  // ------------------------------------------------------------------ prikaz

  function renderList() {
    const list = $('cmsBlockList');
    list.textContent = '';
    state.blocks.forEach((block) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'cms-block-btn w-full text-left px-4 py-3 rounded-lg border mb-2 flex items-center justify-between';
      if (state.current && state.current.key === block.key) btn.classList.add('active');
      const name = document.createElement('span');
      name.textContent = block.label;
      btn.appendChild(name);
      if (typeof state.saved[block.key] === 'string') {
        const badge = document.createElement('span');
        badge.className = 'ml-2 text-xs bg-primary-red text-white px-2 py-0.5 rounded-full';
        badge.textContent = 'izmijenjeno';
        btn.appendChild(badge);
      }
      btn.addEventListener('click', () => selectBlock(block.key));
      list.appendChild(btn);
    });
  }

  function currentValue(block) {
    return typeof state.saved[block.key] === 'string' ? state.saved[block.key] : block.original;
  }

  function selectBlock(key) {
    state.current = state.blocks.find((b) => b.key === key) || null;
    state.htmlMode = false;
    renderList();
    renderEditor();
  }

  function renderEditor() {
    const box = $('cmsEditor');
    const empty = $('cmsEmpty');
    const block = state.current;
    box.classList.toggle('hidden', !block);
    empty.classList.toggle('hidden', !!block);
    $('cmsHistory').classList.add('hidden');
    if (!block) return;

    $('cmsBlockTitle').textContent = block.label;
    const isText = block.type === 'text';
    $('cmsToolbar').classList.toggle('hidden', isText);
    $('cmsRich').classList.toggle('hidden', isText);
    $('cmsSource').classList.add('hidden');
    $('cmsText').classList.toggle('hidden', !isText);
    $('cmsHtmlToggle').classList.toggle('hidden', isText);

    const value = currentValue(block);
    if (isText) {
      $('cmsText').value = plainText(value);
    } else {
      $('cmsRich').innerHTML = value;
      $('cmsSource').value = value;
    }
    const isModified = typeof state.saved[block.key] === 'string';
    $('cmsResetBtn').classList.toggle('hidden', !isModified);
    $('cmsPreviewLink').href = PAGES[state.page].url;
  }

  // ----------------------------------------------------------------- uređivač

  window.cmsFormat = function (command, value) {
    if (state.htmlMode) return;
    $('cmsRich').focus();
    document.execCommand(command, false, value || null);
  };

  window.cmsLink = function () {
    if (state.htmlMode) return;
    const url = prompt('Adresa linka (npr. https://primjer.ba ili /galerija):');
    if (url) window.cmsFormat('createLink', url);
  };

  window.cmsToggleHtml = function () {
    const rich = $('cmsRich');
    const source = $('cmsSource');
    if (!state.htmlMode) {
      source.value = rich.innerHTML;
      rich.classList.add('hidden');
      source.classList.remove('hidden');
      $('cmsToolbar').classList.add('opacity-50');
    } else {
      rich.innerHTML = source.value;
      source.classList.add('hidden');
      rich.classList.remove('hidden');
      $('cmsToolbar').classList.remove('opacity-50');
    }
    state.htmlMode = !state.htmlMode;
  };

  function collectHtml() {
    const block = state.current;
    if (block.type === 'text') return escapeHtml($('cmsText').value.trim());
    return (state.htmlMode ? $('cmsSource').value : $('cmsRich').innerHTML).trim();
  }

  window.cmsSave = async function () {
    const block = state.current;
    if (!block) return;
    const btn = $('cmsSaveBtn');
    btn.disabled = true;
    try {
      const html = collectHtml();
      const data = await api(
        '/api/content/' + encodeURIComponent(state.page) + '/' + encodeURIComponent(block.key),
        { method: 'PUT', body: JSON.stringify({ html }) }
      );
      state.saved[block.key] = data.html;
      renderList();
      renderEditor();
      alert('Sačuvano. Izmjena je odmah vidljiva na stranici.');
    } catch (e) {
      alert('Greška pri čuvanju: ' + e.message);
    } finally {
      btn.disabled = false;
    }
  };

  window.cmsReset = async function () {
    const block = state.current;
    if (!block || !confirm('Vratiti ovaj blok na originalni tekst?')) return;
    try {
      await api(
        '/api/content/' + encodeURIComponent(state.page) + '/' + encodeURIComponent(block.key),
        { method: 'DELETE' }
      );
      delete state.saved[block.key];
      renderList();
      renderEditor();
    } catch (e) {
      alert('Greška: ' + e.message);
    }
  };

  window.cmsShowHistory = async function () {
    const block = state.current;
    if (!block) return;
    const panel = $('cmsHistory');
    const list = $('cmsHistoryList');
    panel.classList.remove('hidden');
    list.textContent = 'Učitavanje…';
    try {
      const data = await api(
        '/api/content/' + encodeURIComponent(state.page) + '/' + encodeURIComponent(block.key) + '/history'
      );
      const revisions = data.revisions || [];
      list.textContent = '';
      if (!revisions.length) {
        list.textContent = 'Nema ranijih verzija.';
        return;
      }
      revisions.forEach((rev) => {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between gap-3 py-2 border-b';
        const info = document.createElement('span');
        info.className = 'text-sm';
        const when = rev.created_at ? new Date(rev.created_at + 'Z').toLocaleString('sr-Latn') : '';
        const text = rev.html === null ? '(vraćeno na original)' : plainText(rev.html).slice(0, 80);
        info.textContent = when + ' — ' + text;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'text-sm font-bold text-primary-blue underline whitespace-nowrap';
        btn.textContent = 'Vrati ovu verziju';
        btn.addEventListener('click', () => restore(rev.id));
        row.appendChild(info);
        row.appendChild(btn);
        list.appendChild(row);
      });
    } catch (e) {
      list.textContent = 'Greška: ' + e.message;
    }
  };

  async function restore(revisionId) {
    const block = state.current;
    if (!block || !confirm('Vratiti ovu verziju?')) return;
    try {
      const data = await api(
        '/api/content/' + encodeURIComponent(state.page) + '/' + encodeURIComponent(block.key) +
          '/restore/' + revisionId,
        { method: 'POST' }
      );
      if (typeof data.html === 'string') state.saved[block.key] = data.html;
      else delete state.saved[block.key];
      renderList();
      renderEditor();
    } catch (e) {
      alert('Greška: ' + e.message);
    }
  }
})();

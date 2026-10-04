/**
 * Admin: poruke iz kontakt forme (tab "Poruke")
 *
 * Sav tekst posjetilaca se prikazuje kao običan tekst (textContent), nikad kao HTML.
 */
(function () {
  'use strict';

  const state = { page: 1, pages: 1 };
  const $ = (id) => document.getElementById(id);

  function url(path) {
    return window.API_CONFIG ? window.API_CONFIG.getUrl(path) : path;
  }

  async function api(path, options = {}) {
    const res = await fetch(url(path), {
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

  function setBadge(unread) {
    const badge = $('porukeCount');
    if (!badge) return;
    badge.textContent = unread;
    badge.classList.toggle('hidden', !unread);
  }

  function el(tag, className, text) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  function renderMessage(m) {
    const card = el('div', 'card rounded-2xl p-5 mb-4 border-l-4 ' + (m.is_read ? 'border-gray-300' : 'border-primary-red'));

    const head = el('div', 'flex flex-wrap items-start justify-between gap-3 mb-3');
    const who = el('div');
    who.appendChild(el('div', 'font-bold text-lg', m.name + (m.is_read ? '' : '  •  novo')));
    const mail = el('a', 'text-primary-blue underline text-sm', m.email);
    mail.href = 'mailto:' + m.email + '?subject=' + encodeURIComponent('Re: ' + (m.subject || 'Vaša poruka PED Majevica'));
    who.appendChild(mail);
    head.appendChild(who);
    const when = m.created_at ? new Date(m.created_at + 'Z').toLocaleString('sr-Latn') : '';
    head.appendChild(el('div', 'text-sm opacity-70', when));
    card.appendChild(head);

    if (m.subject) card.appendChild(el('div', 'text-sm font-semibold mb-1', 'Tema: ' + m.subject));
    if (m.membership_interest) {
      card.appendChild(el('div', 'inline-block text-xs bg-secondary-gold text-primary-blue font-bold px-2 py-1 rounded-full mb-2', 'Zanima ga članstvo'));
    }
    const body = el('p', 'whitespace-pre-wrap break-words mb-4', m.message);
    card.appendChild(body);

    const actions = el('div', 'flex flex-wrap gap-2');
    const reply = el('a', 'px-4 py-2 rounded-lg font-bold bg-primary-blue text-white', 'Odgovori');
    reply.href = mail.href;
    actions.appendChild(reply);

    const toggle = el('button', 'px-4 py-2 rounded-lg font-bold border border-gray-300',
      m.is_read ? 'Označi kao nepročitano' : 'Označi kao pročitano');
    toggle.type = 'button';
    toggle.addEventListener('click', async () => {
      try {
        await api('/api/contact/' + m.id + '/read', { method: 'PUT', body: JSON.stringify({ is_read: !m.is_read }) });
        load();
      } catch (e) { alert('Greška: ' + e.message); }
    });
    actions.appendChild(toggle);

    const del = el('button', 'px-4 py-2 rounded-lg font-bold border border-red-300 text-red-600', 'Obriši');
    del.type = 'button';
    del.addEventListener('click', async () => {
      if (!confirm('Trajno obrisati ovu poruku?')) return;
      try {
        await api('/api/contact/' + m.id, { method: 'DELETE' });
        load();
      } catch (e) { alert('Greška: ' + e.message); }
    });
    actions.appendChild(del);

    card.appendChild(actions);
    return card;
  }

  async function load() {
    const list = $('porukeList');
    if (!list) return;
    try {
      const data = await api('/api/contact?per_page=20&page=' + state.page);
      state.pages = data.pagination.pages || 1;
      setBadge(data.unread);
      list.textContent = '';
      if (!data.messages.length) {
        list.appendChild(el('p', 'opacity-70', 'Nema poruka.'));
      }
      data.messages.forEach((m) => list.appendChild(renderMessage(m)));
      $('porukePrev').classList.toggle('hidden', state.page <= 1);
      $('porukeNext').classList.toggle('hidden', state.page >= state.pages);
    } catch (e) {
      list.textContent = 'Greška pri učitavanju poruka: ' + e.message;
    }
  }

  window.loadMessages = function () { state.page = 1; return load(); };
  window.messagesPage = function (delta) { state.page = Math.max(1, Math.min(state.pages, state.page + delta)); return load(); };

  // broj nepročitanih odmah pri otvaranju admina
  document.addEventListener('DOMContentLoaded', async () => {
    try {
      const data = await api('/api/contact?per_page=1&unread=1');
      setBadge(data.unread);
    } catch (e) { /* bez prijave ostaje skriveno */ }
  });
})();

// frontend/js/admin/admin.js

import { state } from "./state.js";
import { TrailsAPI, EventsAPI } from "./api.js";
import { loadPosts } from "./posts.js";
import { updateDashboard } from "./dashboard.js";
import { initTheme, toggleTheme } from "./theme.js";

document.addEventListener("DOMContentLoaded", initAdmin);

/* ======================
   INIT
====================== */

async function initAdmin() {
  initTheme();
  bindTheme();

  // POSTS
  await loadPosts();
  updateDashboard();

  // TRAILS
  await loadTrails();
  updateDashboard();

  // EVENTS
  await loadEvents();
  updateDashboard();
}

/* ======================
   THEME
====================== */

function bindTheme() {
  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.addEventListener("click", toggleTheme);
  }
}

/* ======================
   LOADERS
====================== */

async function loadTrails() {
  try {
    const res = await TrailsAPI.list();

    // NORMALIZACIJA: uvijek array
    if (Array.isArray(res)) {
      state.trails = res;
    } else if (res && Array.isArray(res.trails)) {
      state.trails = res.trails;
    } else {
      state.trails = [];
    }
  } catch (err) {
    console.error("Greška pri učitavanju staza:", err);
    state.trails = [];
  }
}

async function loadEvents() {
  try {
    const res = await EventsAPI.list();

    // NORMALIZACIJA: uvijek array
    if (Array.isArray(res)) {
      state.events = res;
    } else if (res && Array.isArray(res.events)) {
      state.events = res.events;
    } else {
      state.events = [];
    }
  } catch (err) {
    console.error("Greška pri učitavanju događaja:", err);
    state.events = [];
  }
}

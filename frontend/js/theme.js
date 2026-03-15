// frontend/js/admin/admin.js
import { state } from "./state.js";
import { TrailsAPI, EventsAPI } from "./api.js";
import { loadPosts } from "./posts.js";
import { updateDashboard } from "./dashboard.js";
import { initTheme, toggleTheme } from "./theme.js";

document.addEventListener("DOMContentLoaded", initAdmin);

async function initAdmin() {
  initTheme();
  bindThemeToggle();

  await loadPosts();
  await loadTrails();
  await loadEvents();
  updateDashboard();
}

/* ======================
   THEME
====================== */

function bindThemeToggle() {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.addEventListener("click", toggleTheme);
}

/* ======================
   LOADERS
====================== */

async function loadTrails() {
  try {
    state.trails = await TrailsAPI.list();
  } catch (err) {
    console.error("Greška pri učitavanju staza:", err);
  }
}

async function loadEvents() {
  try {
    state.events = await EventsAPI.list();
  } catch (err) {
    console.error("Greška pri učitavanju događaja:", err);
  }
}

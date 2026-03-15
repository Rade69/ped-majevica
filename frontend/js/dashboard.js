// frontend/js/admin/dashboard.js
import { state } from "./state.js";

/* ======================
   DASHBOARD API
====================== */

export function updateDashboard() {
  // Posts
  setTextIfExists("posts-count", state.posts.length);
  setTextIfExists("headerPostCount", state.posts.length);

  // Trails
  setTextIfExists("trails-count", state.trails.length);
  setTextIfExists("headerTrailCount", state.trails.length);

  // Events
  setTextIfExists("events-count", state.events.length);
  setTextIfExists("headerEventCount", state.events.length);
}

/* ======================
   HELPERS
====================== */

function setTextIfExists(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = String(value);
}

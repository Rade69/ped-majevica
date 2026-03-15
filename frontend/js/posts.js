// frontend/js/admin/posts.js
import { state } from "./state.js";
import { PostsAPI } from "./api.js";
import { openPreview } from "./preview.js";

/* ======================
   PUBLIC API
====================== */

export async function loadPosts() {
  try {
    state.posts = await PostsAPI.list();
    renderPosts();
  } catch (err) {
    console.error("Greška pri učitavanju postova:", err);
  }
}

/* ======================
   RENDER
====================== */

function renderPosts() {
  const container = document.getElementById("posts-list");
  container.innerHTML = "";

  if (!state.posts.length) {
    container.innerHTML = "<p>Nema članaka.</p>";
    return;
  }

  state.posts.forEach((post) => {
    const el = document.createElement("div");
    el.className = "post-row";

    el.innerHTML = `
      <h3>${post.title}</h3>
      <small>${post.created_at}</small>
      <div class="actions">
        <button class="preview-btn">👁</button>
        <button class="delete-btn">🗑</button>
      </div>
    `;

    el.querySelector(".preview-btn")
      .addEventListener("click", () => openPreview(post.id));

    el.querySelector(".delete-btn")
      .addEventListener("click", () => deletePost(post.id));

    container.appendChild(el);
  });
}

/* ======================
   CRUD
====================== */

async function deletePost(id) {
  if (!confirm("Obrisati članak?")) return;

  try {
    await PostsAPI.remove(id);
    await loadPosts();
  } catch (err) {
    alert("Greška pri brisanju.");
    console.error(err);
  }
}

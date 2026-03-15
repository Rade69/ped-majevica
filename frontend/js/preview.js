// frontend/js/admin/preview.js
import { state } from "./state.js";

/* ======================
   PREVIEW MODAL
====================== */

export function openPreview(postId) {
  const post = state.posts.find(p => p.id === postId);
  if (!post) return;

  const modal = document.getElementById("preview-modal");
  const content = document.getElementById("preview-content");

  content.innerHTML = `
    <h2>${post.title}</h2>
    <small>${post.created_at}</small>
    <p>${post.preview || ""}</p>
    <hr />
    <div>${post.content || ""}</div>
  `;

  modal.style.display = "block";
}

export function closePreview() {
  const modal = document.getElementById("preview-modal");
  modal.style.display = "none";
}

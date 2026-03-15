/**
 * Gallery System - Centralized gallery management
 * Replaces inline gallery code
 */

const GallerySystem = (function () {
  "use strict";

  // State
  let currentIndex = 0;
  let images = [];
  let isOpen = false;

  // DOM Elements
  let lightbox = null;
  let lightboxImg = null;
  let lightboxCaption = null;
  let closeBtn = null;
  let prevBtn = null;
  let nextBtn = null;

  /**
   * Initialize gallery system
   */
  function init() {
    // Create lightbox DOM if not exists
    createLightbox();

    // Attach event listeners to gallery images
    attachGalleryListeners();

    console.log("✅ GallerySystem initialized");
  }

  /**
   * Create lightbox DOM elements
   */
  function createLightbox() {
    if (document.getElementById("gallery-lightbox")) return;

    const lightboxHTML = `
      <div id="gallery-lightbox" class="fixed inset-0 z-50 hidden bg-black bg-opacity-95">
        <button id="lightbox-close" class="absolute top-4 right-4 text-white text-4xl hover:text-gray-300 z-10">&times;</button>
        <button id="lightbox-prev" class="absolute left-4 top-1/2 -translate-y-1/2 text-white text-5xl hover:text-gray-300">&lsaquo;</button>
        <button id="lightbox-next" class="absolute right-4 top-1/2 -translate-y-1/2 text-white text-5xl hover:text-gray-300">&rsaquo;</button>
        <div class="flex items-center justify-center h-full p-8">
          <img id="lightbox-image" class="max-w-full max-h-full object-contain" src="" alt="">
        </div>
        <div id="lightbox-caption" class="absolute bottom-4 left-0 right-0 text-center text-white text-lg"></div>
        <div id="lightbox-counter" class="absolute top-4 left-4 text-white text-lg"></div>
      </div>
    `;

    document.body.insertAdjacentHTML("beforeend", lightboxHTML);

    // Cache DOM elements
    lightbox = document.getElementById("gallery-lightbox");
    lightboxImg = document.getElementById("lightbox-image");
    lightboxCaption = document.getElementById("lightbox-caption");
    closeBtn = document.getElementById("lightbox-close");
    prevBtn = document.getElementById("lightbox-prev");
    nextBtn = document.getElementById("lightbox-next");

    // Attach event listeners
    closeBtn.addEventListener("click", close);
    prevBtn.addEventListener("click", prev);
    nextBtn.addEventListener("click", next);

    // Close on background click
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox) close();
    });

    // Keyboard navigation
    document.addEventListener("keydown", handleKeyboard);
  }

  /**
   * Attach click listeners to gallery images
   */
  function attachGalleryListeners() {
    // Find all gallery containers
    const galleries = document.querySelectorAll("[data-gallery]");

    galleries.forEach((gallery) => {
      const images = gallery.querySelectorAll("img[data-full]");
      images.forEach((img, index) => {
        img.style.cursor = "pointer";
        img.addEventListener("click", () => {
          open(gallery.dataset.gallery, index);
        });
      });
    });
  }

  /**
   * Open gallery at specific index
   * @param {string} galleryId - Gallery identifier
   * @param {number} index - Starting image index
   */
  function open(galleryId, index = 0) {
    const gallery = document.querySelector(`[data-gallery="${galleryId}"]`);
    if (!gallery) {
      console.error(`Gallery not found: ${galleryId}`);
      return;
    }

    // Collect all images from gallery
    const imgElements = gallery.querySelectorAll("img[data-full]");
    images = Array.from(imgElements).map((img) => ({
      full: img.dataset.full,
      thumb: img.src,
      caption: img.alt || img.dataset.caption || "",
    }));

    if (images.length === 0) return;

    currentIndex = Math.min(index, images.length - 1);
    isOpen = true;

    updateImage();
    lightbox.classList.remove("hidden");
    document.body.style.overflow = "hidden";

    // Dispatch custom event
    lightbox.dispatchEvent(
      new CustomEvent("gallery:open", {
        detail: { galleryId, index },
      })
    );
  }

  /**
   * Close gallery
   */
  function close() {
    isOpen = false;
    lightbox.classList.add("hidden");
    document.body.style.overflow = "";

    // Dispatch custom event
    lightbox.dispatchEvent(new CustomEvent("gallery:close"));
  }

  /**
   * Navigate to previous image
   */
  function prev() {
    currentIndex = currentIndex > 0 ? currentIndex - 1 : images.length - 1;
    updateImage();
  }

  /**
   * Navigate to next image
   */
  function next() {
    currentIndex = currentIndex < images.length - 1 ? currentIndex + 1 : 0;
    updateImage();
  }

  /**
   * Go to specific image
   * @param {number} index - Image index
   */
  function goTo(index) {
    if (index >= 0 && index < images.length) {
      currentIndex = index;
      updateImage();
    }
  }

  /**
   * Update displayed image
   */
  function updateImage() {
    const image = images[currentIndex];
    if (!image) return;

    // Preload next image
    if (currentIndex < images.length - 1) {
      const preload = new Image();
      preload.src = images[currentIndex + 1].full;
    }

    lightboxImg.src = image.full;
    lightboxImg.alt = image.caption;
    lightboxCaption.textContent = image.caption;

    // Update counter
    const counter = document.getElementById("lightbox-counter");
    if (counter) {
      counter.textContent = `${currentIndex + 1} / ${images.length}`;
    }
  }

  /**
   * Handle keyboard navigation
   * @param {KeyboardEvent} e
   */
  function handleKeyboard(e) {
    if (!isOpen) return;

    switch (e.key) {
      case "Escape":
        close();
        break;
      case "ArrowLeft":
        prev();
        break;
      case "ArrowRight":
        next();
        break;
    }
  }

  /**
   * Add images to gallery dynamically
   * @param {string} galleryId - Gallery identifier
   * @param {Array} newImages - Array of image objects
   */
  function addImages(galleryId, newImages) {
    const gallery = document.querySelector(`[data-gallery="${galleryId}"]`);
    if (!gallery) return;

    newImages.forEach((imgData) => {
      const img = document.createElement("img");
      img.src = imgData.thumb || imgData.full;
      img.dataset.full = imgData.full;
      img.alt = imgData.caption || "";
      img.dataset.caption = imgData.caption || "";
      img.className = imgData.class || "w-full h-48 object-cover rounded-lg cursor-pointer";

      img.addEventListener("click", () => {
        const index = gallery.querySelectorAll("img[data-full]").length;
        open(galleryId, index);
      });

      gallery.appendChild(img);
    });
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Public API
  return {
    open,
    close,
    prev,
    next,
    goTo,
    addImages,
    init,
    isOpen: () => isOpen,
    getCurrentIndex: () => currentIndex,
  };
})();

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = GallerySystem;
}

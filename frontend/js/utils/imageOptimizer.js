/**
 * Image Optimizer - Lazy loading and responsive images
 * Handles WebP conversion, srcset generation, and lazy loading
 */

const ImageOptimizer = (function () {
  "use strict";

  // Configuration
  const config = {
    lazyLoadThreshold: 200, // pixels before viewport
    webpSupported: null,
    rootMargin: "50px",
    quality: 80,
    breakpoints: [320, 640, 768, 1024, 1280, 1920],
  };

  // Check WebP support
  function checkWebPSupport() {
    if (config.webpSupported !== null) {
      return config.webpSupported;
    }

    const webpData =
      "data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoCAAEAAQAcJaQAA3AA/v3AgAA=";

    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        config.webpSupported = true;
        resolve(true);
      };
      img.onerror = () => {
        config.webpSupported = false;
        resolve(false);
      };
      img.src = webpData;
    });
  }

  // Generate srcset for responsive images
  function generateSrcset(imageUrl, breakpoints = config.breakpoints) {
    if (!imageUrl || imageUrl.startsWith("data:")) {
      return "";
    }

    // Check if URL already has parameters
    const separator = imageUrl.includes("?") ? "&" : "?";
    const baseUrl = imageUrl.split("?")[0];
    const ext = baseUrl.split(".").pop().split("?")[0];

    // Generate srcset for each breakpoint
    const srcset = breakpoints
      .map((width) => {
        const url = `${baseUrl}${separator}w=${width}&q=${config.quality}`;
        return `${url} ${width}w`;
      })
      .join(", ");

    return srcset;
  }

  // Generate WebP URL
  function getWebPUrl(imageUrl) {
    if (!imageUrl || !config.webpSupported) {
      return imageUrl;
    }

    // Already WebP
    if (imageUrl.includes(".webp")) {
      return imageUrl;
    }

    // Add WebP format parameter (adjust based on your image CDN/server)
    const separator = imageUrl.includes("?") ? "&" : "?";
    return `${imageUrl}${separator}fmt=webp`;
  }

  // Lazy load image
  function lazyLoadImage(img) {
    const src = img.dataset.src;
    const srcset = img.dataset.srcset;
    const fallbackSrc = img.dataset.fallback;

    if (!src) return;

    // If WebP is supported, try to use WebP version
    if (config.webpSupported && !src.includes(".webp")) {
      const webpSrc = getWebPUrl(src);
      img.src = webpSrc;
    } else {
      img.src = src;
    }

    // Set srcset if available
    if (srcset) {
      if (config.webpSupported) {
        // Convert srcset URLs to WebP
        const webpSrcset = srcset
          .split(",")
          .map((s) => {
            const [url, size] = s.trim().split(" ");
            return `${getWebPUrl(url)} ${size}`;
          })
          .join(", ");
        img.srcset = webpSrcset;
      } else {
        img.srcset = srcset;
      }
    }

    // Set fallback for older browsers
    if (fallbackSrc) {
      img.onerror = () => {
        img.src = fallbackSrc;
      };
    }

    // Add loaded class
    img.addEventListener("load", () => {
      img.classList.add("lazy-loaded");
      img.classList.remove("lazy-loading");
    });

    img.classList.remove("lazy-placeholder");
    img.removeAttribute("data-src");
    img.removeAttribute("data-srcset");
  }

  // Initialize lazy loading with IntersectionObserver
  function initLazyLoading() {
    // Check WebP support first
    checkWebPSupport().then(() => {
      const lazyImages = document.querySelectorAll("img[data-lazy], img[data-src]");

      if (!("IntersectionObserver" in window)) {
        // Fallback for older browsers
        lazyImages.forEach(lazyLoadImage);
        return;
      }

      const observer = new IntersectionObserver(
        (entries, observer) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              lazyLoadImage(entry.target);
              observer.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: `${config.lazyLoadThreshold}px`,
          threshold: 0,
        }
      );

      lazyImages.forEach((img) => {
        img.classList.add("lazy-loading");
        observer.observe(img);
      });
    });
  }

  // Add responsive image attributes
  function addResponsiveAttributes(img, options = {}) {
    const { src, breakpoints = config.breakpoints, sizes } = options;

    if (!src) return;

    // Add data-src for lazy loading
    img.dataset.src = src;

    // Generate srcset if not already present
    if (!img.dataset.srcset) {
      const srcset = generateSrcset(src, breakpoints);
      if (srcset) {
        img.dataset.srcset = srcset;
      }
    }

    // Set sizes attribute
    if (sizes) {
      img.sizes = sizes;
    } else {
      // Default sizes
      img.sizes = "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw";
    }

    // Add placeholder while loading
    if (!img.src || img.src === window.location.href) {
      img.src =
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E";
      img.classList.add("lazy-placeholder");
    }
  }

  // Create responsive image element
  function createResponsiveImage(options = {}) {
    const {
      src,
      alt = "",
      breakpoints = config.breakpoints,
      sizes,
      className = "",
      loading = "lazy",
    } = options;

    const img = document.createElement("img");
    img.alt = alt;
    img.className = className;
    img.loading = loading;

    addResponsiveAttributes(img, { src, breakpoints, sizes });

    return img;
  }

  // Preload critical images
  function preloadImage(src) {
    const link = document.createElement("link");
    link.rel = "preload";
    link.as = "image";
    link.href = src;
    document.head.appendChild(link);
  }

  // Optimize all images on page
  function optimizeAllImages() {
    const images = document.querySelectorAll("img:not([data-optimized])");

    images.forEach((img) => {
      if (img.dataset.src || img.dataset.lazy) return;

      // Skip if already has srcset or is lazy loaded
      if (img.srcset || img.loading === "lazy") return;

      // Skip small images (icons, etc.)
      if (img.naturalWidth < 100 || img.naturalHeight < 100) return;

      img.dataset.optimized = "true";
      addResponsiveAttributes(img, { src: img.src });
    });
  }

  // Initialize
  function init() {
    initLazyLoading();
    optimizeAllImages();

    // Re-run on DOM changes (for dynamically added images)
    if ("MutationObserver" in window) {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) {
              // Element node
              if (node.tagName === "IMG") {
                if (node.dataset.src || node.dataset.lazy) {
                  initLazyLoading();
                }
              } else {
                const images = node.querySelectorAll?.("img");
                images?.forEach((img) => {
                  if (!img.dataset.optimized) {
                    addResponsiveAttributes(img, { src: img.src });
                  }
                });
              }
            }
          });
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });
    }

    console.log("✅ ImageOptimizer initialized");
  }

  // Auto-initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Public API
  return {
    init,
    generateSrcset,
    getWebPUrl,
    addResponsiveAttributes,
    createResponsiveImage,
    preloadImage,
    optimizeAllImages,
    checkWebPSupport,
  };
})();

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = ImageOptimizer;
}

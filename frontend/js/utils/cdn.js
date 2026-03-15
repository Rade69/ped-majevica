/**
 * CDN Configuration for PED Majevica
 * Handles static asset delivery through CDN
 */

const CDNConfig = (function () {
  "use strict";

  // CDN Configuration
  const config = {
    // CDN base URL (change for production)
    baseUrl: "", // e.g., "https://cdn.pedmajevica.org"

    // Enable CDN in production
    enabled: process.env.NODE_ENV === "production",

    // Asset paths
    paths: {
      images: "/images",
      css: "/css",
      js: "/js",
      fonts: "/fonts",
      blog: "/images/blog",
      gallery: "/images/gallery",
      trails: "/images/trails",
      hero: "/images/hero",
    },

    // Image optimization options
    images: {
      quality: 80,
      format: "webp",
      breakpoints: [320, 640, 768, 1024, 1280],
    },
  };

  /**
   * Get CDN URL for a static asset
   * @param {string} path - Asset path relative to static folder
   * @returns {string} - Full CDN URL or relative path
   */
  function getAssetUrl(path) {
    if (!config.enabled || !config.baseUrl) {
      return path;
    }

    // Already full URL
    if (path.startsWith("http")) {
      return path;
    }

    return `${config.baseUrl}${path}`;
  }

  /**
   * Get optimized image URL
   * @param {string} path - Image path
   * @param {object} options - Image options
   * @returns {string} - Optimized image URL
   */
  function getImageUrl(path, options = {}) {
    if (!path) return "";

    // Skip data URLs
    if (path.startsWith("data:")) {
      return path;
    }

    const { width, quality, format } = {
      width: options.width || null,
      quality: options.quality || config.images.quality,
      format: options.format || (supportsWebP() ? config.images.format : "jpeg"),
      ...options,
    };

    // Build CDN URL with transformation parameters
    let url = getAssetUrl(path);

    // If using image CDN (Cloudinary, Imgix, etc.)
    if (config.enabled && config.imageCdn) {
      const params = [];
      if (width) params.push(`w=${width}`);
      if (quality) params.push(`q=${quality}`);
      if (format) params.push(`fmt=${format}`);

      if (params.length > 0) {
        const separator = url.includes("?") ? "&" : "?";
        url = `${url}${separator}${params.join("&")}`;
      }
    }

    return url;
  }

  /**
   * Check if WebP is supported
   * @returns {boolean}
   */
  function supportsWebP() {
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL("image/webp").startsWith("data:image/webp");
  }

  /**
   * Generate srcset for responsive images
   * @param {string} path - Image path
   * @param {Array} breakpoints - Array of widths
   * @returns {string} - srcset attribute value
   */
  function generateSrcSet(path, breakpoints = config.images.breakpoints) {
    if (!path || path.startsWith("data:")) {
      return "";
    }

    return breakpoints
      .map((width) => `${getImageUrl(path, { width })} ${width}w`)
      .join(", ");
  }

  /**
   * Preload critical assets
   * @param {Array} assets - Array of asset paths
   */
  function preloadAssets(assets) {
    assets.forEach((asset) => {
      const link = document.createElement("link");
      link.rel = "preload";

      // Determine as based on file extension
      if (asset.endsWith(".css")) {
        link.as = "style";
      } else if (asset.endsWith(".js")) {
        link.as = "script";
      } else if (/\.(jpg|jpeg|png|webp|svg|gif)$/i.test(asset)) {
        link.as = "image";
      }

      link.href = getAssetUrl(asset);
      document.head.appendChild(link);
    });
  }

  /**
   * Initialize CDN with custom configuration
   * @param {object} customConfig - Custom configuration overrides
   */
  function init(customConfig = {}) {
    // Merge custom config
    Object.assign(config, customConfig);

    // Check for CDN environment variable
    if (process.env.CDN_URL) {
      config.baseUrl = process.env.CDN_URL;
      config.enabled = true;
    }

    console.log(
      `✅ CDN initialized: ${config.enabled ? "enabled" : "disabled"}`,
      config.baseUrl ? `@ ${config.baseUrl}` : ""
    );
  }

  // Public API
  return {
    config,
    init,
    getAssetUrl,
    getImageUrl,
    generateSrcSet,
    preloadAssets,
    supportsWebP,
  };
})();

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = CDNConfig;
}

/**
 * ============================================
 * API CONFIGURATION
 * ============================================
 * Centralized API endpoint configuration
 * Supports both development and production
 */

const API_CONFIG = {
  // Production backend URL (Render.com)
  PRODUCTION_API: 'https://ped-majevica.onrender.com',

  // Development backend URL (local Flask server)
  DEVELOPMENT_API: 'http://127.0.0.1:5000',

  // Auto-detect environment
  get BASE_URL() {
    // If running on localhost, use development API
    if (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.port === '8080' ||
        window.location.port === '5500') {
      return this.DEVELOPMENT_API;
    }

    // Production domains (Netlify or custom domain)
    return this.PRODUCTION_API;
  },

  // API endpoints
  ENDPOINTS: {
    POSTS: '/api/posts',
    TRAILS: '/api/trails',
    EVENTS: '/api/events',
    LOGIN: '/api/login',
    LOGOUT: '/api/logout',
  },

  // Helper method to get full URL
  getUrl(endpoint) {
    return this.BASE_URL + endpoint;
  }
};

// Export for use in other scripts
window.API_CONFIG = API_CONFIG;

/**
 * ============================================
 * API CONFIGURATION
 * ============================================
 * Centralized API endpoint configuration with CSRF and credentials support
 * Supports both development and production
 */

const API_CONFIG = (function() {
  'use strict';

  // Default configuration
  const config = {
    // Production backend URL (Render.com)
    PRODUCTION_API: 'https://ped-majevica-backend.onrender.com',

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
      CSRF_TOKEN: '/api/csrf-token',
      PASSWORD_RESET_REQUEST: '/api/password-reset-request',
      PASSWORD_RESET_CONFIRM: '/api/password-reset-confirm',
      CHANGE_PASSWORD: '/api/change-password',
    },

    // CORS credentials mode
    credentials: 'include', // 'include' for cross-origin, 'same-origin' for same origin
    
    // Default headers
    defaultHeaders: {
      'Content-Type': 'application/json',
    },
    
    // CSRF token
    csrfToken: null,
    
    // Environment
    env: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'development' : 'production',
    
    // Debug mode
    debug: false,
  };
  
  // Public API
  return {
    // Legacy properties for backward compatibility
    get PRODUCTION_API() { return config.PRODUCTION_API; },
    get DEVELOPMENT_API() { return config.DEVELOPMENT_API; },
    get BASE_URL() { return config.BASE_URL; },
    get ENDPOINTS() { return config.ENDPOINTS; },
    
    // New methods and properties
    getUrl(endpoint) {
      return config.BASE_URL + endpoint;
    },
    
    getCsrfToken() {
      // Try to get from cookie first
      const cookieToken = this._getCsrfTokenFromCookie();
      if (cookieToken) {
        config.csrfToken = cookieToken;
        return cookieToken;
      }
      
      // Return stored token
      return config.csrfToken;
    },
    
    setCsrfToken(token) {
      config.csrfToken = token;
      // Also set in cookie for compatibility
      document.cookie = `csrf_token=${token}; path=/; SameSite=Lax`;
    },
    
    async fetchCsrfToken() {
      try {
        const response = await fetch(this.getUrl(this.ENDPOINTS.CSRF_TOKEN), {
          credentials: config.credentials,
        });
        
        if (response.ok) {
          const data = await response.json();
          const token = data.csrf_token;
          this.setCsrfToken(token);
          return token;
        }
        return null;
      } catch (error) {
        console.error('Failed to fetch CSRF token:', error);
        return null;
      }
    },
    
    getHeaders(additionalHeaders = {}) {
      const headers = { ...config.defaultHeaders, ...additionalHeaders };
      
      // Add CSRF token if available (for state-changing methods)
      const csrfToken = this.getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      return headers;
    },
    
    getCredentials() {
      return config.credentials;
    },
    
    // Helper method for fetch requests
    async fetchWithAuth(endpoint, options = {}) {
      const url = endpoint.startsWith('http') ? endpoint : this.getUrl(endpoint);
      const headers = this.getHeaders(options.headers);
      const credentials = this.getCredentials();
      
      return fetch(url, {
        credentials,
        headers,
        ...options,
      });
    },
    
    // Private method
    _getCsrfTokenFromCookie() {
      const name = 'csrf_token=';
      const decodedCookie = decodeURIComponent(document.cookie);
      const ca = decodedCookie.split(';');
      
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
          return c.substring(name.length, c.length);
        }
      }
      return null;
    },
    
    // Configuration getters/setters
    getConfig() {
      return { ...config };
    },
    
    updateConfig(updates) {
      Object.assign(config, updates);
      if (config.debug) {
        console.log('API_CONFIG updated:', config);
      }
    },
    
    // Initialize (call early)
    init() {
      if (config.env === 'development') {
        config.debug = true;
      }
      
      // Auto-fetch CSRF token on initialization
      // Note: This is async but we don't wait for it
      this.fetchCsrfToken().then(token => {
        if (token && config.debug) {
          console.log('API_CONFIG: CSRF token auto-fetched');
        }
      });
      
      if (config.debug) {
        console.log('API_CONFIG initialized:', {
          BASE_URL: config.BASE_URL,
          env: config.env,
          credentials: config.credentials,
        });
      }
      
      return this;
    },
  };
})();

// Initialize and export
window.API_CONFIG = API_CONFIG.init();

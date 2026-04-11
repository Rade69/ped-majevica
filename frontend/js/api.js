// frontend/js/api.js
// Centralizovani API sloj za PED Majevica
// Koristi Config iz config.js za podešavanja

/**
 * Custom error klasa za API greške
 */
export class ApiError extends Error {
  constructor(message, statusCode, data = null) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.data = data;
  }
}

/**
 * Prikazivanje notifikacija korisniku
 */
function showNotification(message, type = 'info') {
  // Proveri da li postoji notification container
  let container = document.getElementById('notification-container');
  
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;max-width:400px;';
    document.body.appendChild(container);
  }
  
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.style.cssText = `
    padding: 12px 16px;
    margin-bottom: 10px;
    border-radius: 4px;
    color: white;
    font-size: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    background-color: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
  `;
  notification.textContent = message;
  
  container.appendChild(notification);
  
  // Automatsko uklanjanje nakon 5 sekundi
  setTimeout(() => {
    notification.remove();
  }, 5000);
}

/**
 * Centralizovana request funkcija sa poboljšanim error handling-om
 * Koristi API_CONFIG za base URL, credentials i CSRF token
 */
async function request(endpoint, options = {}) {
  try {
    // Get URL from API_CONFIG (handles absolute/relative paths)
    const url = endpoint.startsWith('http') 
      ? endpoint  // Absolute URL
      : window.API_CONFIG?.getUrl(endpoint) || endpoint; // Use API_CONFIG or fallback
    
    // Get headers from API_CONFIG (includes CSRF token)
    const headers = window.API_CONFIG?.getHeaders(options.headers) || {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    
    // Use credentials from API_CONFIG (defaults to 'include' for cross-origin)
    const credentials = window.API_CONFIG?.getCredentials() || 'include';
    
    const res = await fetch(url, {
      credentials,
      headers,
      ...options,
    });

    // Parsiranje response-a
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const errorMessage = data?.message || data?.error || data?.message || res.statusText;
      const statusCode = res.status;
      
      // Logovanje greške
      console.error(`API Greška [${statusCode}]:`, errorMessage, 'URL:', url);
      
      // Prikazivanje korisničkih poruka za specifične status code-ove
      if (statusCode === 401) {
        showNotification('Vaša sesija je istekla. Molimo vas da se ponovo prijavite.', 'error');
        // Redirect na login stranicu nakon 2 sekunde
        setTimeout(() => {
          window.location.href = '/pages/login.html';
        }, 2000);
      } else if (statusCode === 403) {
        showNotification('Nemate dozvolu za ovu operaciju.', 'error');
      } else if (statusCode >= 500) {
        showNotification('Došlo je do greške na serveru. Pokušajte ponovo kasnije.', 'error');
      } else if (statusCode === 429) {
        showNotification('Previše zahteva. Sačekajte trenutak i pokušajte ponovo.', 'error');
      } else {
        // Generic error message
        showNotification(errorMessage || 'Došlo je do greške. Pokušajte ponovo.', 'error');
      }
      
      throw new ApiError(errorMessage, statusCode, data);
    }

    // Return null za 204 No Content
    if (res.status === 204) return null;
    
    return data;
    
  } catch (error) {
    // Mrežne greške (nema konekcije)
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      console.error('Mrežna greška: Proverite internet konekciju');
      showNotification('Nema konekcije sa serverom. Proverite internet.', 'error');
    }
    
    // Re-throw za dalje handle-ovanje
    throw error;
  }
}

/* ======================
   POSTS API
====================== */
export const PostsAPI = {
  list() {
    return request("posts/");
  },

  create(data) {
    return request("posts/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update(id, data) {
    return request(`posts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  remove(id) {
    return request(`posts/${id}`, {
      method: "DELETE",
    });
  },
};

/* ======================
   TRAILS API
====================== */
export const TrailsAPI = {
  list() {
    return request("trails/");
  },
};

/* ======================
   EVENTS API
====================== */
export const EventsAPI = {
  list() {
    return request("events/");
  },
};

/* ======================
   AUTH API
====================== */
export const AuthAPI = {
  login(username, password) {
    return request("login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },
  
  logout() {
    return request("logout", { method: "GET" });
  },
  
  changePassword(currentPassword, newPassword, confirmPassword) {
    return request("change-password", {
      method: "POST",
      body: JSON.stringify({ 
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword 
      }),
    });
  },
  
  requestPasswordReset(email) {
    return request("password-reset-request", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
  },
  
  resetPassword(token, newPassword, confirmPassword) {
    return request("password-reset-confirm", {
      method: "POST",
      body: JSON.stringify({ 
        token, 
        new_password: newPassword,
        confirm_password: confirmPassword 
      }),
    });
  },
};

/* ======================
   UTILITY FUNCTIONS
====================== */
/**
 * Fetch CSRF token from server
 * @returns {Promise<string>} CSRF token
 */
export async function fetchCsrfToken() {
  try {
    // Use API_CONFIG's fetchCsrfToken method if available
    if (window.API_CONFIG && window.API_CONFIG.fetchCsrfToken) {
      return await window.API_CONFIG.fetchCsrfToken();
    }
    
    // Fallback to direct request
    const response = await request("csrf-token", { method: "GET" });
    return response.csrf_token;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    return null;
  }
}

/**
 * Initialize CSRF token and store it globally
 * Should be called early in application startup
 */
export async function initCsrfToken() {
  const token = await fetchCsrfToken();
  if (token) {
    // Store in global CSRF object (compatible with app.js)
    if (!window.CSRF) window.CSRF = {};
    window.CSRF.token = token;
    
    // Also set in API_CONFIG for consistency
    if (window.API_CONFIG && window.API_CONFIG.setCsrfToken) {
      window.API_CONFIG.setCsrfToken(token);
    }
    
    console.log('CSRF token initialized');
    return token;
  }
  return null;
}

// frontend/js/admin/api.js
// Centralizovani API sloj za admin panel

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
 */
async function request(url, options = {}) {
  try {
    const res = await fetch(url, {
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });

    // Parsiranje response-a
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const errorMessage = data?.message || data?.error || data?.message || res.statusText;
      const statusCode = res.status;
      
      // Logovanje greške
      console.error(`API Greška [${statusCode}]:`, errorMessage);
      
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
    return request("/api/posts/");
  },

  create(data) {
    return request("/api/posts/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  update(id, data) {
    return request(`/api/posts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  remove(id) {
    return request(`/api/posts/${id}`, {
      method: "DELETE",
    });
  },
};

/* ======================
   TRAILS API
====================== */
export const TrailsAPI = {
  list() {
    return request("/api/trails/");
  },
};

/* ======================
   EVENTS API
====================== */
export const EventsAPI = {
  list() {
    return request("/api/events/");
  },
};

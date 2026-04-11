// trails.js - Dynamic Trail Loading with Pagination
// ===================================================

(function() {
  'use strict';

// Bezbedna konfiguracija API endpoint-a sa fallback-om
const TRAILS_API = (function() {
    // Prvo pokušaj da koristiš centralnu konfiguraciju
    if (window.API_CONFIG && typeof window.API_CONFIG.getUrl === 'function') {
        console.log('✅ trails.js: Koristim API_CONFIG');
        return window.API_CONFIG.getUrl(window.API_CONFIG.ENDPOINTS.TRAILS);
    }
    
    // Fallback za razvojno okruženje - koristi absolutni URL za localhost
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (isLocalhost) {
        console.log('⚠️ trails.js: API_CONFIG nije dostupan, koristim development URL (localhost:5000)');
        return 'http://localhost:5000/api/trails';
    }
    
    // Fallback za produkciju - relativni put
    console.log('⚠️ trails.js: API_CONFIG nije dostupan, koristim relativni put');
    return '/api/trails';
})();

let allTrails = [];
let displayedTrails = [];
let currentFilter = 'all';
const TRAILS_PER_PAGE = 3;
let currentPage = 1;

// Load trails from backend
async function loadTrails() {
  try {
    console.log('🏔️ Učitavanje staza sa:', TRAILS_API);
    // Use credentials for cross-origin requests
    const fetchOptions = {};
    if (window.API_CONFIG && window.API_CONFIG.getCredentials) {
      fetchOptions.credentials = window.API_CONFIG.getCredentials();
    } else {
      fetchOptions.credentials = 'include';
    }
    const response = await fetch(TRAILS_API, fetchOptions);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    allTrails = data.trails || [];

    // Sort trails by custom order: Velika Staza-Tavna, Herojeva staza, Novakova pećina
    const trailOrder = ['Velika Staza-Tavna', 'Herojeva staza', 'Novakova pećina'];
    allTrails.sort((a, b) => {
      const indexA = trailOrder.findIndex(name => a.name.includes(name) || name.includes(a.name));
      const indexB = trailOrder.findIndex(name => b.name.includes(name) || name.includes(b.name));
      // If found in order list, use that order. Otherwise put at end.
      const orderA = indexA === -1 ? 999 : indexA;
      const orderB = indexB === -1 ? 999 : indexB;
      return orderA - orderB;
    });

    // Expose trails data globally for trail modal
    window.trailsDataFromAPI = allTrails;
    console.log(`✅ Učitano ${allTrails.length} staza`);

    // Initial render - show first 3 trails
    currentPage = 1;
    filterAndRenderTrails(currentFilter);

  } catch (error) {
    console.error('❌ Greška pri učitavanju staza:', error);
    console.error('❌ Error details:', {
      message: error.message,
      stack: error.stack,
      api: TRAILS_API
    });
    showTrailsError();
  }
}

// Filter trails by difficulty
function filterAndRenderTrails(difficulty) {
  currentFilter = difficulty;
  currentPage = 1; // Reset to page 1 when filtering

  // Filter trails
  if (difficulty === 'all') {
    displayedTrails = [...allTrails];
  } else {
    displayedTrails = allTrails.filter(trail => {
      const diff = trail.difficulty.toLowerCase();
      return diff === difficulty || diff === difficulty.toLowerCase();
    });
  }

  console.log(`🔍 Filter: ${difficulty}, prikazano: ${displayedTrails.length} staza`);

  // Render trails
  renderTrails();
  updateLoadMoreButton();
}

// Render trails to container
function renderTrails() {
  const container = document.getElementById('trailsContainer');
  if (!container) return;

  const trailsToShow = displayedTrails.slice(0, currentPage * TRAILS_PER_PAGE);

  if (trailsToShow.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12">
        <i class="fas fa-hiking text-gray-300 text-6xl mb-4"></i>
        <p class="text-gray-500 text-xl">Nema staza za prikaz</p>
      </div>
    `;
    return;
  }

  container.innerHTML = trailsToShow.map(trail => createTrailCard(trail)).join('');

  // Lazy load images
  lazyLoadImages();
}

// Create trail card HTML
function createTrailCard(trail) {
  const difficultyBadge = getDifficultyBadge(trail.difficulty);
  const difficultyClass = getDifficultyClass(trail.difficulty);

  return `
    <div class="trail-card group bg-white rounded-2xl overflow-hidden shadow-2xl hover:shadow-[0_25px_50px_-12px_rgba(0,0,0,0.35)] transition-all duration-500 border-b-4 ${difficultyClass}"
      data-difficulty="${trail.difficulty.toLowerCase()}" data-region="majevica">
      <div class="relative h-48 sm:h-56 md:h-64 overflow-hidden">
        <!-- Difficulty Badge -->
        ${difficultyBadge}
        <!-- Year Badge -->
        <div class="absolute top-4 left-4 bg-secondary-gold text-primary-blue px-3 py-1 rounded-full text-xs font-bold">
          ${new Date(trail.created_at).getFullYear()}
        </div>
        <img
          src="${trail.image_url || '/assets/images/trails/placeholder-trail.webp'}"
          data-src="${trail.image_url || '/assets/images/trails/placeholder-trail.webp'}"
          alt="${trail.name}"
          loading="lazy"
          class="lazy-image w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
          width="800" height="450">
      </div>
      <div class="p-6">
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-xl font-bold text-primary-blue group-hover:text-primary-red transition-colors">
            ${trail.name}
          </h3>
          <div class="flex items-center text-secondary-gold">
            ${generateStars(trail.rating || 4.5)}
          </div>
        </div>
        <p class="text-gray-600 mb-6 line-clamp-3">
          ${trail.description}
        </p>
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="flex items-center text-gray-700">
            <div class="w-8 h-8 rounded-full bg-primary-blue/10 flex items-center justify-center mr-2">
              <i class="fas fa-road text-primary-blue"></i>
            </div>
            <div>
              <div class="font-bold text-primary-blue">${trail.distance_km} km</div>
              <div class="text-xs text-gray-500">Dužina</div>
            </div>
          </div>
          <div class="flex items-center text-gray-700">
            <div class="w-8 h-8 rounded-full bg-primary-red/10 flex items-center justify-center mr-2">
              <i class="fas fa-clock text-primary-red"></i>
            </div>
            <div>
              <div class="font-bold text-primary-red">${trail.duration_hours} h</div>
              <div class="text-xs text-gray-500">Vrijeme</div>
            </div>
          </div>
        </div>
        <div class="flex justify-between items-center">
          <button type="button"
            class="view-trail-btn px-5 py-2 bg-primary-red hover:bg-red-dark text-white rounded-lg font-medium transition-all hover:scale-105"
            data-trail-id="${trail.id}">
            Detalji <i class="fas fa-info-circle ml-2" aria-hidden="true"></i>
          </button>
          <div class="flex space-x-2">
            ${trail.gpx_file_url ? `
              <a href="${trail.gpx_file_url}" download
                class="w-10 h-10 rounded-full border-2 border-primary-blue text-primary-blue hover:bg-primary-blue hover:text-white transition-all flex items-center justify-center"
                aria-label="Preuzmi GPX fajl za ${trail.name}"
                title="Preuzmi GPS podatke">
                <i class="fas fa-download" aria-hidden="true"></i>
              </a>
            ` : ''}
            <button type="button"
              class="w-10 h-10 rounded-full border-2 border-secondary-blue text-secondary-blue hover:bg-secondary-blue hover:text-white transition-all flex items-center justify-center"
              aria-label="Dodaj ${trail.name} u omiljene"
              title="Sačuvaj ovu stazu u omiljene">
              <i class="far fa-heart" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

// Get difficulty badge HTML
function getDifficultyBadge(difficulty) {
  const diff = difficulty.toLowerCase();

  if (diff === 'lagana' || diff === 'laka') {
    return `
      <div class="absolute top-4 right-4 bg-gradient-to-r from-green-500 to-green-600 text-white px-4 py-1 rounded-full text-sm font-bold flex items-center">
        <i class="fas fa-hiking mr-2" aria-hidden="true"></i> Lagana
      </div>
    `;
  } else if (diff === 'srednja') {
    return `
      <div class="absolute top-4 right-4 bg-gradient-to-r from-orange-500 to-orange-600 text-white px-4 py-1 rounded-full text-sm font-bold flex items-center">
        <i class="fas fa-signal mr-2"></i> Srednja
      </div>
    `;
  } else if (diff === 'teška' || diff === 'teska') {
    return `
      <div class="absolute top-4 right-4 bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-1 rounded-full text-sm font-bold flex items-center">
        <i class="fas fa-skull-crossbones mr-2"></i> Teška
      </div>
    `;
  }

  return `
    <div class="absolute top-4 right-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white px-4 py-1 rounded-full text-sm font-bold flex items-center">
      <i class="fas fa-tree mr-2" aria-hidden="true"></i> Rekreativna
    </div>
  `;
}

// Get difficulty border class
function getDifficultyClass(difficulty) {
  const diff = difficulty.toLowerCase();

  if (diff === 'lagana' || diff === 'laka') {
    return 'border-green-500';
  } else if (diff === 'srednja') {
    return 'border-primary-red';
  } else if (diff === 'teška' || diff === 'teska') {
    return 'border-red-600';
  }

  return 'border-secondary-blue';
}

// Generate star rating HTML
function generateStars(rating) {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

  let stars = '';

  for (let i = 0; i < fullStars; i++) {
    stars += '<i class="fas fa-star"></i>';
  }

  if (hasHalfStar) {
    stars += '<i class="fas fa-star-half-alt ml-1"></i>';
  }

  for (let i = 0; i < emptyStars; i++) {
    stars += '<i class="far fa-star ml-1"></i>';
  }

  return stars;
}

// Update Load More button visibility
function updateLoadMoreButton() {
  const button = document.getElementById('loadMoreTrails');
  if (!button) return;

  const totalShown = currentPage * TRAILS_PER_PAGE;
  const hasMore = totalShown < displayedTrails.length;

  if (hasMore) {
    button.style.display = 'inline-flex';
    button.innerHTML = `
      Učitaj još staza
      <i class="fas fa-arrow-down ml-3 group-hover:translate-y-1 transition-transform" aria-hidden="true"></i>
    `;
  } else if (displayedTrails.length > TRAILS_PER_PAGE) {
    button.style.display = 'inline-flex';
    button.innerHTML = `
      <i class="fas fa-check mr-3" aria-hidden="true"></i>
      Sve staze prikazane (${displayedTrails.length})
    `;
    button.disabled = true;
    button.classList.add('opacity-50', 'cursor-not-allowed');
  } else {
    button.style.display = 'none';
  }
}

// Show error message
function showTrailsError() {
  const container = document.getElementById('trailsContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="col-span-full text-center py-12 bg-red-50 rounded-xl">
      <i class="fas fa-exclamation-triangle text-red-500 text-6xl mb-4"></i>
      <p class="text-red-700 text-xl font-semibold mb-2">Greška pri učitavanju staza</p>
      <p class="text-red-600">Molimo pokušajte kasnije</p>
    </div>
  `;
}

// Lazy load images
function lazyLoadImages() {
  const images = document.querySelectorAll('.lazy-image');

  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.getAttribute('data-src');

        if (src) {
          img.src = src;
          img.classList.add('loaded');
        }

        observer.unobserve(img);
      }
    });
  });

  images.forEach(img => imageObserver.observe(img));
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
  console.log('🔷 trails.js: DOMContentLoaded event fired');
  console.log('🔷 trails.js: API_CONFIG =', window.API_CONFIG);
  console.log('🔷 trails.js: TRAILS_API =', TRAILS_API);

  // Load trails on page load
  loadTrails();

  // Filter buttons
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(button => {
    button.addEventListener('click', function() {
      const filter = this.getAttribute('data-filter');

      // Update active button
      filterButtons.forEach(btn => {
        btn.classList.remove('bg-primary-blue', 'text-white');
        btn.classList.add('bg-white', 'text-gray-600');
      });

      this.classList.remove('bg-white', 'text-gray-600');
      this.classList.add('bg-primary-blue', 'text-white');

      // Filter and render
      filterAndRenderTrails(filter);
    });
  });

  // Load More button
  const loadMoreBtn = document.getElementById('loadMoreTrails');
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', function() {
      if (!this.disabled) {
        currentPage++;
        renderTrails();
        updateLoadMoreButton();

        // Smooth scroll to new content
        setTimeout(() => {
          const lastCard = document.querySelectorAll('.trail-card')[currentPage * TRAILS_PER_PAGE - 1];
          if (lastCard) {
            lastCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 100);
      }
    });
  }
});

})(); // End of IIFE

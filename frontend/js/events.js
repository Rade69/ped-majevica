// events.js - Dynamic Event Loading from JSON with Auto-Refresh
// =============================================================

(function() {
  'use strict';

const JSON_PATH = '/assets/data/plan_aktivnosti.json';
const MAX_EVENTS = 6;
const REFRESH_INTERVAL = 3600000; // 1 sat u milisekundama

let allFutureEvents = [];

// Parse various date formats from JSON
function parseEventDate(dateStr) {
  if (!dateStr) return null;

  // Clean the string
  dateStr = dateStr.trim().replace(/\n/g, '');

  // Handle ISO format (2026-02-28)
  if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
    return new Date(dateStr);
  }

  // Handle formats like "03/04.01.2026", "17/18.01.2026.", "01/02/03.05.2026."
  // Extract the last day and the date parts
  const match = dateStr.match(/(\d+(?:\/\d+)*)[.\-](\d{1,2})[.\-](\d{4})/);
  if (match) {
    const dayPart = match[1];
    const month = parseInt(match[2]) - 1; // JS months are 0-indexed
    const year = parseInt(match[3]);

    // Take the last day if multiple days (e.g., "03/04" -> 04)
    const days = dayPart.split('/');
    const day = parseInt(days[days.length - 1]);

    return new Date(year, month, day);
  }

  // Handle formats like "03-06.07.2026."
  const matchRange = dateStr.match(/(\d+)-(\d+)[.\-](\d{1,2})[.\-](\d{4})/);
  if (matchRange) {
    const endDay = parseInt(matchRange[2]);
    const month = parseInt(matchRange[3]) - 1;
    const year = parseInt(matchRange[4]);
    return new Date(year, month, endDay);
  }

  return null;
}

// Format date for display (DD)
function formatDay(date) {
  return date.getDate().toString().padStart(2, '0');
}

// Get month abbreviation
function getMonthAbbr(date) {
  const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAJ', 'JUN', 'JUL', 'AVG', 'SEP', 'OKT', 'NOV', 'DEC'];
  return months[date.getMonth()];
}

// Load events from JSON file
async function loadEvents() {
  const container = document.getElementById('eventsContainer');
  if (!container) return;

  try {
    console.log('📅 Učitavanje događaja iz:', JSON_PATH);
    const response = await fetch(JSON_PATH);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time for accurate comparison

    allFutureEvents = [];

    // Collect all events from all months
    Object.keys(data).forEach(month => {
      if (!Array.isArray(data[month])) return;

      data[month].forEach(event => {
        // Support both field naming conventions
        const dateStr = event.datum || event.date;
        const activity = event.naziv_aktivnosti || event.activity;
        const organizer = event.organizator_vodic || event.organizer_guide;

        const eventDate = parseEventDate(dateStr);

        // Skip events with invalid dates or past events
        if (!eventDate || eventDate < today) return;

        // Skip events with placeholder dates
        if (dateStr && dateStr.match(/^[а-яА-Я]+$/)) return;

        allFutureEvents.push({
          date: dateStr,
          activity: activity,
          organizer_guide: organizer,
          jsDate: eventDate,
          monthName: month
        });
      });
    });

    // Sort by date (chronological order)
    allFutureEvents.sort((a, b) => a.jsDate - b.jsDate);

    console.log(`✅ Pronađeno ${allFutureEvents.length} budućih događaja`);

    // Render first 6 events
    renderEvents();

  } catch (error) {
    console.error('❌ Greška pri učitavanju događaja:', error);
    showEventsError();
  }
}

// Render events to container
function renderEvents() {
  const container = document.getElementById('eventsContainer');
  if (!container) return;

  // Take only first 6 upcoming events
  const eventsToShow = allFutureEvents.slice(0, MAX_EVENTS);

  if (eventsToShow.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12">
        <i class="fas fa-calendar-times text-gray-300 text-6xl mb-4"></i>
        <p class="text-gray-500 text-xl">Trenutno nema planiranih akcija</p>
      </div>
    `;
    updateLoadMoreButton(false);
    return;
  }

  container.innerHTML = eventsToShow.map(event => createEventCard(event)).join('');
  updateLoadMoreButton(allFutureEvents.length > MAX_EVENTS);
}

// Create event card HTML
function createEventCard(event) {
  const day = formatDay(event.jsDate);
  const month = getMonthAbbr(event.jsDate);

  return `
    <div class="group bg-white rounded-2xl p-6 border-2 border-primary-blue/20 hover:border-primary-blue hover:border-opacity-100 transition-all duration-300 hover:shadow-2xl transform hover:-translate-y-2">
      <div class="flex items-start mb-6">
        <div class="bg-primary-blue text-white rounded-xl p-4 text-center min-w-20">
          <div class="text-2xl font-bold">${day}</div>
          <div class="text-sm tracking-wider">${month}</div>
        </div>
        <div class="ml-4">
          <h3 class="text-xl font-bold text-primary-blue group-hover:text-primary-red transition-colors">
            ${event.activity}
          </h3>
          <p class="text-gray-600 text-sm">${event.monthName}</p>
        </div>
      </div>
      <div class="space-y-3 mb-6 text-gray-700">
        <div class="flex items-center">
          <i class="fas fa-calendar-alt text-primary-blue mr-3"></i>
          <span>${event.date}</span>
        </div>
        ${event.organizer_guide ? `
          <div class="flex items-center">
            <i class="fas fa-users text-secondary-gold mr-3"></i>
            <span>${event.organizer_guide}</span>
          </div>
        ` : ''}
      </div>
      <div class="flex justify-center">
        <button type="button"
          class="view-event-btn px-6 py-3 bg-primary-blue text-white rounded-xl font-semibold inline-flex items-center"
          data-event-activity="${encodeURIComponent(event.activity)}">
          Detalji <i class="fas fa-info-circle ml-2" aria-hidden="true"></i>
        </button>
      </div>
    </div>
  `;
}

// Update Load More button
function updateLoadMoreButton(hasMore) {
  const button = document.getElementById('loadMoreEvents');
  if (!button) return;

  if (hasMore) {
    button.style.display = 'inline-flex';
    button.innerHTML = `
      Prikaži sve događaje (${allFutureEvents.length})
      <i class="fas fa-arrow-right ml-3" aria-hidden="true"></i>
    `;
    button.disabled = false;
    button.classList.remove('opacity-50', 'cursor-not-allowed');
  } else {
    button.style.display = 'none';
  }
}

// Show error message
function showEventsError() {
  const container = document.getElementById('eventsContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="col-span-full text-center py-12 bg-red-50 rounded-xl">
      <i class="fas fa-exclamation-triangle text-red-500 text-6xl mb-4"></i>
      <p class="text-red-700 text-xl font-semibold mb-2">Greška pri učitavanju događaja</p>
      <p class="text-red-600">Molimo pokušajte kasnije</p>
    </div>
  `;
}

// Open event modal with details
function openEventModal(activityEncoded) {
  const activity = decodeURIComponent(activityEncoded);
  const event = allFutureEvents.find(e => e.activity === activity);
  if (!event) return;

  const day = formatDay(event.jsDate);
  const month = getMonthAbbr(event.jsDate);
  const year = event.jsDate.getFullYear();

  // Set modal title
  const modalTitle = document.getElementById('modalEventTitle');
  if (modalTitle) {
    modalTitle.textContent = event.activity;
  }

  // Build modal content
  let modalContent = `
    <div class="space-y-6">
      <!-- Event Date -->
      <div class="flex items-center gap-4 pb-4 border-b-2 border-gray-100">
        <div class="bg-gradient-to-br from-primary-blue to-secondary-blue text-white rounded-xl p-4 text-center min-w-24">
          <div class="text-3xl font-bold">${day}</div>
          <div class="text-sm tracking-wider">${month}</div>
          <div class="text-xs opacity-80">${year}</div>
        </div>
        <div>
          <span class="inline-block px-4 py-2 rounded-full bg-primary-blue/10 text-primary-blue font-semibold text-sm">
            ${event.monthName}
          </span>
        </div>
      </div>

      <!-- Event Details -->
      <div class="grid grid-cols-1 gap-4">
        <div class="flex items-center p-4 bg-primary-blue/5 rounded-xl">
          <div class="w-12 h-12 rounded-full bg-primary-blue/20 flex items-center justify-center mr-4">
            <i class="fas fa-calendar-alt text-primary-blue text-xl"></i>
          </div>
          <div>
            <div class="text-xs text-gray-500 uppercase font-semibold">Datum</div>
            <div class="text-gray-800 font-bold">${event.date}</div>
          </div>
        </div>

        ${event.organizer_guide ? `
          <div class="flex items-center p-4 bg-secondary-gold/5 rounded-xl">
            <div class="w-12 h-12 rounded-full bg-secondary-gold/20 flex items-center justify-center mr-4">
              <i class="fas fa-users text-secondary-gold text-xl"></i>
            </div>
            <div>
              <div class="text-xs text-gray-500 uppercase font-semibold">Organizator / Vodič</div>
              <div class="text-gray-800 font-bold">${event.organizer_guide}</div>
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;

  const modalContentEl = document.getElementById('modalEventContent');
  if (modalContentEl) {
    modalContentEl.innerHTML = modalContent;
  }

  // Show modal
  const modal = document.getElementById('eventModal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
  }
}

// Close event modal
function closeEventModal() {
  const modal = document.getElementById('eventModal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.body.style.overflow = '';
  }
}

// Auto-refresh: Check every hour if events have expired
function startAutoRefresh() {
  setInterval(() => {
    console.log('🔄 Auto-refresh: Provjera isteklih događaja...');
    loadEvents();
  }, REFRESH_INTERVAL);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
  console.log('📅 events.js: Inicijalizacija...');

  // Load events on page load
  loadEvents();

  // Start auto-refresh
  startAutoRefresh();

  // Load More button - show all events
  const loadMoreBtn = document.getElementById('loadMoreEvents');
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', function() {
      if (!this.disabled) {
        // Redirect to full calendar page or show all events
        const container = document.getElementById('eventsContainer');
        if (container) {
          container.innerHTML = allFutureEvents.map(event => createEventCard(event)).join('');
          this.style.display = 'none';
        }
      }
    });
  }

  // Event card "Detalji" button - using event delegation
  document.addEventListener('click', function(e) {
    if (e.target.closest('.view-event-btn')) {
      const btn = e.target.closest('.view-event-btn');
      const activityEncoded = btn.getAttribute('data-event-activity');
      if (activityEncoded) {
        openEventModal(activityEncoded);
      }
    }
  });

  // Close modal button
  const closeModalBtn = document.getElementById('closeEventModal');
  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeEventModal);
  }

  // Close modal on background click
  const eventModal = document.getElementById('eventModal');
  if (eventModal) {
    eventModal.addEventListener('click', function(e) {
      if (e.target === this) {
        closeEventModal();
      }
    });
  }

  // Close modal on ESC key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const modal = document.getElementById('eventModal');
      if (modal && !modal.classList.contains('hidden')) {
        closeEventModal();
      }
    }
  });
});

})(); // End of IIFE

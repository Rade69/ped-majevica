// ============================================
// PED MAJEVICA 1988 - REFACTORED JAVASCRIPT
// Version: 2.0.0 - FINAL COMPLETE
// ============================================

const PEDMajevicaApp = (function () {
    'use strict';

    // ============================================
    // CSRF TOKEN MANAGEMENT
    // ============================================
    const CSRF = {
        token: null,

        async init() {
            try {
                const res = await fetch('/api/csrf-token', { credentials: 'include' });
                if (res.ok) {
                    const data = await res.json();
                    this.token = data.csrf_token;
                    // Inject into all forms with CSRF token hidden input
                    document.querySelectorAll('form').forEach(form => {
                        if (!form.querySelector('input[name="csrf_token"]')) {
                            const input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = 'csrf_token';
                            input.value = this.token;
                            form.appendChild(input);
                        }
                    });
                }
            } catch (e) {
                console.warn('CSRF token fetch failed:', e);
            }
        },

        getHeader() {
            return { 'X-CSRFToken': this.token };
        }
    };

    // Export to window for use in other JS files
    window.CSRF = CSRF;

    const CONFIG = {
        lazyLoading: { rootMargin: '100px 0px', threshold: 0.1, maxLoadingTime: 10000 },
        debounce: { scroll: 100, resize: 200 },
        animation: { trailCardDelay: 100, fadeInDuration: 600 },
        notification: { duration: 5000, maxVisible: 3 }
    };

    const STORAGE_KEYS = { theme: 'pedmajevica-theme' };

    const AppState = {
        isMobile: window.innerWidth < 768,
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        theme: localStorage.getItem(STORAGE_KEYS.theme) || 'light',
        isDev: window.location.hostname === 'localhost',
        performance: { images: { total: 0, loaded: 0, errors: 0 } },
        instances: {},
        cleanupFns: []
    };

    const Utils = {
        escapeHtml(text) {
            if (typeof text !== 'string') return text;
            return text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m]));
        },
        debounce(func, wait) {
            let timeout;
            return function (...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },
        throttle(func, limit) {
            let inThrottle;
            return function (...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        isValidEmail: (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
        log: (...args) => { if (AppState.isDev) console.log(...args); },
        generateId: () => `ped_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };

    class LazyLoader {
        constructor() {
            this.images = new Map();
            this.observer = null;
            this.loaded = 0;
            this.errors = 0;
        }

        init() {
            Utils.log('🖼️ LazyLoader init');
            if (AppState.prefersReducedMotion) {
                this.loadAll();
            } else if ('IntersectionObserver' in window) {
                this.observer = new IntersectionObserver((entries) => {
                    entries.forEach(e => {
                        if (e.isIntersecting) {
                            this.load(e.target);
                            this.observer.unobserve(e.target);
                        }
                    });
                }, { rootMargin: CONFIG.lazyLoading.rootMargin, threshold: CONFIG.lazyLoading.threshold });

                document.querySelectorAll('img[data-src]').forEach(img => {
                    this.images.set(img, { src: img.dataset.src, loaded: false });
                    this.observer.observe(img);
                });
                AppState.performance.images.total = this.images.size;
            } else {
                this.loadAll();
            }
            this.loadCritical();
            AppState.cleanupFns.push(() => { if (this.observer) this.observer.disconnect(); this.images.clear(); });
        }

        load(img) {
            const data = this.images.get(img);
            if (!data || data.loaded) return;

            img.classList.add('loading');
            const temp = new Image();
            const timeoutId = setTimeout(() => {
                if (!data.loaded) this.error(img, data);
            }, CONFIG.lazyLoading.maxLoadingTime);

            temp.onload = () => {
                clearTimeout(timeoutId);
                img.src = data.src;
                img.classList.remove('loading');
                img.classList.add('loaded');
                data.loaded = true;
                this.loaded++;
                AppState.performance.images.loaded = this.loaded;
                this.images.delete(img);
            };

            temp.onerror = () => {
                clearTimeout(timeoutId);
                this.error(img, data);
            };

            temp.src = data.src;
        }

        error(img, data) {
            data.error = true;
            this.errors++;
            AppState.performance.images.errors = this.errors;
            img.classList.remove('loading');
            img.classList.add('error');
            this.images.delete(img);
        }

        loadAll() {
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
                img.onload = () => { img.classList.add('loaded'); this.loaded++; };
                delete img.dataset.src;
            });
        }

        loadCritical() {
            document.querySelectorAll('.trail-card:nth-child(-n+3) img[data-src]').forEach((img, i) => {
                setTimeout(() => {
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.add('loaded', 'critical-image');
                        delete img.dataset.src;
                    }
                }, i * 100);
            });
        }
    }

    class MobileMenu {
        constructor() {
            this.toggle = document.getElementById('mobileMenuToggle');
            this.menu = document.getElementById('mobileMenu');
            this.icon = this.toggle?.querySelector('i');
            this.isOpen = false;
        }

        init() {
            if (!this.toggle) return;
            this.toggle.addEventListener('click', () => this.isOpen ? this.close() : this.open());
            this.menu?.querySelectorAll('a').forEach(l => l.addEventListener('click', () => this.close()));
            document.addEventListener('keydown', e => { if (e.key === 'Escape' && this.isOpen) this.close(); });
        }

        open() {
            this.menu.classList.remove('hidden');
            this.icon?.classList.replace('fa-bars', 'fa-times');
            this.isOpen = true;
            document.body.style.overflow = 'hidden';
        }

        close() {
            this.menu.classList.add('hidden');
            this.icon?.classList.replace('fa-times', 'fa-bars');
            this.isOpen = false;
            document.body.style.overflow = '';
        }
    }

    class NotificationSystem {
        constructor() { this.notifications = []; this.container = null; }

        init() {
            this.container = document.createElement('div');
            this.container.className = 'fixed top-4 right-4 z-[1000] space-y-2';
            document.body.appendChild(this.container);
        }

        show(msg, type = 'info') {
            if (this.notifications.length >= CONFIG.notification.maxVisible) {
                this.notifications.shift()?.remove();
            }

            const id = Utils.generateId();
            const notif = document.createElement('div');
            notif.id = id;
            notif.className = 'bg-white rounded-xl shadow-2xl p-4 max-w-sm transform translate-x-full transition-transform duration-300';

            const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
            const colors = { success: 'text-success', error: 'text-error', warning: 'text-warning', info: 'text-info' };

            notif.innerHTML = `
                <div class="flex items-start">
                    <i class="fas ${icons[type]} text-xl mr-3 ${colors[type]}"></i>
                    <div class="flex-1"><p class="text-gray-800 font-medium">${Utils.escapeHtml(msg)}</p></div>
                    <button class="ml-3 text-gray-400 hover:text-gray-600 close-notif"><i class="fas fa-times"></i></button>
                </div>
            `;

            this.container.appendChild(notif);
            this.notifications.push(notif);
            requestAnimationFrame(() => notif.classList.remove('translate-x-full'));

            notif.querySelector('.close-notif').addEventListener('click', () => this.remove(id));
            const tid = setTimeout(() => this.remove(id), CONFIG.notification.duration);
            notif.dataset.tid = tid;
        }

        remove(id) {
            const n = document.getElementById(id);
            if (!n) return;
            clearTimeout(parseInt(n.dataset.tid));
            n.classList.add('translate-x-full');
            setTimeout(() => {
                n.remove();
                this.notifications = this.notifications.filter(x => x.id !== id);
            }, 300);
        }
    }

    class SmoothScroller {
        init() {
            document.querySelectorAll('a[href^="#"]').forEach(link => {
                link.addEventListener('click', e => {
                    const target = document.querySelector(link.getAttribute('href'));
                    if (target) {
                        e.preventDefault();
                        window.scrollTo({ top: target.offsetTop - 80, behavior: 'smooth' });
                    }
                });
            });

            const btn = document.getElementById('scrollToTop');
            if (btn) {
                window.addEventListener('scroll', Utils.throttle(() => {
                    const show = window.scrollY > 500;
                    btn.classList.toggle('visible', show);
                    btn.classList.toggle('opacity-0', !show);
                    btn.classList.toggle('pointer-events-none', !show);
                }, 100), { passive: true });

                btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
            }
        }
    }

    class ThemeSystem {
        init() {
            const toggle = document.getElementById('themeToggle');
            if (!toggle) return;

            const icon = toggle.querySelector('i');
            const saved = localStorage.getItem(STORAGE_KEYS.theme);

            // Uvek osiguraj da ikona ima zlatnu boju
            if (icon) {
                icon.classList.add('text-secondary-gold');
            }

            // Ako je dark mode sačuvan, primeni ga odmah
            if (saved === 'dark') {
                this.applyDarkMode();
                if (icon) {
                    icon.classList.remove('fa-sun');
                    icon.classList.add('fa-moon');
                }
            } else {
                this.applyLightMode();
                if (icon) {
                    icon.classList.remove('fa-moon');
                    icon.classList.add('fa-sun');
                }
            }

            toggle.addEventListener('click', () => {
                const isCurrentlyDark = document.documentElement.classList.contains('dark');

                if (isCurrentlyDark) {
                    this.applyLightMode();
                    if (icon) {
                        icon.classList.remove('fa-moon');
                        icon.classList.add('fa-sun');
                    }
                    if (window.NotificationSystem) {
                        window.NotificationSystem.show('Svijetli mod aktiviran', 'info');
                    }
                } else {
                    this.applyDarkMode();
                    if (icon) {
                        icon.classList.remove('fa-sun');
                        icon.classList.add('fa-moon');
                    }
                    if (window.NotificationSystem) {
                        window.NotificationSystem.show('Tamni mod aktiviran', 'info');
                    }
                }
            });

            // Dodaj transition klasu za smooth efekte
            document.documentElement.classList.add('dark-transition');
        }

        applyDarkMode() {
            document.documentElement.classList.add('dark');
            localStorage.setItem(STORAGE_KEYS.theme, 'dark');
        }

        applyLightMode() {
            document.documentElement.classList.remove('dark');
            localStorage.setItem(STORAGE_KEYS.theme, 'light');
        }
    }

    class TrailFilter {
        init() {
            const btns = document.querySelectorAll('.filter-btn');
            const cards = document.querySelectorAll('.trail-card');
            if (btns.length === 0) return;

            btns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const filter = btn.getAttribute('data-filter');
                    btns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    cards.forEach((c, i) => {
                        const diff = c.getAttribute('data-difficulty');
                        const show = filter === 'all' || filter === diff;

                        if (show) {
                            setTimeout(() => {
                                c.style.display = 'block';
                                requestAnimationFrame(() => {
                                    c.style.opacity = '1';
                                    c.style.transform = 'translateY(0)';
                                });
                            }, i * 50);
                        } else {
                            c.style.opacity = '0';
                            c.style.transform = 'translateY(20px)';
                            setTimeout(() => c.style.display = 'none', 300);
                        }
                    });
                });
            });

            cards.forEach((c, i) => {
                c.style.opacity = '0';
                c.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    c.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    c.style.opacity = '1';
                    c.style.transform = 'translateY(0)';
                }, 200 + i * 100);
            });
        }
    }

    class TrailModal {
        constructor() {
            this.modal = document.getElementById('trailModal');
            this.isOpen = false;
            this.data = {
                1: { name: "Velika staza - Orlovič", difficulty: "Srednja", length: "18 km", time: "5-6 sati", description: "Historijska staza do najvišeg vrha.", features: ["Panoramski vidik", "Potok i izvor vode", "Označena staza"], equipment: ["Planinarske cipele", "Ruksak", "GPS", "Kišna odjeća"], gpxFile: "velika-staza.gpx" },
                2: { name: "Mala staza - Porodična", difficulty: "Laka", length: "10.8 km", time: "4-5 sati", description: "Idealna za porodice.", features: ["Ravna staza", "Piknik mjesto", "Dječije igralište"], equipment: ["Udobna obuća", "Voda", "Sunčana krema"], gpxFile: "mala-staza.gpx" },
                3: { name: "Novakova pećina", difficulty: "Laka", length: "1.2 km", time: "40 min", description: "Kratka rekreativna staza.", features: ["Kratka šetnja", "Zanimljiva pećina", "Edukativni paneli"], equipment: ["Udobna obuća", "Voda", "Svjetiljka"], gpxFile: "novakova-pecina.gpx" }
            };
        }

        init() {
            if (!this.modal) return;

            document.querySelectorAll('.view-trail-btn').forEach(btn => {
                btn.addEventListener('click', e => {
                    e.stopPropagation();
                    this.open(btn.getAttribute('data-trail'));
                });
            });

            document.getElementById('closeModal')?.addEventListener('click', () => this.close());
            this.modal.addEventListener('click', e => { if (e.target === this.modal) this.close(); });
            document.addEventListener('keydown', e => { if (e.key === 'Escape' && this.isOpen) this.close(); });
        }

        open(id) {
            const t = this.data[id];
            if (!t) return;

            document.getElementById('modalTrailName').textContent = t.name;
            document.getElementById('modalContent').innerHTML = `
                <div class="grid md:grid-cols-2 gap-8">
                    <div>
                        <h4 class="text-lg font-bold text-primary-blue mb-3">Opis</h4>
                        <p class="text-gray-700 mb-6">${Utils.escapeHtml(t.description)}</p>
                        <h4 class="text-lg font-bold text-primary-blue mb-3">Karakteristike</h4>
                        <ul class="space-y-2 mb-6">${t.features.map(f => `<li class="flex items-center"><i class="fas fa-check text-primary-red mr-3"></i>${Utils.escapeHtml(f)}</li>`).join('')}</ul>
                        <h4 class="text-lg font-bold text-primary-blue mb-3">Oprema</h4>
                        <ul class="space-y-2">${t.equipment.map(e => `<li class="flex items-center"><i class="fas fa-hiking text-secondary-gold mr-3"></i>${Utils.escapeHtml(e)}</li>`).join('')}</ul>
                    </div>
                    <div>
                        <div class="bg-gradient-to-br from-primary-blue/5 to-primary-red/5 rounded-2xl p-6 mb-6">
                            <h4 class="text-lg font-bold text-primary-blue mb-4">Detalji</h4>
                            <div class="space-y-3">
                                <div class="flex justify-between"><span>Težina:</span><b>${Utils.escapeHtml(t.difficulty)}</b></div>
                                <div class="flex justify-between"><span>Dužina:</span><b>${Utils.escapeHtml(t.length)}</b></div>
                                <div class="flex justify-between"><span>Vrijeme:</span><b>${Utils.escapeHtml(t.time)}</b></div>
                            </div>
                        </div>
                        <button class="w-full py-3 bg-primary-blue text-white font-bold rounded-lg mb-4 dl-btn"><i class="fas fa-download mr-2"></i>Preuzmi GPX</button>
                        <button class="w-full py-3 bg-primary-red text-white font-bold rounded-lg share-btn"><i class="fas fa-share-alt mr-2"></i>Podijeli</button>
                    </div>
                </div>
            `;

            this.modal.classList.remove('hidden');
            this.modal.classList.add('flex', 'active');
            document.body.style.overflow = 'hidden';
            this.isOpen = true;

            document.querySelector('.dl-btn')?.addEventListener('click', () => {
                window.NotificationSystem.show(`Preuzimanje ${t.gpxFile}...`, 'info');
            });

            document.querySelector('.share-btn')?.addEventListener('click', () => {
                if (navigator.share) {
                    navigator.share({ title: t.name, url: window.location.href }).then(() =>
                        window.NotificationSystem.show('Podijeljeno!', 'success')
                    ).catch(() => { });
                } else {
                    window.NotificationSystem.show('Link kopiran!', 'info');
                }
            });
        }

        close() {
            if (!this.isOpen) return;
            this.modal.classList.remove('active', 'flex');
            this.modal.classList.add('hidden');
            document.body.style.overflow = '';
            this.isOpen = false;
        }
    }

    class FormHandler {
        init() {
            const form = document.getElementById('contactForm');
            if (form) {
                form.addEventListener('submit', async e => {
                    e.preventDefault();
                    const name = document.getElementById('name')?.value.trim();
                    const email = document.getElementById('email')?.value.trim();
                    const msg = document.getElementById('message')?.value.trim();

                    if (!name || !Utils.isValidEmail(email) || !msg) {
                        window.NotificationSystem.show('Popunite sva polja!', 'error');
                        return;
                    }

                    const btn = form.querySelector('button[type="submit"]');
                    const orig = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Šaljem...';
                    btn.disabled = true;

                    await new Promise(r => setTimeout(r, 2000));

                    window.NotificationSystem.show('Poruka poslana!', 'success');
                    form.reset();
                    btn.innerHTML = orig;
                    btn.disabled = false;
                });
            }

            const subBtn = document.getElementById('subscribeBtn');
            if (subBtn) {
                subBtn.addEventListener('click', async () => {
                    const input = subBtn.previousElementSibling;
                    const email = input?.value.trim();

                    if (!Utils.isValidEmail(email)) {
                        window.NotificationSystem.show('Unesite validan email!', 'error');
                        return;
                    }

                    const orig = subBtn.innerHTML;
                    subBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    subBtn.disabled = true;

                    await new Promise(r => setTimeout(r, 1500));

                    window.NotificationSystem.show('Prijavljeni ste!', 'success');
                    input.value = '';
                    subBtn.innerHTML = orig;
                    subBtn.disabled = false;
                });
            }
        }
    }

    function init() {
        Utils.log('🚀 Initializing...');

        // Initialize CSRF token first
        CSRF.init();

        const ns = new NotificationSystem();
        ns.init();
        window.NotificationSystem = ns;

        const systems = {
            lazyLoader: new LazyLoader(),
            mobileMenu: new MobileMenu(),
            smoothScroller: new SmoothScroller(),
            trailFilter: new TrailFilter(),
            trailModal: new TrailModal(),
            formHandler: new FormHandler(),
            themeSystem: new ThemeSystem()
        };

        Object.entries(systems).forEach(([name, sys]) => {
            try {
                sys.init();
                AppState.instances[name] = sys;
                Utils.log(`✅ ${name}`);
            } catch (e) {
                console.error(`❌ ${name}:`, e);
            }
        });

        ['#joinBtn', '#mobileJoinBtn'].forEach(s => {
            document.querySelector(s)?.addEventListener('click', () => {
                window.NotificationSystem.show('Uskoro dostupno!', 'info');
            });
        });

        document.querySelectorAll('[title*="omiljene"]').forEach(btn => {
            btn.addEventListener('click', function () {
                const icon = this.querySelector('i');
                if (icon.classList.contains('far')) {
                    icon.classList.replace('far', 'fas');
                    icon.classList.add('text-primary-red');
                    window.NotificationSystem.show('Dodano!', 'success');
                } else {
                    icon.classList.replace('fas', 'far');
                    icon.classList.remove('text-primary-red');
                    window.NotificationSystem.show('Uklonjeno!', 'info');
                }
            });
        });

        Utils.log('✅ Done');
    }

    return {
        init,
        state: AppState,
        notify: (m, t) => window.NotificationSystem?.show(m, t),
        debug: { log: () => console.log('State:', AppState) }
    };

})();

document.addEventListener('DOMContentLoaded', () => PEDMajevicaApp.init());

window.addEventListener('load', () => {
    const p = document.getElementById('preloader');
    if (p) {
        p.style.opacity = '0';
        setTimeout(() => p.style.display = 'none', 500);
    }
});

if (window.location.hostname === 'localhost') {
    window.PED = PEDMajevicaApp;
    console.log('🔧 Debug: window.PED.debug.log()');
}
// ============================================
// DARK MODE FIX - Inline styles
// ============================================
(function () {
    // PROVJERI da li stil već postoji
    if (document.getElementById('dark-mode-styles')) {
        console.log('⚠️ Dark mode styles already loaded');
        return;
    }

    const darkModeStyles = document.createElement('style');
    darkModeStyles.id = 'dark-mode-styles';
    darkModeStyles.textContent = `
        html.dark, html.dark body { 
            background: #111827 !important; 
            color: #f3f4f6 !important; 
        }
        html.dark section { 
            background: #1f2937 !important; 
        }
        html.dark .bg-white { 
            background: #1f2937 !important; 
        }
        html.dark h1, html.dark h2, html.dark h3 { 
            color: #f3f4f6 !important; 
        }
        html.dark p { 
            color: #d1d5db !important; 
        }
        html.dark header { 
            background: linear-gradient(to right, #1f2937, #111827) !important; 
        }
        html.dark footer { 
            background: #111827 !important; 
        }
        html.dark .trail-card {
            background: #1f2937 !important;
        }
        html.dark .text-gray-700 {
            color: #d1d5db !important;
        }
        html.dark .text-gray-600 {
            color: #e5e7eb !important;
        }
        html.dark .text-gray-800 {
            color: #f3f4f6 !important;
        }
        
        /* Secondary blue - različite boje za različite pozadine */
        .text-secondary-blue {
            color: #003366 !important;
        }
        html.dark .text-secondary-blue {
            color: #60a5fa !important;
        }
        
        /* Plava gradijent pozadina - zlatni tekst */
        .bg-gradient-to-r.from-primary-blue .text-secondary-blue {
            color: #fbbf24 !important;
        }
        
        /* Outline buttons u dark modu */
        html.dark .bg-secondary-gold {
            background: transparent !important;
            border: 2px solid #fbbf24 !important;
            color: #fbbf24 !important;
        }
        html.dark .bg-secondary-gold:hover {
            background: #fbbf24 !important;
            color: #111827 !important;
        }
        
        /* Link buttons sa border-om - zlatni u dark modu */
        html.dark .border-primary-blue {
            border-color: #fbbf24 !important;
        }
        html.dark a.text-primary-blue {
            color: #fbbf24 !important;
        }
            /* Link buttons sa border-om - zlatni u dark modu */
        html.dark .border-primary-blue {
            border-color: #fbbf24 !important;
        }
        html.dark a.text-primary-blue {
            color: #fbbf24 !important;
        }
        html.dark a.hover\:bg-primary-blue:hover {
            background: #fbbf24 !important;
            color: #111827 !important;
        }
        
        /* DIV i ostali elementi sa text-primary-blue - svjetlija plava */
        html.dark .text-primary-blue:not(a) {
            color: #60a5fa !important;
        }
        html.dark a.hover\:bg-primary-blue:hover {
            background: #fbbf24 !important;
            color: #111827 !important;
        }
        
        /* Scroll to top button - custom gradijent */
        #scrollToTop {
            background: linear-gradient(135deg, #D62828 0%, #003366 50%, #FFD700 100%) !important;
        }
        #scrollToTop:hover {
            background: linear-gradient(135deg, #FF6B6B 0%, #1E4A8B 50%, #FFA500 100%) !important;
            transform: scale(1.15) !important;
        }
            /* Filter button "Sve staze" - zlatni u dark modu */
        html.dark .filter-btn.border-primary-blue {
            background: transparent !important;
            border-color: #fbbf24 !important;
            color: #fbbf24 !important;
        }
        html.dark .filter-btn.border-primary-blue:hover {
            background: #fbbf24 !important;
            color: #111827 !important;
        }
            /* Zlatni gradient button - tamniji tekst u dark modu */
        html.dark .bg-gradient-to-r.from-secondary-gold {
            background: linear-gradient(to right, #d97706, #f59e0b) !important;
        }
        html.dark .bg-gradient-to-r.from-secondary-gold .text-primary-blue,
        html.dark .bg-gradient-to-r.from-secondary-gold {
            color: #1e293b !important;
        }
        
        
        
        /* Firefox scrollbar */
        * {
            scrollbar-width: thin;
            scrollbar-color: #D62828 #1f2937;
        }
    `;
    document.head.appendChild(darkModeStyles);
    console.log('✅ Dark mode styles loaded');
})();
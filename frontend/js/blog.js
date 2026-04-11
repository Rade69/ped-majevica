// ============================================================================
// BLOG SYSTEM - PED Majevica 1988
// Sa integrisanom transliteracijom Ćirilica ⇄ Latinica i API paginacijom
// ============================================================================

// Globalne promenljive
let currentPosts = [];          // Postovi za trenutnu stranicu
let currentPagination = {};     // Paginacioni podaci od API-ja
let currentPage = 1;
const articlesPerPage = 6;      // Mora da se podudara sa backend per_page
let currentScript = 'cyrillic'; // default
let currentSearch = '';         // Trenutni search termin
let currentCategory = 'sve';    // Trenutna kategorija ('sve' za sve)

// Fetch postova sa API-ja sa paginacijom
async function fetchPosts(page = 1, search = '', category = 'sve') {
    try {
        // Use API_CONFIG for correct backend URL
        let apiUrl;
        if (window.API_CONFIG && typeof window.API_CONFIG.getUrl === 'function') {
            apiUrl = window.API_CONFIG.getUrl(window.API_CONFIG.ENDPOINTS.POSTS);
        } else {
            // Development fallback
            const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            if (isLocalhost) {
                apiUrl = 'http://localhost:5000/api/posts';
            } else {
                apiUrl = '/api/posts';
            }
        }
        
        // Dodaj query parametre
        const url = new URL(apiUrl);
        url.searchParams.set('page', page);
        url.searchParams.set('per_page', articlesPerPage);
        
        if (search && search.trim() !== '') {
            url.searchParams.set('search', search.trim());
        }
        
        if (category && category !== 'sve') {
            url.searchParams.set('category', category);
        }
        
        console.log('📚 Blog: Fetching from:', url.toString());
        
        // Use credentials for cross-origin requests
        const response = await fetch(url.toString(), {
          credentials: window.API_CONFIG ? window.API_CONFIG.getCredentials() : 'include'
        });
        
        console.log('📚 Blog: Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📚 Blog: Data received:', data);
        
        // Handle both old format (data.posts) and new format (data.data.posts)
        const posts = data.data?.posts || data.posts || [];
        const pagination = data.data?.pagination || data.pagination || {};
        
        console.log('📚 Blog: Fetched', posts.length, 'posts for page', page);
        console.log('📚 Blog: Pagination info:', pagination);
        
        return { posts, pagination };
        
    } catch (error) {
        console.error('📚 Blog: Greška pri fetch-ovanju postova:', error);
        throw error;
    }
}

// Inicijalizacija
async function initBlog() {
    console.log('📚 Blog: Inicijalizacija...');
    try {
        // Resetuj trenutne vrednosti
        currentSearch = '';
        currentCategory = 'sve';
        currentPage = 1;
        
        // Učitaj prvu stranicu
        await loadPage(1);
        
        console.log('📚 Blog: Inicijalizacija završena!');
    } catch (error) {
        console.error('Greška pri učitavanju članaka:', error);
        console.error('Stack trace:', error.stack);
        showError();
    }
}

// Učitaj stranicu sa trenutnim filterima
async function loadPage(page) {
    try {
        console.log(`📚 Blog: Učitavam stranicu ${page} sa search='${currentSearch}', category='${currentCategory}'`);
        
        const result = await fetchPosts(page, currentSearch, currentCategory);
        currentPosts = result.posts;
        currentPagination = result.pagination;
        currentPage = page;
        
        // Sortiranje po datumu - NAJNOVIJI PRVO (API već sortira, ali za svaki slučaj)
        try {
            currentPosts.sort((a, b) => {
                const dateA = new Date(a.created_at || a.date || 0);
                const dateB = new Date(b.created_at || b.date || 0);
                if (isNaN(dateA.getTime())) return 1;
                if (isNaN(dateB.getTime())) return -1;
                return dateB - dateA; // Noviji prvo (DESC)
            });
        } catch (sortError) {
            console.error('📚 Blog: Greška pri sortiranju:', sortError);
        }
        
        renderArticles();
        renderPagination();
        
    } catch (error) {
        console.error('📚 Blog: Greška pri učitavanju stranice:', error);
        throw error;
    }
}


}

// Praćenje promene pisma
function setupScriptChangeListener() {
    // Slušaj custom event koji će transliterator emitovati
    document.addEventListener('scriptChanged', function(e) {
        currentScript = e.detail.script;
        renderArticles(); // Re-render sa novim pismom
    });
    
    // Fallback - proveri svakih 500ms da li se promenilo pismo
    setInterval(() => {
        if (typeof transliterator !== 'undefined') {
            const newScript = transliterator.getCurrentScript();
            if (newScript !== currentScript) {
                currentScript = newScript;
                renderArticles();
            }
        }
    }, 500);
}

// Event listeners
function setupEventListeners() {
    // Search
    const searchInput = document.getElementById('blogSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Filter
    const filterSelect = document.getElementById('blogFilter');
    if (filterSelect) {
        filterSelect.addEventListener('change', handleFilter);
    }
    
    // Modal close - oba dugmeta
    const modal = document.getElementById('articleModal');
    const closeBtn = document.getElementById('closeModal');
    const closeBtnBottom = document.getElementById('closeModalBtn');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
    
    if (closeBtnBottom) {
        closeBtnBottom.addEventListener('click', closeModal);
    }
    
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // ESC key za zatvaranje modala
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Search funkcija
async function handleSearch(e) {
    const query = e.target.value.trim();
    
    console.log(`📚 Blog: Search query: "${query}"`);
    
    // Ažuriraj trenutni search i resetuj na prvu stranicu
    currentSearch = query;
    currentPage = 1;
    
    try {
        await loadPage(1);
    } catch (error) {
        console.error('📚 Blog: Greška pri pretrazi:', error);
        showError();
    }
}

// Filter funkcija
async function handleFilter(e) {
    const category = e.target.value;
    
    console.log(`📚 Blog: Filter category: "${category}"`);
    
    // Ažuriraj trenutnu kategoriju i resetuj na prvu stranicu
    currentCategory = category;
    currentPage = 1;
    
    // Resetuj search kada se menja kategorija (opciono)
    // currentSearch = '';
    
    try {
        await loadPage(1);
    } catch (error) {
        console.error('📚 Blog: Greška pri filtriranju:', error);
        showError();
    }
}

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Transliteracija teksta
function transliterateText(text, targetScript) {
    if (typeof transliterator !== 'undefined') {
        return transliterator.transliterate(text, targetScript);
    }
    return text; // Fallback ako nema transliteratora
}

// Transliteracija HTML-a - SAMO TEKST, NE TAGOVI!
function transliterateHTML(html, targetScript) {
    if (!html || typeof transliterator === 'undefined') {
        return html;
    }
    
    // Kreiraj privremeni element
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    
    // Transliteruj sve text node-ove
    const walker = document.createTreeWalker(
        tempDiv,
        NodeFilter.SHOW_TEXT,
        null
    );
    
    let node;
    while (node = walker.nextNode()) {
        if (node.nodeValue && node.nodeValue.trim()) {
            node.nodeValue = transliterator.transliterate(node.nodeValue, targetScript);
        }
    }
    
    return tempDiv.innerHTML;
}

// Render članaka
function renderArticles() {
    console.log('📚 Blog: renderArticles() called');
    const container = document.getElementById('blogArticlesContainer');
    console.log('📚 Blog: Container found:', !!container);
    if (!container) return;

    console.log('📚 Blog: Current posts:', currentPosts.length);

    if (currentPosts.length === 0) {
        const noResultsText = currentScript === 'latin' 
            ? 'Nema pronađenih članaka.' 
            : 'Нема пронађених чланака.';
        
        container.innerHTML = `
            <div class="col-span-3 text-center py-12">
                <i class="fas fa-search text-6xl text-gray-300 mb-4"></i>
                <p class="text-xl text-gray-500">${noResultsText}</p>
            </div>
        `;
        renderPagination();
        return;
    }
    
    container.innerHTML = currentPosts.map(article => {
        const categoryInfo = getCategoryInfo(article.category);
        const dateStr = formatDate(article.date);
        const excerpt = article.preview || article.content_text.substring(0, 150) + '...';
        const hasImages = article.images && article.images.length > 0;
        
        // Transliteruj tekst prema trenutnom pismu
        const title = transliterateText(article.title, currentScript);
        const excerptTranslit = transliterateText(excerpt, currentScript);
        const categoryLabel = transliterateText(categoryInfo.label, currentScript);
        const readMoreText = currentScript === 'latin' ? 'Pročitaj više' : 'Прочитај више';
        
        return `
            <article class="group bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 border border-gray-100 flex flex-col">
                <div class="relative h-48 overflow-hidden bg-gradient-to-br ${categoryInfo.gradient}">
                    <div class="absolute top-4 left-4 z-10">
                        <span class="bg-white/90 backdrop-blur-sm text-primary-blue px-3 py-1 rounded-full text-sm font-bold shadow-lg">
                            <i class="${categoryInfo.icon} mr-1"></i> ${categoryLabel}
                        </span>
                    </div>
                    ${hasImages ? `
                        <img src="${article.images[0]}" alt="${article.title}"
                            class="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                            onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'absolute inset-0 flex items-center justify-center\\'><i class=\\'${categoryInfo.icon} text-white/20 text-8xl\\'></i></div>';">
                    ` : `
                        <div class="absolute inset-0 flex items-center justify-center">
                            <i class="${categoryInfo.icon} text-white/20 text-8xl"></i>
                        </div>
                    `}
                </div>
                <div class="p-6 flex-1 flex flex-col">
                    <div class="flex items-center text-gray-500 text-sm mb-4">
                        <span class="${categoryInfo.bgClass} text-white px-3 py-1 rounded-full font-medium shadow-sm">${categoryLabel}</span>
                        <span class="mx-2">•</span>
                        <span>${dateStr}</span>
                    </div>
                    <h3 class="text-xl font-bold text-primary-blue group-hover:text-primary-red transition-colors mb-4 line-clamp-2">
                        ${title}
                    </h3>
                    <p class="text-gray-600 mb-6 leading-relaxed line-clamp-3 flex-1">
                        ${excerptTranslit}
                    </p>
                    <button onclick="openArticle(${article.id})"
                        class="inline-flex items-center text-primary-red font-bold hover:text-red-dark transition-colors group self-start">
                        ${readMoreText}
                        <i class="fas fa-arrow-right ml-3 group-hover:translate-x-2 transition-transform"></i>
                    </button>
                </div>
            </article>
        `;
    }).join('');
    
    renderPagination();
}

// Paginacija
function renderPagination() {
    const paginationContainer = document.getElementById('blogPagination');
    if (!paginationContainer) return;
    
    // Koristi paginacione podatke od API-ja
    const totalPages = currentPagination.pages || 0;
    const hasPrev = currentPagination.has_prev || false;
    const hasNext = currentPagination.has_next || false;
    const currentPageNum = currentPagination.page || currentPage;
    
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let html = '<div class="flex items-center justify-center space-x-2">';
    
    // Previous
    if (hasPrev) {
        const prevPage = currentPagination.prev_page || (currentPageNum - 1);
        html += `
            <button onclick="changePage(${prevPage})"
                class="px-4 py-2 rounded-lg border-2 border-primary-blue text-primary-blue hover:bg-primary-blue hover:text-white transition-all duration-300">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPageNum) {
            html += `
                <button class="px-4 py-2 rounded-lg bg-primary-red text-white font-bold">
                    ${i}
                </button>
            `;
        } else if (i === 1 || i === totalPages || Math.abs(i - currentPageNum) <= 1) {
            html += `
                <button onclick="changePage(${i})"
                    class="px-4 py-2 rounded-lg border-2 border-gray-300 text-gray-700 hover:border-primary-blue hover:text-primary-blue transition-all duration-300">
                    ${i}
                </button>
            `;
        } else if (Math.abs(i - currentPageNum) === 2) {
            html += `<span class="px-2 text-gray-400">...</span>`;
        }
    }
    
    // Next
    if (hasNext) {
        const nextPage = currentPagination.next_page || (currentPageNum + 1);
        html += `
            <button onclick="changePage(${nextPage})"
                class="px-4 py-2 rounded-lg border-2 border-primary-blue text-primary-blue hover:bg-primary-blue hover:text-white transition-all duration-300">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;
    }
    
    html += '</div>';
    paginationContainer.innerHTML = html;
}

// Promena stranice
async function changePage(page) {
    console.log(`📚 Blog: Menjam stranicu na ${page}`);
    
    // Scroll to top of blog section pre nego što se učitaju novi podaci
    const blogSection = document.getElementById('blog');
    if (blogSection) {
        blogSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    try {
        await loadPage(page);
    } catch (error) {
        console.error('📚 Blog: Greška pri promeni stranice:', error);
        showError();
    }
}

// Fetch pojedinačnog članka
async function fetchArticle(articleId) {
    try {
        // Use API_CONFIG for correct backend URL
        let apiUrl;
        if (window.API_CONFIG && typeof window.API_CONFIG.getUrl === 'function') {
            apiUrl = window.API_CONFIG.getUrl(window.API_CONFIG.ENDPOINTS.POSTS + '/' + articleId);
        } else {
            // Development fallback
            const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            if (isLocalhost) {
                apiUrl = 'http://localhost:5000/api/posts/' + articleId;
            } else {
                apiUrl = '/api/posts/' + articleId;
            }
        }
        
        console.log('📚 Blog: Fetching article:', apiUrl);
        
        const response = await fetch(apiUrl, {
          credentials: window.API_CONFIG ? window.API_CONFIG.getCredentials() : 'include'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        const article = data.data || data;
        console.log('📚 Blog: Article fetched:', article.id);
        return article;
        
    } catch (error) {
        console.error('📚 Blog: Greška pri fetch-ovanju članka:', error);
        throw error;
    }
}

// Otvori članak
async function openArticle(articleId) {
    try {
        console.log(`📚 Blog: Otvaram članak ${articleId}`);
        
        // Prikaži loading stanje u modalu
        const modal = document.getElementById('articleModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        if (modal && modalTitle && modalContent) {
            modalTitle.textContent = 'Učitavanje...';
            modalContent.innerHTML = '<div class="text-center py-8"><i class="fas fa-spinner fa-spin text-4xl text-primary-blue"></i><p class="mt-4 text-gray-600">Učitavam članak...</p></div>';
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.style.overflow = 'hidden';
        }
        
        // Fetch article from API
        const article = await fetchArticle(articleId);
        
        // Prikaži članak u modalu
        showModal(article);
        
    } catch (error) {
        console.error('📚 Blog: Greška pri otvaranju članka:', error);
        
        // Prikaži error poruku
        const modal = document.getElementById('articleModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        
        if (modal && modalTitle && modalContent) {
            modalTitle.textContent = 'Greška';
            modalContent.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-500"></i>
                    <p class="mt-4 text-gray-700">Došlo je do greške pri učitavanju članka.</p>
                    <p class="text-gray-500 text-sm mt-2">Molimo pokušajte ponovo.</p>
                </div>
            `;
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.style.overflow = 'hidden';
        }
    }
}

// Prikaži modal
function showModal(article) {
    const modal = document.getElementById('articleModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalCategory = document.getElementById('modalCategory');
    const modalDate = document.getElementById('modalDate');
    const modalContent = document.getElementById('modalContent');
    
    if (!modal) return;
    
    const categoryInfo = getCategoryInfo(article.category);
    const dateStr = formatDate(article.date);
    
    // Transliteruj sadržaj prema trenutnom pismu
    const title = transliterateText(article.title, currentScript);
    const categoryLabel = transliterateText(categoryInfo.label, currentScript);
    
    modalTitle.textContent = title;
    modalCategory.innerHTML = `<i class="${categoryInfo.icon} mr-2"></i>${categoryLabel}`;
    modalCategory.className = `inline-flex items-center px-4 py-2 rounded-full text-white font-bold ${categoryInfo.bgClass}`;
    modalDate.textContent = dateStr;
    
    // Content - transliteruj HTML sadržaj
    let content = '';
    if (article.content_html) {
        content = article.content_html;
    } else {
        // Fallback to plain text with paragraphs
        const paragraphs = article.content_text.split('\n\n');
        content = paragraphs
            .filter(p => p.trim().length > 0)
            .map(p => `<p class="mb-4">${transliterateText(p.trim(), currentScript)}</p>`)
            .join('');
    }
    
    // Transliteruj HTML sadržaj (samo tekst, ne tagove!)
    const transliteratedContent = transliterateHTML(content, currentScript);
    modalContent.innerHTML = transliteratedContent;
    
    // Transliteruj dugme "Zatvori"
    const closeModalBtn = document.getElementById('closeModalBtn');
    if (closeModalBtn) {
        const btnText = closeModalBtn.querySelector('.translatable');
        if (btnText) {
            const closeText = currentScript === 'latin' ? 'Zatvori' : 'Затвори';
            btnText.textContent = closeText;
        }
    }
    
    // Prikaži modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
    
    // Animacija
    setTimeout(() => {
        const modalInner = modal.querySelector('.modal-inner');
        if (modalInner) {
            modalInner.style.transform = 'translateY(0)';
            modalInner.style.opacity = '1';
        }
    }, 10);
}

// Zatvori modal
function closeModal() {
    const modal = document.getElementById('articleModal');
    if (!modal) return;
    
    const modalInner = modal.querySelector('.modal-inner');
    if (modalInner) {
        modalInner.style.transform = 'translateY(20px)';
        modalInner.style.opacity = '0';
    }
    
    setTimeout(() => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
    }, 300);
}

// Greška pri učitavanju
function showError() {
    const container = document.getElementById('blogArticlesContainer');
    if (!container) return;
    
    const errorText = currentScript === 'latin'
        ? 'Greška pri učitavanju članaka. Molimo osvežite stranicu.'
        : 'Грешка при учитавању чланака. Молимо освежите страницу.';
    
    container.innerHTML = `
        <div class="col-span-3 text-center py-12">
            <i class="fas fa-exclamation-triangle text-6xl text-red-500 mb-4"></i>
            <p class="text-xl text-gray-700">${errorText}</p>
        </div>
    `;
}

// Kategorija info
function getCategoryInfo(category) {
    const categories = {
        'oprema': {
            label: 'Опрема',
            labelLatin: 'Oprema',
            icon: 'fas fa-hiking',
            gradient: 'from-blue-500 to-blue-600',
            bgClass: 'bg-blue-600'
        },
        'ishrana': {
            label: 'Исхрана',
            labelLatin: 'Ishrana',
            icon: 'fas fa-apple-alt',
            gradient: 'from-green-500 to-green-600',
            bgClass: 'bg-green-600'
        },
        'savjeti': {
            label: 'Савјети',
            labelLatin: 'Savjeti',
            icon: 'fas fa-lightbulb',
            gradient: 'from-yellow-500 to-yellow-600',
            bgClass: 'bg-yellow-600'
        },
        'putopisi': {
            label: 'Путописи',
            labelLatin: 'Putopisi',
            icon: 'fas fa-mountain',
            gradient: 'from-purple-500 to-purple-600',
            bgClass: 'bg-purple-600'
        },
        'ostalo': {
            label: 'Остало',
            labelLatin: 'Ostalo',
            icon: 'fas fa-book',
            gradient: 'from-gray-500 to-gray-600',
            bgClass: 'bg-gray-600'
        }
    };
    
    const info = categories[category] || categories['ostalo'];
    
    // Vrati label prema trenutnom pismu
    return {
        ...info,
        label: currentScript === 'latin' ? info.labelLatin : info.label
    };
}

// Format datuma
function formatDate(dateStr) {
    const date = new Date(dateStr);
    
    const monthsCyrillic = [
        'јануар', 'фебруар', 'март', 'април', 'мај', 'јуни',
        'јули', 'август', 'септембар', 'октобар', 'новембар', 'децембар'
    ];
    
    const monthsLatin = [
        'januar', 'februar', 'mart', 'april', 'maj', 'juni',
        'juli', 'avgust', 'septembar', 'oktobar', 'novembar', 'decembar'
    ];
    
    const months = currentScript === 'latin' ? monthsLatin : monthsCyrillic;
    
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    
    return `${day}. ${month} ${year}.`;
}

// Inicijalizuj kad se stranica učita
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBlog);
} else {
    initBlog();
}
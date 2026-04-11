// ============================================================================
// BLOG SYSTEM - PED Majevica 1988
// Sa integrisanom transliteracijom Ćirilica ⇄ Latinica
// ============================================================================

// Globalne promenljive
let allArticles = [];
let filteredArticles = [];
let currentPage = 1;
const articlesPerPage = 6;
let currentScript = 'cyrillic'; // default

// Inicijalizacija
async function initBlog() {
    console.log('📚 Blog: Inicijalizacija...');
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
        console.log('📚 Blog: Fetching from:', apiUrl);
        // Use credentials for cross-origin requests
        const response = await fetch(apiUrl, {
          credentials: window.API_CONFIG ? window.API_CONFIG.getCredentials() : 'include'
        });
        console.log('📚 Blog: Response status:', response.status);
        const data = await response.json();
        console.log('📚 Blog: Data received:', data);
        
        // Handle both old format (data.posts) and new format (data.data.posts)
        allArticles = data.data?.posts || data.posts || [];
        console.log('📚 Blog: Total posts:', allArticles.length);
        
        if (allArticles.length === 0) {
            console.warn('📚 Blog: Nema članaka za prikaz');
        }
        
        filteredArticles = [...allArticles];

        // Sortiranje po datumu - NAJNOVIJI PRVO (sa error handling)
        try {
            allArticles.sort((a, b) => {
                const dateA = new Date(a.created_at || a.date || 0);
                const dateB = new Date(b.created_at || b.date || 0);
                if (isNaN(dateA.getTime())) return 1;
                if (isNaN(dateB.getTime())) return -1;
                return dateB - dateA; // Noviji prvo (DESC)
            });
            console.log('📚 Blog: Sortirano', allArticles.length, 'članaka');
        } catch (sortError) {
            console.error('📚 Blog: Greška pri sortiranju:', sortError);
        }

        filteredArticles = [...allArticles];

        // Proveri trenutno pismo iz transliteratora
        if (typeof transliterator !== 'undefined' && typeof transliterator.getCurrentScript === 'function') {
            currentScript = transliterator.getCurrentScript();
            console.log('📚 Blog: Current script:', currentScript);
        } else {
            console.log('📚 Blog: Transliterator nije dostupan, koristim default');
            currentScript = 'latin';
        }

        console.log('📚 Blog: Pozivam renderArticles()');
        renderArticles();
        
        console.log('📚 Blog: Pozivam setupEventListeners()');
        setupEventListeners();
        
        console.log('📚 Blog: Pozivam setupScriptChangeListener()');
        setupScriptChangeListener();
        
        console.log('📚 Blog: Inicijalizacija završena!');
    } catch (error) {
        console.error('Greška pri učitavanju članaka:', error);
        console.error('Stack trace:', error.stack);
        showError();
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
function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    
    if (query === '') {
        filteredArticles = [...allArticles];
    } else {
        filteredArticles = allArticles.filter(article => {
            const title = article.title.toLowerCase();
            const content = article.content_text.toLowerCase();
            
            // Pretraga i na ćirilici i na latinici
            return title.includes(query) || content.includes(query) ||
                   transliterateText(title, 'latin').toLowerCase().includes(query) ||
                   transliterateText(content, 'latin').toLowerCase().includes(query);
        });
    }
    
    currentPage = 1;
    renderArticles();
}

// Filter funkcija
function handleFilter(e) {
    const category = e.target.value;
    
    if (category === 'sve') {
        filteredArticles = [...allArticles];
    } else {
        filteredArticles = allArticles.filter(article => article.category === category);
    }
    
    currentPage = 1;
    renderArticles();
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

    const startIndex = (currentPage - 1) * articlesPerPage;
    const endIndex = startIndex + articlesPerPage;
    const articlesToShow = filteredArticles.slice(startIndex, endIndex);
    console.log('📚 Blog: Articles to show:', articlesToShow.length);

    if (articlesToShow.length === 0) {
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
    
    container.innerHTML = articlesToShow.map(article => {
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
    
    const totalPages = Math.ceil(filteredArticles.length / articlesPerPage);
    
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let html = '<div class="flex items-center justify-center space-x-2">';
    
    // Previous
    if (currentPage > 1) {
        html += `
            <button onclick="changePage(${currentPage - 1})"
                class="px-4 py-2 rounded-lg border-2 border-primary-blue text-primary-blue hover:bg-primary-blue hover:text-white transition-all duration-300">
                <i class="fas fa-chevron-left"></i>
            </button>
        `;
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `
                <button class="px-4 py-2 rounded-lg bg-primary-red text-white font-bold">
                    ${i}
                </button>
            `;
        } else if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 1) {
            html += `
                <button onclick="changePage(${i})"
                    class="px-4 py-2 rounded-lg border-2 border-gray-300 text-gray-700 hover:border-primary-blue hover:text-primary-blue transition-all duration-300">
                    ${i}
                </button>
            `;
        } else if (Math.abs(i - currentPage) === 2) {
            html += `<span class="px-2 text-gray-400">...</span>`;
        }
    }
    
    // Next
    if (currentPage < totalPages) {
        html += `
            <button onclick="changePage(${currentPage + 1})"
                class="px-4 py-2 rounded-lg border-2 border-primary-blue text-primary-blue hover:bg-primary-blue hover:text-white transition-all duration-300">
                <i class="fas fa-chevron-right"></i>
            </button>
        `;
    }
    
    html += '</div>';
    paginationContainer.innerHTML = html;
}

// Promena stranice
function changePage(page) {
    currentPage = page;
    renderArticles();
    
    // Scroll to top of blog section
    const blogSection = document.getElementById('blog');
    if (blogSection) {
        blogSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Otvori članak
function openArticle(articleId) {
    const article = allArticles.find(a => a.id === articleId);
    if (!article) return;
    
    // Ako je kratak članak (<300 reči) - otvori u modalu
    if (article.word_count < 300) {
        showModal(article);
    } else {
        // Dugi članak - otvori u modalu (kasnije možemo dodati zasebne HTML stranice)
        showModal(article);
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
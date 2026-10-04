/**
 * Serbian Transliterator - Ćirilica ⇄ Latinica
 * PED Majevica 1988
 * 
 * Preslovljava tekst između ćirilice i latinice sa automatskim pamćenjem izbora
 */

class SerbianTransliterator {
    constructor() {
        // Cyrillic to Latin mapping
        this.toLatin = {
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
            'Ђ': 'Đ', 'Е': 'E', 'Ж': 'Ž', 'З': 'Z', 'И': 'I',
            'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M',
            'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R',
            'С': 'S', 'Т': 'T', 'Ћ': 'Ć', 'У': 'U', 'Ф': 'F',
            'Х': 'H', 'Ц': 'C', 'Ч': 'Č', 'Џ': 'Dž', 'Ш': 'Š',
            
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'ђ': 'đ', 'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'i',
            'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm',
            'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r',
            'с': 's', 'т': 't', 'ћ': 'ć', 'у': 'u', 'ф': 'f',
            'х': 'h', 'ц': 'c', 'ч': 'č', 'џ': 'dž', 'ш': 'š'
        };
        
        // Latin to Cyrillic mapping
        this.toCyrillic = {};
        for (let [cyr, lat] of Object.entries(this.toLatin)) {
            this.toCyrillic[lat] = cyr;
        }
        
        this.currentScript = this.getPreference();
    }
    
    /**
     * Normalize mixed script text to pure Latin first
     * @param {string} text 
     * @returns {string}
     */
    normalizeToLatin(text) {
        if (!text) return '';
        
        let output = '';
        for (let char of text) {
            output += this.toLatin[char] || char;
        }
        return output;
    }
    
    /**
     * Check if text is in Cyrillic script
     * @param {string} text 
     * @returns {boolean}
     */
    isCyrillic(text) {
        // Count Cyrillic characters
        const cyrillicChars = text.match(/[А-Яа-яЁё]/g);
        // Count Latin characters  
        const latinChars = text.match(/[A-Za-z]/g);
        
        if (!cyrillicChars && !latinChars) return null; // No letters
        if (!cyrillicChars) return false; // Only Latin
        if (!latinChars) return true; // Only Cyrillic
        
        // If mixed, return majority
        return cyrillicChars.length > latinChars.length;
    }
    
    /**
     * Transliterate text between scripts
     * @param {string} text - Text to transliterate
     * @param {string} direction - 'latin' or 'cyrillic'
     * @returns {string} Transliterated text
     */
    transliterate(text, direction = 'latin') {
        if (!text) return '';
        
        // CRITICAL FIX: If text is mixed, normalize to Latin first
        const textIsCyrillic = this.isCyrillic(text);
        const isMixed = textIsCyrillic === null || (text.match(/[А-Яа-я]/g) && text.match(/[A-Za-z]/g));
        
        let normalizedText = text;
        
        // If converting to Cyrillic and text has ANY Cyrillic chars, normalize to Latin first
        if (direction === 'cyrillic' && (isMixed || textIsCyrillic)) {
            normalizedText = this.normalizeToLatin(text);
        }
        
        // Check if normalized text is already in target script
        const isTargetScript = direction === 'cyrillic' ? 
            this.isCyrillic(normalizedText) === true : 
            this.isCyrillic(normalizedText) === false;
        
        if (isTargetScript) {
            return normalizedText;
        }
        
        let result = normalizedText;
        
        if (direction === 'cyrillic') {
            // Latin to Cyrillic - handle digraphs first
            result = result.replace(/Lj/g, 'Љ').replace(/lj/g, 'љ');
            result = result.replace(/Nj/g, 'Њ').replace(/nj/g, 'њ');
            result = result.replace(/Dž/g, 'Џ').replace(/dž/g, 'џ');
            
            // Then single characters
            let output = '';
            for (let char of result) {
                output += this.toCyrillic[char] || char;
            }
            return output;
        } else {
            // Cyrillic to Latin
            let output = '';
            for (let char of result) {
                output += this.toLatin[char] || char;
            }
            return output;
        }
    }
    
    /**
     * Toggle script on entire page
     * @param {string} targetScript - 'latin' or 'cyrillic'
     */
    togglePageScript(targetScript) {
        // Convert all text nodes in body
        const walk = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            { acceptNode: (node) => this._acceptNode(node) }
        );

        let node;
        while (node = walk.nextNode()) {
            if (node.nodeValue && node.nodeValue.trim()) {
                node.nodeValue = this.transliterate(node.nodeValue, targetScript);
            }
        }
        
        // Save preference
        this.currentScript = targetScript;
        localStorage.setItem('ped-script-preference', targetScript);
    }
    
    /**
     * Koji tekstualni cvorovi se prevode (isto pravilo za cijelu stranicu i za naknadno dodate dijelove)
     */
    _acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;

        const tagName = parent.tagName;
        if (tagName === 'SCRIPT' || tagName === 'STYLE' || tagName === 'CODE' || tagName === 'PRE' ||
            tagName === 'TEXTAREA') {
            return NodeFilter.FILTER_REJECT;
        }
        // dugmad za izbor pisma imaju fiksan tekst
        if (parent.classList.contains('script-btn')) return NodeFilter.FILTER_REJECT;
        // .no-translate i translate="no" (e-mail, telefon...) se ne diraju
        if (parent.closest('.no-translate')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
    }

    /**
     * Stranice sa data-script-sync: pismo prati izbor posjetioca (zadano: latinica) i za sadrzaj
     * koji se ucita naknadno (clanci, staze, dogadjaji, izmjene iz admina).
     */
    isSyncEnabled() {
        return document.documentElement.hasAttribute('data-script-sync');
    }

    convertSubtree(root) {
        if (!root) return;
        if (root.nodeType === Node.TEXT_NODE) {
            if (root.nodeValue && root.nodeValue.trim() && this._acceptNode(root) === NodeFilter.FILTER_ACCEPT) {
                root.nodeValue = this.transliterate(root.nodeValue, this.currentScript);
            }
            return;
        }
        if (root.nodeType !== Node.ELEMENT_NODE) return;
        const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => this._acceptNode(n) });
        let node;
        while ((node = walk.nextNode())) {
            if (node.nodeValue && node.nodeValue.trim()) {
                node.nodeValue = this.transliterate(node.nodeValue, this.currentScript);
            }
        }
    }

    startObserver() {
        if (this._observer || !document.body) return;
        this._observer = new MutationObserver((mutations) => {
            for (const m of mutations) m.addedNodes.forEach((n) => this.convertSubtree(n));
        });
        this._observer.observe(document.body, { childList: true, subtree: true });
    }

    /**
     * Get stored script preference
     * @returns {string} 'latin' or 'cyrillic'
     */
    getPreference() {
        // Javne stranice (data-script-sync): zadano je latinica, kao ostatak teksta; ćirilica je izbor posjetioca.
        // Ostale stranice (admin) zadržavaju staro ponašanje.
        const fallback = this.isSyncEnabled() ? 'latin' : 'cyrillic';
        return localStorage.getItem('ped-script-preference') || fallback;
    }
    
    /**
     * Apply stored preference on page load
     */
    applyPreference() {
        const pref = this.getPreference();
        if (this.isSyncEnabled()) {
            // oba pisma: stranica (i sadrzaj koji se tek ucitava) prati izbor posjetioca
            if (document.body) {
                this.togglePageScript(pref);
                this.startObserver();
            }
            return;
        }
        if (pref === 'latin') {
            this.togglePageScript('latin');
        }
    }

    /**
     * Get current script
     * @returns {string} 'latin' or 'cyrillic'
     */
    getCurrentScript() {
        return this.currentScript;
    }
}

// Create and export global instance
const transliterator = new SerbianTransliterator();

// Convenience function for simple use
function transliterate(text, direction = 'latin') {
    return transliterator.transliterate(text, direction);
}

// Switch script function for UI buttons
function switchScript(targetScript) {
    // Update desktop button states
    const cyrillicBtn = document.getElementById('btn-cyrillic');
    const latinBtn = document.getElementById('btn-latin');
    
    if (cyrillicBtn && latinBtn) {
        cyrillicBtn.classList.toggle('active', targetScript === 'cyrillic');
        latinBtn.classList.toggle('active', targetScript === 'latin');
    }
    
    // Update mobile button states
    const cyrillicBtnMobile = document.getElementById('btn-cyrillic-mobile');
    const latinBtnMobile = document.getElementById('btn-latin-mobile');
    
    if (cyrillicBtnMobile && latinBtnMobile) {
        cyrillicBtnMobile.classList.toggle('active', targetScript === 'cyrillic');
        latinBtnMobile.classList.toggle('active', targetScript === 'latin');
    }
    
    // Convert page
    transliterator.togglePageScript(targetScript);
}

// Auto-apply preference on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        transliterator.applyPreference();
        
        // Update button states
        const savedScript = transliterator.getPreference();
        
        // Desktop buttons
        const cyrillicBtn = document.getElementById('btn-cyrillic');
        const latinBtn = document.getElementById('btn-latin');
        
        if (cyrillicBtn && latinBtn) {
            cyrillicBtn.classList.toggle('active', savedScript === 'cyrillic');
            latinBtn.classList.toggle('active', savedScript === 'latin');
        }
        
        // Mobile buttons
        const cyrillicBtnMobile = document.getElementById('btn-cyrillic-mobile');
        const latinBtnMobile = document.getElementById('btn-latin-mobile');
        
        if (cyrillicBtnMobile && latinBtnMobile) {
            cyrillicBtnMobile.classList.toggle('active', savedScript === 'cyrillic');
            latinBtnMobile.classList.toggle('active', savedScript === 'latin');
        }
    });
} else {
    transliterator.applyPreference();
}
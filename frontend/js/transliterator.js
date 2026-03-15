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
            {
                acceptNode: function(node) {
                    // Skip script, style, and code tags
                    const parent = node.parentElement;
                    if (!parent) return NodeFilter.FILTER_REJECT;
                    
                    const tagName = parent.tagName;
                    if (tagName === 'SCRIPT' || 
                        tagName === 'STYLE' || 
                        tagName === 'CODE' ||
                        tagName === 'PRE') {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // Skip script toggle buttons - FIKSIRAN TEKST!
                    if (parent.classList.contains('script-btn')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    // 🔒 Skip .no-translate elements
                    if (parent.closest('.no-translate')) {
                        return NodeFilter.FILTER_REJECT;
                    }
                    
                    return NodeFilter.FILTER_ACCEPT;
                }
            }
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
     * Get stored script preference
     * @returns {string} 'latin' or 'cyrillic'
     */
    getPreference() {
        return localStorage.getItem('ped-script-preference') || 'cyrillic';
    }
    
    /**
     * Apply stored preference on page load
     */
    applyPreference() {
        const pref = this.getPreference();
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
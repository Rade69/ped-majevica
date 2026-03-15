# 🏔️ PED Majevica 1988 - Planinarsko Društvo

Moderan, responsive web sajt za Planinsko ekološko društvo Majevica osnovano 1988.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4.1-38B2AC?logo=tailwind-css)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🎨 **Moderni dizajn** sa custom bojama i animacijama
- 🌙 **Dark mode** support
- 📱 **Fully responsive** (mobile-first pristup)
- ⚡ **Optimizovani performansi** (lazy loading, tree-shaking)
- ♿ **Accessibility** features
- 🎯 **SEO optimizovan**

## 🛠️ Tech Stack

- **HTML5** - Semantički markup
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **Vanilla JavaScript (ES6+)** - Bez dependencies
- **Font Awesome 6.4** - Ikone
- **Google Fonts** - Inter & Playfair Display

## 📂 Struktura Projekta

```
ped-majevica/
├── README.md                       # Glavna dokumentacija
├── PROJECT_STRUCTURE.md            # Detaljna struktura fajlova
├── docs/                           # Dokumentacija
│   ├── ADMIN_USERS_GUIDE.md
│   ├── IMAGE_GUIDE.md
│   └── deployment/
├── deployment/                     # Deployment fajlovi
│   ├── vps/
│   ├── netlify/
│   └── render/
├── backend/                        # Python Flask Backend
│   ├── app/                        # Flask aplikacija
│   ├── data/                       # JSON podaci
│   ├── scripts/                    # Skripte i alati
│   ├── tests/                      # Test suite
│   ├── migrations/                 # Database migracije
│   └── instance/                   # Local podaci
└── frontend/                       # Frontend
    ├── pages/                      # HTML stranice
    ├── js/                         # JavaScript moduli
    └── assets/                     # Statički resursi
```

Za detaljnu strukturu, pogledajte [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v16+ preporučeno)
- npm (dolazi sa Node.js)

### Instalacija

```bash
# 1. Kloniraj repo (ili preuzmi ZIP)
git clone https://github.com/tvoj-username/ped-majevica.git
cd ped-majevica

# 2. Instaliraj dependencies
npm install

# 3. Pokreni development server sa live reload
npm run dev
```

Otvori `index.html` u browseru - promjene u CSS-u će se automatski rebuild-ovati!

### Production Build

```bash
# Generiši minified CSS za produkciju
npm run build
```

## 📜 NPM Scripts

| Script                | Opis                                           |
| --------------------- | ---------------------------------------------- |
| `npm run dev`         | Development mode sa watcherom (prati promjene) |
| `npm run build`       | Production build (minified CSS)                |
| `npm run build:debug` | Debug build (bez minify-a, za debugging)       |

## 🎨 Customization

### Boje

Promijeni boje u `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'primary-red': '#D62828',     // Glavna crvena
        'primary-blue': '#003366',    // Glavna plava
        'secondary-gold': '#FFD700',  // Zlatna (akcenti)
        // ... dodaj svoje boje
      }
    }
  }
}
```

### Komponente

Kreiraj custom komponente u `assets/css/input.css`:

```css
@layer components {
  .custom-button {
    @apply px-6 py-3 bg-primary-red text-white rounded-lg;
    @apply hover:bg-red-dark transition-all duration-300;
  }
}
```

## 🌙 Dark Mode

Dark mode se automatski toggle-uje klikom na ikonu mjeseca u navigaciji.

Koristi `dark:` prefix za dark mode stilove:

```html
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Sadržaj
</div>
```

## 📱 Responsive Breakpoints

| Breakpoint    | Width    | Tailwind Class |
| ------------- | -------- | -------------- |
| Mobile        | < 640px  | (default)      |
| Tablet        | ≥ 768px  | `md:`          |
| Desktop       | ≥ 1024px | `lg:`          |
| Large Desktop | ≥ 1280px | `xl:`          |

Primjer:

```html
<div class="text-base md:text-lg lg:text-xl">
  Responsive text
</div>
```

## 🔧 Troubleshooting

### Problem: `output.css` je prazan

**Rješenje:**
```bash
# Provjeri da li su content paths tačni u tailwind.config.js
# Rebuild CSS
npm run build:debug
```

### Problem: Stilovi se ne primjenjuju

**Rješenje:**
```bash
# Hard refresh browser
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)

# Ili obriši browser cache
```

### Problem: `npm` nije prepoznat

**Rješenje:**
- Instaliraj [Node.js](https://nodejs.org/)
- Restartuj terminal nakon instalacije

## 📈 Performance

- ✅ **CSS Bundle:** ~150 KB minified (~95% manje od CDN-a)
- ✅ **First Contentful Paint:** < 1.5s
- ✅ **Lighthouse Score:** 90+ (Performance, Accessibility, Best Practices, SEO)

## 🤝 Contributing

Doprinosi su dobrodošli! Ako želiš da pomogneš:

1. Fork-uj projekat
2. Kreiraj feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit promjene (`git commit -m 'Add: Amazing feature'`)
4. Push na branch (`git push origin feature/AmazingFeature`)
5. Otvori Pull Request

## 📄 License

Distribuirano pod MIT licencom. Vidi `LICENSE` fajl za više informacija.

## 📧 Kontakt

**PED Majevica 1988**
- Email: radovan1969@gmail.com
- Website: https://pedmajevica.ba
- Facebook: [PED Majevica](https://facebook.com/pedmajevica)

## 🙏 Credits

- Dizajn i development: [Radovan Stojanović]
- Slike: [Unsplash](https://unsplash.com)
- Ikone: [Font Awesome](https://fontawesome.com)
- Framework: [Tailwind CSS](https://tailwindcss.com)

---

**Napravljeno sa ❤️ za ljubitelje planina** 🏔️

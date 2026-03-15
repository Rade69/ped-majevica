# 📸 Image Upload & Optimization Guide - PED Majevica

## 📋 Folder Struktura

```
frontend/assets/images/
├── blog/           # Blog članci slike
├── trails/         # Planinarske staze fotografije
├── gallery/        # Galerija fotografija
├── icons/          # Ikone i mali grafički elementi
└── hero/           # Hero/Banner slike
```

---

## 🎯 Optimalne Dimenzije

### Blog Članci

| Tip | Dimenzije | Format | Max Size |
|-----|-----------|--------|----------|
| **Header Image** | 1200x630px | WebP | 200KB |
| **Thumbnail** | 600x400px | WebP | 100KB |
| **In-content** | 800x600px | WebP | 150KB |

### Staze (Trails)

| Tip | Dimenzije | Format | Max Size |
|-----|-----------|--------|----------|
| **Hero Image** | 1200x800px | WebP | 300KB |
| **Gallery** | 800x600px | WebP | 150KB |
| **Map** | 1000x800px | PNG | 200KB |

### Galerija

| Tip | Dimenzije | Format | Max Size |
|-----|-----------|--------|----------|
| **Thumbnail** | 400x300px | WebP | 80KB |
| **Lightbox Full** | 1920x1080px | WebP | 500KB |

---

## 🛠️ Alati Za Optimizaciju

### 1. **Squoosh (Google) - PREPORUČUJEM** ⭐

**URL**: https://squoosh.app/

**Kako koristiti:**

1. **Upload sliku**
   - Drag & drop ili klikni "Select an image"

2. **Izaberi format** (desna strana):
   - **WebP** (najbolji)
   - Ili **MozJPEG** (JPEG alternative)

3. **Podesi Quality**:
   - Blog slike: **75-80%**
   - Galerija: **80-85%**
   - Thumbnails: **70-75%**

4. **Resize** (ako treba):
   - Klikni na "Resize"
   - Unesi target width/height
   - Maintain aspect ratio ✓

5. **Download**
   - Poredi original vs compressed size
   - Download kad si zadovoljan

**Primer:**
```
Original: 3.2 MB (4000x3000px)
After:    180 KB (1200x800px, WebP 80%)
Savings:  94% 🎉
```

---

### 2. **TinyPNG/TinyJPG**

**URL**: https://tinypng.com/

**Kako koristiti:**

1. Upload do 20 slika odjednom
2. Automatski compression
3. Download ZIP sa svim slikama

**Dobro za:** Batch processing JPEG/PNG

---

### 3. **ImageOptim (Mac)**

**URL**: https://imageoptim.com/

**Dobro za:** Bulk optimization lokalno

---

## 📝 Korak-Po-Korak: Dodavanje Slika Na Blog

### Scenario: Dodaješ sliku za blog članak "Oprema Za Planinarenje"

#### Korak 1: Pripremi Sliku

1. **Original slika:**
   - Ime: `DSC_1234.jpg`
   - Dimenzije: 4000x3000px
   - Veličina: 3.5 MB

2. **Otvori Squoosh**: https://squoosh.app/

3. **Upload** `DSC_1234.jpg`

4. **Podesi:**
   - Format: **WebP**
   - Quality: **80%**
   - Resize: Width **1200px** (height će biti automatski 900px)

5. **Download** kao `oprema-planinarenje-hero.webp`

6. **Ponovi za thumbnail**:
   - Resize: Width **600px**
   - Quality: **75%**
   - Save kao: `oprema-planinarenje-thumb.webp`

#### Korak 2: Upload Na Sajt

```bash
# Kopiraj slike u projekat
cp ~/Downloads/oprema-planinarenje-hero.webp frontend/assets/images/blog/
cp ~/Downloads/oprema-planinarenje-thumb.webp frontend/assets/images/blog/
```

#### Korak 3: Dodaj U JSON (backend/data/posts.json)

```json
{
  "id": 1,
  "title": "Oprema Za Planinarenje",
  "slug": "oprema-za-planinarenje",
  "images": [
    "/assets/images/blog/oprema-planinarenje-hero.webp",
    "/assets/images/blog/oprema-planinarenje-thumb.webp"
  ],
  "preview": "/assets/images/blog/oprema-planinarenje-thumb.webp",
  // ... rest of data
}
```

#### Korak 4: Migracija U Bazu

```bash
cd backend
python migrate_json_to_db.py
```

#### Korak 5: Commit & Deploy

```bash
git add frontend/assets/images/blog/
git add backend/data/posts.json
git commit -m "Add images for blog post: Oprema Za Planinarenje"
git push origin main
```

---

## 🏔️ Dodavanje Slika Za Staze

### Primer: Staza "Javorak"

#### Priprema Slika

**Potrebno:**
1. Hero slika (1200x800px)
2. 3-5 galerija slika (800x600px)
3. Mapa staze (1000x800px, PNG)

#### Imenovanje Fajlova

```
staza-javorak-hero.webp          (1200x800px, 250KB)
staza-javorak-01.webp             (800x600px, 120KB)
staza-javorak-02.webp             (800x600px, 115KB)
staza-javorak-03.webp             (800x600px, 130KB)
staza-javorak-mapa.png            (1000x800px, 180KB)
```

#### Folder Lokacija

```
frontend/assets/images/trails/
├── staza-javorak-hero.webp
├── staza-javorak-01.webp
├── staza-javorak-02.webp
├── staza-javorak-03.webp
└── staza-javorak-mapa.png
```

#### JSON Update (backend/data/trails.json)

```json
{
  "id": 1,
  "name": "Јаворак",
  "slug": "javorak",
  "images": [
    "/assets/images/trails/staza-javorak-hero.webp",
    "/assets/images/trails/staza-javorak-01.webp",
    "/assets/images/trails/staza-javorak-02.webp",
    "/assets/images/trails/staza-javorak-03.webp"
  ],
  "map_image": "/assets/images/trails/staza-javorak-mapa.png",
  // ... rest of data
}
```

---

## 🖼️ Galerija Fotografija

### Batch Upload

1. **Pripremi sve slike**:
   - 10-20 fotografija
   - Resize to 1920x1080px (full)
   - Quality: 85%

2. **Kreiraj thumbnails**:
   - 400x300px
   - Quality: 70%

3. **Imenovanje**:
   ```
   galerija-2024-janvar-01.webp
   galerija-2024-janvar-01-thumb.webp
   galerija-2024-janvar-02.webp
   galerija-2024-janvar-02-thumb.webp
   ...
   ```

4. **Upload**:
   ```bash
   cp ~/Downloads/galerija-* frontend/assets/images/gallery/
   ```

---

## ✅ Checklist Pre Upload-a

### Za Svaku Sliku:

- [ ] **Format**: WebP (ili JPEG ako WebP nije moguć)
- [ ] **Dimenzije**: Prema tabeli gore
- [ ] **Compression**: 70-85% quality
- [ ] **Veličina fajla**: Ispod max size
- [ ] **Ime fajla**: Lowercase, no spaces, dash-separated
      - ✅ `staza-javorak-hero.webp`
      - ❌ `Staza Javorak Hero.jpg`
- [ ] **Copyright**: Proveri da imaš pravo koristiti sliku

### Pre Commit-a:

- [ ] Slike su u pravom folderu
- [ ] JSON fajlovi ažurirani
- [ ] Testirano lokalno
- [ ] Git add images + JSON
- [ ] Commit sa opisnom porukom

---

## 🔧 Advanced: Responsive Images

### HTML Primer (za budućnost)

```html
<picture>
  <!-- WebP za moderne browsere -->
  <source srcset="/assets/images/blog/oprema-hero.webp" type="image/webp">

  <!-- Fallback JPEG za stare browsere -->
  <img src="/assets/images/blog/oprema-hero.jpg"
       alt="Planinarenje oprema"
       loading="lazy"
       width="1200"
       height="800">
</picture>
```

### Responsive Sizes

```html
<img srcset="/assets/images/blog/oprema-400.webp 400w,
             /assets/images/blog/oprema-800.webp 800w,
             /assets/images/blog/oprema-1200.webp 1200w"
     sizes="(max-width: 600px) 400px,
            (max-width: 900px) 800px,
            1200px"
     src="/assets/images/blog/oprema-800.webp"
     alt="Oprema">
```

---

## 📊 Performance Tips

### 1. **Lazy Loading**

```html
<img src="slika.webp" loading="lazy" alt="Opis">
```

### 2. **Width/Height Attributes**

```html
<img src="slika.webp" width="1200" height="800" alt="Opis">
```

Prevents layout shift!

### 3. **CDN (Opciono)**

Za buduće:
- Cloudflare Images
- ImageKit.io
- Cloudinary

---

## 🎨 Ikone Za Blog Kategorije

### Trenutno: Font Awesome Ikone

```html
<i class="fas fa-hiking"></i>        <!-- Oprema -->
<i class="fas fa-apple-alt"></i>     <!-- Ishrana -->
<i class="fas fa-lightbulb"></i>     <!-- Savjeti -->
<i class="fas fa-mountain"></i>      <!-- Putopisi -->
```

### Zamena Sa Fotografijama

#### Opcija 1: Mali Ikone (64x64px)

```
frontend/assets/images/icons/
├── category-oprema.webp      (64x64px, 10KB)
├── category-ishrana.webp     (64x64px, 10KB)
├── category-savjeti.webp     (64x64px, 10KB)
└── category-putopisi.webp    (64x64px, 10KB)
```

**Gdje naći:**
- **Unsplash**: https://unsplash.com/ (besplatno)
- **Pexels**: https://www.pexels.com/ (besplatno)
- **Pixabay**: https://pixabay.com/ (besplatno)

**Keywords:**
- Oprema: "hiking gear", "backpack icon"
- Ishrana: "healthy food", "apple icon"
- Savjeti: "lightbulb", "idea icon"
- Putopisi: "mountain", "hiking trail"

#### Opcija 2: Header Fotografije Za Blog Kartice

Umesto gradient pozadine, koristi pravu fotografiju:

```html
<!-- Trenutno: Gradient -->
<div class="bg-gradient-to-br from-blue-500 to-blue-600">
  <i class="fas fa-image text-white/30 text-8xl"></i>
</div>

<!-- Novi: Prava fotografija -->
<div class="relative h-48 overflow-hidden">
  <img src="/assets/images/blog/oprema-thumb.webp"
       alt="Oprema"
       class="w-full h-full object-cover">
</div>
```

---

## 📚 Resursi

### Besplatne Stock Fotografije:

1. **Unsplash** - https://unsplash.com/
   - Visok kvalitet
   - Besplatno za komercijalnu upotrebu
   - Attribution nije obavezna (ali je fina)

2. **Pexels** - https://www.pexels.com/
   - Video + Photo
   - Besplatno

3. **Pixabay** - https://pixabay.com/
   - 2.8M+ slika
   - Besplatno

### Tools:

- **Squoosh**: https://squoosh.app/
- **TinyPNG**: https://tinypng.com/
- **Remove.bg**: https://www.remove.bg/ (ukloni pozadinu)
- **Canva**: https://www.canva.com/ (edit/resize)

---

## 🆘 Troubleshooting

### Problem: Slika je previše velika

**Rešenje:**
1. Resize u Squoosh
2. Smanji quality na 70-75%
3. Proveri da li je WebP format

### Problem: Slika se ne prikazuje

**Check:**
1. Da li je path tačan? `/assets/images/blog/slika.webp`
2. Da li je fajl commitovan i pushovan?
3. Da li browser podržava WebP? (pravi JPEG fallback)

### Problem: Layout shift kada se slika učita

**Rešenje:**
```html
<img src="slika.webp"
     width="1200"
     height="800"
     alt="Opis">
```

---

**Datum kreiranja**: 12. Januar 2026
**Autor**: Claude Sonnet 4.5
**Projekat**: PED Majevica 1988

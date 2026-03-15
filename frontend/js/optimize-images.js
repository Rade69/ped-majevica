// optimize-images.js - pokreni jednom za optimizaciju slika
const sharp = require('sharp');
const fs = require('fs-extra');
const path = require('path');

const imageConfigs = {
  'trail-cards': [
    { width: 400, quality: 80 },
    { width: 800, quality: 85 },
    { width: 1200, quality: 90 }
  ],
  'hero': [
    { width: 800, quality: 85 },
    { width: 1600, quality: 90 },
    { width: 2400, quality: 95 }
  ],
  'gallery': [
    { width: 400, quality: 80 },
    { width: 800, quality: 85 }
  ]
};

async function optimizeImages() {
  console.log('🖼️  Optimizacija slika...');

  // Kreiraj folder strukturu
  await fs.ensureDir('assets/images/optimized/trails');
  await fs.ensureDir('assets/images/optimized/hero');
  await fs.ensureDir('assets/images/optimized/gallery');

  // TODO: Ovde dodaj svoje slike za optimizaciju
  console.log('✅ Folder struktura kreirana');
  console.log('📝 Dodaj svoje slike u assets/images/raw/ pa pokreni skriptu');
}

if (require.main === module) {
  optimizeImages().catch(console.error);
}
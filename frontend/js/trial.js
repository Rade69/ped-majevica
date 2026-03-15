// ============================================
// PED MAJEVICA 1988 - TRAIL MODAL SYSTEM
// ============================================

console.log('🏔️ Trail Modal System loaded');

// Podaci o stazama
const trailsData = {
    1: {
        name: "Velika staza - Orlovič (1180m)",
        difficulty: "Teška",
        duration: "6-7 sati",
        distance: "12 km",
        elevation: "800m",
        description: "Najpoznatija staza PED Majevica koja vodi do vrha Orlovič (1180m). Ova staza nudi spektakularne poglede na okolne planine i dolinu. Preporučuje se za iskusne planinare sa dobrom fizičkom kondicijom.",
        features: [
            "Obeležena planinarska staza",
            "Pogled na 360° sa vrha",
            "Prirodni izvori vode na pola puta",
            "Raznovrsna flora i fauna",
            "Tradicionalno planinarski cilj od 1988."
        ],
        equipment: [
            "Planinske cipele (obavezno)",
            "Dovoljno vode (min. 2L)",
            "Zaštita od sunca",
            "GPS uređaj ili mapa",
            "Prva pomoć"
        ],
        warning: "Staza je zahtevna i nije preporučljiva za početnike. Obavezno proverite vremensku prognozu pre polaska.",
        contact: "+387 65 581 354"
    },
    2: {
        name: "Mala staza - Porodična (450m)",
        difficulty: "Lagana",
        duration: "2-3 sata",
        distance: "5 km",
        elevation: "250m",
        description: "Idealna staza za početnike i porodice sa decom. Ugodna šetnja kroz šumu sa blagim usponom. Pogodna za sve starosne kategorije.",
        features: [
            "Dobro održavana staza",
            "Piknik zona na polovini puta",
            "Edukativne table o lokalnoj flori",
            "Sigurna za decu",
            "Dostupna tokom cele godine"
        ],
        equipment: [
            "Udobna sportska obuća",
            "Flašica vode",
            "Laka jakna (po potrebi)",
            "Foto aparat za uspomene"
        ],
        warning: "Staza je bezbedna, ali ipak preporučujemo nadzor dece.",
        contact: "+387 65 581 354"
    },
    3: {
        name: "Novakova pećina (720m)",
        difficulty: "Srednja",
        duration: "4-5 sati",
        distance: "8 km",
        elevation: "450m",
        description: "Mistična pećina smeštena u srcu Majevice. Kombinuje planinarenje sa speleološkom avanturom. Savršena za avanturiste koji žele nešto više od obične planinske staze.",
        features: [
            "Istorijska pećina sa legendama",
            "Kombinacija staze i pećinskog istraživanja",
            "Spektakularan pogled na dolinu",
            "Bogata istorija i tradicija",
            "Idealno za fotografe"
        ],
        equipment: [
            "Planinske cipele (obavezno)",
            "Baterijska lampa (za pećinu)",
            "Voda (1.5L)",
            "Lagana jakna",
            "Mobilni telefon"
        ],
        warning: "Pećina zahteva oprez. Obavezno posetite sa iskusnim vodičem ili u grupi.",
        contact: "+387 65 581 354"
    }
};

// Otvori modal
function openTrailModal(trailId) {
    console.log('🗺️ Opening trail modal:', trailId);

    // First try API data, then fallback to hardcoded data
    let trail = null;

    if (window.trailsDataFromAPI && window.trailsDataFromAPI.length > 0) {
        const apiTrail = window.trailsDataFromAPI.find(t => t.id === parseInt(trailId));
        if (apiTrail) {
            // Convert API format to display format
            trail = {
                name: apiTrail.name,
                difficulty: apiTrail.difficulty || 'Nepoznato',
                duration: apiTrail.duration_hours ? `${apiTrail.duration_hours} sati` : 'Nepoznato',
                distance: apiTrail.distance_km ? `${apiTrail.distance_km} km` : 'Nepoznato',
                elevation: apiTrail.elevation_gain_m ? `${apiTrail.elevation_gain_m}m` : 'Nepoznato',
                description: apiTrail.description || 'Opis nije dostupan.',
                features: [],
                equipment: [],
                warning: apiTrail.warning || '',
                contact: apiTrail.contact || '+387 65 581 354'
            };

            // Use custom features from database if available
            if (apiTrail.features && apiTrail.features.length > 0) {
                trail.features = apiTrail.features;
            } else {
                // Fallback: Build features from boolean flags
                if (apiTrail.scenic_views) trail.features.push('Panoramski pogledi');
                if (apiTrail.water_sources) trail.features.push('Izvori vode');
                if (apiTrail.shelters) trail.features.push('Skloništa/planinarski dom');
                if (apiTrail.start_point) trail.features.push(`Početak: ${apiTrail.start_point}`);
                if (apiTrail.end_point) trail.features.push(`Kraj: ${apiTrail.end_point}`);
                if (apiTrail.region) trail.features.push(`Region: ${apiTrail.region}`);
            }

            // Use custom equipment from database if available
            if (apiTrail.equipment && apiTrail.equipment.length > 0) {
                trail.equipment = apiTrail.equipment;
            } else {
                // Default equipment
                trail.equipment = [
                    'Planinske cipele',
                    'Dovoljno vode',
                    'Zaštita od sunca',
                    'Mobilni telefon'
                ];
            }

            console.log('✅ Using API trail data:', trail.name);
        }
    }

    // Fallback to hardcoded data
    if (!trail) {
        trail = trailsData[trailId];
    }

    if (!trail) {
        console.error('❌ Trail not found:', trailId);
        return;
    }
    
    const modal = document.getElementById('trailModal');
    const modalTitle = document.getElementById('modalTrailName');
    const modalContent = document.getElementById('modalTrailContent');
    
    if (!modal || !modalTitle || !modalContent) {
        console.error('❌ Modal elements not found');
        return;
    }
    
    // Postavi naslov
    modalTitle.textContent = trail.name;
    
    // Generiši sadržaj sa INLINE stilovima (ne zavisi od Tailwind-a)
    modalContent.innerHTML = `
        <div style="padding: 24px;">
            <!-- Info kartice -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">
                <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); padding: 20px; border-radius: 12px; border: 2px solid #fecaca; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px; font-weight: 500;">Težina</div>
                    <div style="font-size: 22px; font-weight: bold; color: #003366;">${trail.difficulty}</div>
                </div>
                <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 20px; border-radius: 12px; border: 2px solid #bfdbfe; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px; font-weight: 500;">Trajanje</div>
                    <div style="font-size: 22px; font-weight: bold; color: #003366;">${trail.duration}</div>
                </div>
                <div style="background: linear-gradient(135deg, #fefce8 0%, #fef08a 100%); padding: 20px; border-radius: 12px; border: 2px solid #fde047; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="font-size: 13px; color: #666; margin-bottom: 6px; font-weight: 500;">Dužina</div>
                    <div style="font-size: 22px; font-weight: bold; color: #003366;">${trail.distance}</div>
                </div>
            </div>
            
            <!-- Opis -->
            <div style="padding: 24px; background: #ffffff; border-radius: 12px; border: 2px solid #e5e7eb; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="font-size: 20px; font-weight: bold; color: #003366; margin-bottom: 12px; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">📝</span> Opis staze
                </h4>
                <p style="color: #374151; line-height: 1.7; font-size: 15px;">${trail.description}</p>
            </div>
            
            <!-- Karakteristike -->
            <div style="padding: 24px; background: #ffffff; border-radius: 12px; border: 2px solid #e5e7eb; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="font-size: 20px; font-weight: bold; color: #003366; margin-bottom: 16px; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">⭐</span> Karakteristike
                </h4>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    ${trail.features.map(f => `
                        <li style="margin-bottom: 12px; display: flex; align-items: start;">
                            <span style="color: #10b981; margin-right: 12px; font-size: 18px; font-weight: bold;">✓</span>
                            <span style="color: #374151; font-size: 15px; line-height: 1.5;">${f}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <!-- Oprema -->
            <div style="padding: 24px; background: #ffffff; border-radius: 12px; border: 2px solid #e5e7eb; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="font-size: 20px; font-weight: bold; color: #003366; margin-bottom: 16px; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">🎒</span> Potrebna oprema
                </h4>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    ${trail.equipment.map(e => `
                        <li style="margin-bottom: 12px; display: flex; align-items: start;">
                            <span style="margin-right: 12px; font-size: 18px;">🎒</span>
                            <span style="color: #374151; font-size: 15px; line-height: 1.5;">${e}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <!-- Upozorenje -->
            <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-left: 5px solid #f59e0b; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: start;">
                    <span style="font-size: 28px; margin-right: 16px;">⚠️</span>
                    <div style="flex: 1;">
                        <h5 style="font-weight: bold; color: #92400e; margin-bottom: 8px; font-size: 16px;">Važno upozorenje</h5>
                        <p style="color: #b45309; font-size: 14px; margin: 0; line-height: 1.6;">${trail.warning}</p>
                    </div>
                </div>
            </div>
            
            <!-- Kontakt -->
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="color: #1e40af; font-size: 15px; margin: 0; font-weight: 500;">
                    📞 Za više informacija: <strong style="color: #003366; font-size: 16px;">${trail.contact}</strong>
                </p>
            </div>
        </div>
    `;
    
    // Prikaži modal
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.body.style.overflow = 'hidden';
    
    console.log('✅ Trail modal opened');
}

// Zatvori modal
function closeTrailModal() {
    const modal = document.getElementById('trailModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = 'auto';
        console.log('✅ Trail modal closed');
    }
}

// Inicijalizacija
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Initializing trail modal system...');

    // Use event delegation since buttons are added dynamically
    document.addEventListener('click', function(e) {
        if (e.target.closest('.view-trail-btn')) {
            e.preventDefault();
            e.stopPropagation();
            const btn = e.target.closest('.view-trail-btn');
            const trailId = btn.getAttribute('data-trail-id');
            console.log(`🖱️ Trail button clicked: ${trailId}`);
            openTrailModal(trailId);
        }
    });

    console.log('✅ Trail button event delegation configured');

    // Close dugme
    const closeBtn = document.getElementById('closeTrailModal');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeTrailModal);
        console.log('✅ Close button configured');
    }
    
    // Klik van modala
    const modal = document.getElementById('trailModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeTrailModal();
            }
        });
    }
    
    // ESC taster
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('trailModal');
            if (modal && !modal.classList.contains('hidden')) {
                closeTrailModal();
            }
        }
    });
    
    // Test funkcija (za debug u console-u)
    window.testTrailModal = openTrailModal;
    console.log('✅ Trail modal system ready! Test: testTrailModal(1)');
});
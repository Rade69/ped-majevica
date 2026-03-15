// Membership Form Handler - FINO PODEŠENE KOORDINATE!

async function generatePristupnica(event) {
    event.preventDefault();

    if (typeof PDFLib === 'undefined') {
        alert('PDF biblioteka nije učitana. Molimo osvježite stranicu i pokušajte ponovo.');
        return;
    }

    if (typeof fontkit === 'undefined') {
        alert('Fontkit biblioteka nije učitana. Molimo osvježite stranicu i pokušajte ponovo.');
        return;
    }

    const formData = {
        imePrezime: document.getElementById('imePrezime').value,
        datumRodjenja: document.getElementById('datumRodjenja').value,
        mjestoRodjenja: document.getElementById('mjestoRodjenja').value,
        mjestoBoravka: document.getElementById('mjestoBoravka').value,
        adresa: document.getElementById('adresa').value,
        telefon: document.getElementById('telefon').value,
        email: document.getElementById('email').value,
        zanimanje: document.getElementById('zanimanje').value,
        datumUclanjenja: document.getElementById('datumUclanjenja').value
    };

    if (!formData.imePrezime || !formData.datumRodjenja || !formData.adresa) {
        alert('Molimo popunite sva obavezna polja!');
        return;
    }

    try {
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Генеришем PDF...';
        submitBtn.disabled = true;

        await fillTemplate(formData);

        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        showSuccessMessage();

    } catch (error) {
        console.error('Greška:', error);
        alert('Došlo je do greške: ' + error.message);

        const submitBtn = event.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-file-pdf"></i><span>Генериши Приступницу (PDF)</span><i class="fas fa-arrow-right"></i>';
            submitBtn.disabled = false;
        }
    }
}

async function fillTemplate(data) {
    const { PDFDocument, rgb } = PDFLib;

    try {
        console.log('📄 Učitavam template...');

        const templateUrl = '/assets/pdf/pristupnica_template.pdf';
        const existingPdfBytes = await fetch(templateUrl).then(res => {
            if (!res.ok) throw new Error('Template nije pronađen!');
            return res.arrayBuffer();
        });

        console.log('✅ Template učitan!');

        const pdfDoc = await PDFDocument.load(existingPdfBytes);
        pdfDoc.registerFontkit(fontkit);

        const pages = pdfDoc.getPages();
        const firstPage = pages[0];

        console.log('📝 Učitavam font...');

        const fontUrl = 'https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Me5WZLCzYlKw.ttf';
        const fontBytes = await fetch(fontUrl).then(res => res.arrayBuffer());
        const font = await pdfDoc.embedFont(fontBytes);

        console.log('✅ Font učitan!');

        const black = rgb(0, 0, 0);
        const fontSize = 10.5;

        // FINO PODEŠENE KOORDINATE!
        const yPositions = {
            line1: 499,  // Ime - bez promene
            line2: 477,  // Mjesto rođenja - bez promene
            line3: 449,  // Mjesto boravka - bez promene
            line4: 422,  // Adresa: bilo 419, +3px GORE
            line5: 396,  // Telefon: bilo 411, -12px DOLE
            line6: 370,  // Email: bilo 403, -25px DOLE
            line7: 345,  // Zanimanje: bilo 367, -25px DOLE
            line8: 320   // Datum: bilo 359, -50px DOLE
        };

        const xStart = 325;

        console.log('📝 Popunjavam polja...');

        const addText = (text, yPos) => {
            firstPage.drawText(text, {
                x: xStart,
                y: yPos,
                size: fontSize,
                font: font,
                color: black
            });
        };

        // Popuni sva polja
        addText(data.imePrezime, yPositions.line1);
        addText(`${data.mjestoRodjenja}, ${data.datumRodjenja}`, yPositions.line2);
        addText(data.mjestoBoravka, yPositions.line3);
        addText(data.adresa, yPositions.line4);
        addText(data.telefon, yPositions.line5);
        addText(data.email, yPositions.line6);
        addText(data.zanimanje, yPositions.line7);
        addText(data.datumUclanjenja, yPositions.line8);

        console.log('💾 Čuvam PDF...');

        const pdfBytes = await pdfDoc.save();

        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${data.imePrezime.replace(/\s+/g, '_')}_pristupnica.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        console.log('✅ Pristupnica gotova!');

    } catch (error) {
        console.error('❌ Greška:', error);
        throw error;
    }
}

function showSuccessMessage() {
    const messageDiv = document.getElementById('successMessage');
    if (messageDiv) {
        messageDiv.classList.remove('hidden');
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => messageDiv.classList.add('hidden'), 5000);
    }
}

function downloadUplatnica(type) {
    const imagePath = type === 'basic' ? '/assets/images/uplatnica-35km.jpg' : '/assets/images/uplatnica-40km.jpg';
    const link = document.createElement('a');
    link.href = imagePath;
    link.download = `uplatnica-${type}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

document.addEventListener('DOMContentLoaded', function () {
    const datumUclanjenjaInput = document.getElementById('datumUclanjenja');
    if (datumUclanjenjaInput) {
        const today = new Date();
        datumUclanjenjaInput.value = today.toISOString().split('T')[0];
    }
});
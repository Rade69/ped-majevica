#!/bin/bash
# ========================================
# Skripta za brisanje starih fajlova
# Koristi SAMO nakon što si testirao novu strukturu!
# ========================================

echo "⚠️  UPOZORENJE: Ova skripta će obrisati stare fajlove!"
echo ""
echo "Stari fajlovi koji će biti obrisani:"
echo "  - app.py"
echo "  - config.py"
echo "  - extensions.py"
echo "  - models/"
echo "  - routes/"
echo "  - services/"
echo "  - middleware/"
echo ""
read -p "Da li želiš da nastaviš? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Otkazano."
    exit 0
fi

echo ""
echo "📁 Brisanje starih fajlova..."

# Brisanje starih root fajlova
rm -f app.py
rm -f config.py
rm -f extensions.py
rm -f ped.db

# Brisanje starih foldera
rm -rf models/
rm -rf routes/
rm -rf services/
rm -rf middleware/

echo ""
echo "✅ Stari fajlovi su obrisani!"
echo ""
echo "Nova struktura:"
tree -I 'venv|__pycache__|*.pyc|migrations|instance' -L 2

echo ""
echo "✅ Gotovo!"

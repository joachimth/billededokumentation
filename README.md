# 📸 Billede Dokumentation

Et professionelt Python-værktøj til at generere fotodokumentationsrapporter i PDF-format med editerbare kommentarfelter.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 To versioner tilgængelige

Dette projekt tilbyder to måder at generere fotodokumentation på:

### 🖥️ **Kommandolinje version** (`app.py`)
- Hurtig og simpel
- Læser billeder fra en mappe
- Genererer PDF automatisk
- Ideel til batch processing og automation

### 🌐 **Web version** (`app_web.py`) ⭐ **NYT!**
- Moderne webinterface
- Drag-and-drop upload
- Omorganisér billeder visuelt
- Tilføj beskrivelser interaktivt
- Ideel til brugervenlig workflow

➡️ **[Se komplet dokumentation for web-versionen](WEB_VERSION.md)**

## 📋 Indholdsfortegnelse

- [Funktioner](#-funktioner)
- [Installation](#-installation)
- [Brug](#-brug)
- [Projektstruktur](#-projektstruktur)
- [Konfiguration](#-konfiguration)
- [Eksempler](#-eksempler)
- [Krav](#-krav)
- [Fejlfinding](#-fejlfinding)
- [Bidrag](#-bidrag)
- [Licens](#-licens)
- [Forfatter](#-forfatter)

## ✨ Funktioner

- 📄 **Professionel PDF-generering**: Automatisk oprettelse af fotodokumentationsrapporter
- 🖼️ **Forsidebillede**: Smuk forside med logo og rapportinformation
- 📐 **Grid-layout**: Organiseret 2x2 billedgrid på hver side
- 🏷️ **Editerbare felter**: Interaktive kommentarfelter under hvert billede
- 🎨 **Automatisk skalering**: Bevarer billedernes aspektforhold
- 📊 **Header og footer**: Professionelt layout med logo og sidetal
- 🔧 **Billedkomprimering**: Optimeret JPEG-komprimering for mindre filstørrelse
- 📅 **Dato-stempel**: Automatisk datering af rapporten

## 🚀 Installation

### Forudsætninger

- Python 3.7 eller nyere
- pip (Python package manager)

### Trin-for-trin installation

1. **Klon repositoriet**
   ```bash
   git clone https://github.com/joachimth/billededokumentation.git
   cd billededokumentation
   ```

2. **Opret et virtuelt miljø (anbefalet)**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Installer dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Brug

### Grundlæggende brug

1. **Placér dine billeder**
   - Læg dine billeder i `billeder/` mappen
   - Understøttede formater: JPG, JPEG, PNG, BMP, GIF

2. **Tilføj dit logo**
   - Placér dit logo som `logo.png` i rodmappen
   - Anbefalede dimensioner: 314x98 pixels

3. **Kør scriptet**
   ```bash
   python app.py
   ```

4. **Find din PDF**
   - Den genererede PDF gemmes som `photo_documentation.pdf`

### Kommandolinje eksempel

```bash
# Aktivér virtuelt miljø
source venv/bin/activate  # macOS/Linux
# eller
venv\Scripts\activate  # Windows

# Kør scriptet
python app.py

# Output:
# PDF-filen er genereret og gemt som: photo_documentation.pdf
```

## 📁 Projektstruktur

```
billededokumentation/
│
├── app.py                    # Hovedscript til PDF-generering
├── requirements.txt          # Python dependencies
├── logo.png                  # Virksomhedslogo (314x98 pixels)
├── README.md                 # Denne fil
├── LICENSE                   # MIT Licens
├── .gitignore               # Git ignore fil
│
├── billeder/                # Mappe til input-billeder
│   ├── IMG_8223.jpeg
│   └── IMG_8224.jpeg
│
└── photo_documentation.pdf  # Output PDF (genereret)
```

## ⚙️ Konfiguration

Du kan tilpasse PDF'ens udseende ved at ændre konstanterne i `app.py`:

```python
# Layout-konstanter
IMAGE_MAX_WIDTH = 260        # Maks. billedbredde (pixels)
IMAGE_MAX_HEIGHT = 260       # Maks. billedhøjde (pixels)
MARGIN_X = 30                # Horisontal margen
MARGIN_Y = 60                # Vertikal margen
COLUMNS = 2                  # Antal kolonner per side
ROWS = 2                     # Antal rækker per side

# Logo-konstanter
LOGO_PATH = "logo.png"       # Sti til logo
HEADER_LOGO_WIDTH = 100      # Logo-bredde i header
HEADER_LOGO_HEIGHT = 30      # Logo-højde i header

# Kvalitet
JPEG_QUALITY = 85            # JPEG komprimering (0-100)
```

### Tilpas forfatter og titel

I `app.py` linje 46 og 56:

```python
c.setAuthor("Joachim Thirsbro")  # Skift til dit navn
c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 210, "Joachim Thirsbro")
```

## 📸 Eksempler

### Input

Placér dine billeder i `billeder/` mappen:

```
billeder/
├── projekt_foto_1.jpg
├── projekt_foto_2.jpg
├── projekt_foto_3.jpg
└── projekt_foto_4.jpg
```

### Output

PDF'en vil indeholde:

1. **Forside** med:
   - Stort logo (centreret)
   - Titel: "Fotodokumentation"
   - Genereringsdato
   - Forfatter

2. **Billedsider** med:
   - 4 billeder per side (2x2 grid)
   - Header med logo og titel
   - Editerbare kommentarfelter under hvert billede
   - Footer med sidetal

## 📦 Krav

Projektet kræver følgende Python-pakker:

```
Pillow          # Billedbehandling
geopy==2.2.0    # Geolokation (hvis behov)
piexif==1.1.3   # EXIF metadata håndtering
pikepdf         # PDF manipulation
fpdf2           # PDF generering (alternativ)
reportlab       # PDF generering (primær)
```

Installer alle med:
```bash
pip install -r requirements.txt
```

## 🔧 Fejlfinding

### Problem: "Ingen billeder fundet i mappen"

**Løsning:**
- Kontrollér at `billeder/` mappen eksisterer
- Sørg for at der er billedfiler i mappen
- Tjek at billederne har understøttede formater (.jpg, .jpeg, .png, .bmp, .gif)

### Problem: Logo vises ikke

**Løsning:**
- Kontrollér at `logo.png` findes i rodmappen
- Tjek at filen er læsbar og i PNG-format
- Prøv med et andet billede

### Problem: PDF genereres ikke

**Løsning:**
- Kontrollér at alle dependencies er installeret: `pip install -r requirements.txt`
- Tjek at du har skrivetilladelser i mappen
- Se fejlmeddelelser i konsollen

### Problem: Billeder ser forvrængede ud

**Løsning:**
- Scriptet bevarer automatisk aspektforholdet
- Hvis billeder stadig ser forkerte ud, tjek at `IMAGE_MAX_WIDTH` og `IMAGE_MAX_HEIGHT` er fornuftige værdier

## 🤝 Bidrag

Bidrag er velkomne! Følg disse trin:

1. Fork repositoriet
2. Opret en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dine ændringer (`git commit -m 'Add some AmazingFeature'`)
4. Push til branchen (`git push origin feature/AmazingFeature`)
5. Åbn en Pull Request

### Udviklings-guidelines

- Følg PEP 8 style guide
- Tilføj kommentarer til kompleks kode
- Test dine ændringer før commit
- Opdater dokumentationen hvis relevant

## 📄 Licens

Dette projekt er licenseret under MIT License - se [LICENSE](LICENSE) filen for detaljer.

## 👤 Forfatter

**Joachim Thirsbro**

- GitHub: [@joachimth](https://github.com/joachimth)

## 🙏 Anerkendelser

- [ReportLab](https://www.reportlab.com/) for PDF-generering
- [Pillow](https://python-pillow.org/) for billedbehandling

## 📈 Fremtidige funktioner

- [ ] Automatisk geo-tagging af billeder
- [ ] Tilpasbar farvetema
- [ ] Eksport til flere formater
- [ ] GUI interface
- [ ] Batch processing af flere mapper
- [ ] Template system til forskellige layouts

## 💡 Tips og tricks

### Optimér billedstørrelse før generering

For hurtigere PDF-generering og mindre filstørrelse:

```bash
# Brug ImageMagick til batch resize
mogrify -resize 1920x1920 -quality 85 billeder/*.jpg
```

### Automatisér med cron job (Linux/macOS)

```bash
# Kør hver dag kl. 18:00
0 18 * * * cd /sti/til/billededokumentation && /sti/til/venv/bin/python app.py
```

### Batch processing

Modificer `app.py` til at håndtere flere mapper:

```python
folders = ["projekt1/billeder", "projekt2/billeder", "projekt3/billeder"]
for folder in folders:
    create_pdf_with_grid_layout(folder, output_pdf=f"{folder}_documentation.pdf")
```

---

**Lavet med ❤️ af Joachim Thirsbro**

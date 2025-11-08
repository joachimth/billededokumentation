# 🚀 Installation & Setup Guide

## Hurtig Start

### 1. Klone projektet
```bash
git clone <repository-url>
cd billededokumentation
```

### 2. Opret virtuelt miljø
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Installer dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurer projektet
- **Tilføj dit logo**: Placer dit logo som `logo.png` i rodmappen
- **Billedmappe**: Opret `billeder/` mappe med dine billeder (valgfrit for web version)

### 5. Kør appen
```bash
# Kommandolinje version
python app.py

# Web version (anbefalet)
python app_web.py
```

## 📁 Projekts struktur efter setup

```
billededokumentation/
├── app.py                    # Kommandolinje version
├── app_web.py                # Web version (optimeret)
├── requirements.txt          # Dependencies
├── logo.png                  # Dit logo (314x98px anbefalet)
├── README.md                 # Dokumentation
│
├── templates/                # Web templates ⭐ NYT
│   └── index.html            # Hoved web interface
│
├── static/                   # Statiske web filer ⭐ NYT
│   ├── css/
│   │   └── style.css         # Moderne responsive styling
│   ├── js/
│   │   └── main.js           # Interaktive funktioner
│   └── uploads/              # Uploadede billeder
│       └── .gitkeep
│
├── billeder/                 # Original billedmappe
└── uploads/                  # Web uploads (automatisk oprettet)
```

## 🎯 Hvad er forbedret i den optimerede version?

### 🔐 Sikkerhed
- Forbedret filvalidering med MIME type kontrol
- Session-baseret filisolering
- Sikre filnavne med hash
- Autoriseret adgang til filer

### ⚡ Performance
- Baggrundsoprydning af gamle filer
- Asynkron filhåndtering
- Forbedret memory management
- Multi-threaded request handling

### 🎨 Brugeroplevelse
- Moderne responsivt design
- Drag-and-drop med progress indicators
- Toast notifications
- Modal billedvisning
- Keyboard shortcuts

### 🛠️ Udvikling
- Forbedret error handling og logging
- Struktureret kode med dokumentation
- API endpoints for debugging
- Konfigurerbar opsætning

## 🌐 Brug af Web Version

1. **Start server**: `python app_web.py`
2. **Åbn browser**: http://localhost:5000
3. **Upload billeder**: Træk og slip eller klik
4. **Omorganisér**: Træk billeder for at ændre rækkefølge
5. **Tilføj beskrivelser**: Klik i tekstfelter
6. **Generer PDF**: Klik "Generer PDF" knappen
7. **Download**: PDF downloades automatisk

## 📱 Responsivt Design

Web versionen fungerer på:
- 💻 Desktop (1200px+)
- 📱 Tablet (768px-1199px)
- 📱 Mobil (under 768px)

## 🔧 Konfiguration

### Ændre port
I `app_web.py` linje 331:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Skift port her
```

### Ændre upload størrelse
I `app_web.py` linje 20:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Ændre PDF layout
I `app_web.py` linje 31-39:
```python
IMAGE_MAX_WIDTH = 260
IMAGE_MAX_HEIGHT = 260
COLUMNS = 2
ROWS = 2
```

## 🚨 Fejlfinding

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Appen starter ikke
```bash
# Tjek om port 5000 er i brug
lsof -i :5000

# Dræb process hvis nødvendigt
kill -9 PID
```

### Billeder uploades ikke
- Tjek konsollen for fejl
- Verificér filstørrelse < 16MB
- Kontrollér upload folder eksisterer

### PDF genereres ikke
- Tjek `logo.png` eksisterer
- Verificér ReportLab er installeret
- Se server logs i `webapp.log`

## 📊 Logging

Web versionen logger til:
- **Console**: Realtime output
- **Fil**: `webapp.log` (server aktiviteter)

## 🧹 Automatisk oprydning

Systemet rydder automatisk op:
- Filer ældre end 7 dage
- Baggrundsoprydning hver time
- Session cleanup

## 🔄 Opdatering

For at opdatere til ny version:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 💡 Tips & Tricks

### Batch upload
Upload mange billeder ved at vælge alle (Ctrl+A) i filbrowseren

### Keyboard shortcuts
- **ESC**: Luk billedvisning
- **Ctrl+Enter**: Generer PDF
- **Delete**: Fjern valgt billede

### Performance
For hurtigere upload: komprimér billeder først
```bash
# Brug ImageMagick
mogrify -resize 1920x1920 -quality 85 billeder/*.jpg
```

## 📞 Support

Har du problemer?
1. Check denne guide
2. Se konsol output
3. Tjek `webapp.log` filen
4. Opret issue på GitHub

---

**Nyd din optimerede fotodokumentation generator! 🎉**
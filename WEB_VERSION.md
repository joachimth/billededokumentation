# 🌐 Web Version - Fotodokumentation Generator

En moderne, brugervenlig webapplikation til at oprette professionelle fotodokumentationsrapporter.

## 🎯 Oversigt

Web-versionen giver en intuitiv drag-and-drop interface til at:
- ✨ Uploade billeder via træk-og-slip eller fil-browser
- 🔄 Omorganisere billeder ved at trække dem rundt
- ✍️ Tilføje beskrivelser til hvert billede
- 📄 Generere professionelle PDF'er med editerbare felter
- 🖼️ Forhåndsvise billeder i fuld størrelse

## 🚀 Kom i gang

### 1. Installation

Installer alle dependencies (inklusive Flask):

```bash
pip install -r requirements.txt
```

### 2. Start webserveren

```bash
python app_web.py
```

Du vil se en velkomstbesked med instruktioner:

```
============================================================
🌐 Fotodokumentation Web App
============================================================

📋 Sådan bruger du appen:
  1. Åbn din browser på http://localhost:5000
  2. Upload dine billeder (træk og slip eller klik)
  3. Omorganisér billeder ved at trække dem
  4. Tilføj beskrivelser til hvert billede
  5. Klik 'Generer PDF' for at oprette din rapport

✨ PDF'en vil være redigérbar med felter til kommentarer!
============================================================
```

### 3. Åbn browseren

Gå til: **http://localhost:5000**

## 💻 Brug af webappen

### Upload billeder

Der er tre måder at uploade billeder:

1. **Træk og slip**: Træk billeder direkte fra din computer til upload-zonen
2. **Klik for at vælge**: Klik på "Vælg filer" knappen
3. **Batch upload**: Vælg flere billeder på én gang

### Organisér billeder

- **Drag-and-drop**: Træk billeder for at ændre deres rækkefølge
- **Slet enkeltbilleder**: Klik på skraldespands-ikonet
- **Ryd alle**: Klik på "Ryd alle" for at starte forfra

### Tilføj beskrivelser

- Klik i tekstfeltet under hvert billede
- Skriv en beskrivelse (valgfrit)
- Beskrivelsen vil blive pre-fyldt i PDF'ens redigérbare felt

### Generer PDF

1. Når du er klar, klik på **"Generer PDF"**
2. PDF'en genereres på serveren
3. Filen downloades automatisk til din computer

## 📁 Projektstruktur

```
billededokumentation/
│
├── app.py                      # Original kommandolinje version
├── app_web.py                  # Flask webapplikation ⭐ NYT
├── requirements.txt            # Dependencies (opdateret med Flask)
├── logo.png                    # Logo til PDF'er
│
├── templates/                  # HTML templates ⭐ NYT
│   └── index.html              # Hoved webinterface
│
├── static/                     # Statiske filer ⭐ NYT
│   ├── style.css               # Styling
│   └── script.js               # JavaScript funktionalitet
│
├── uploads/                    # Midlertidige uploads ⭐ NYT
│   ├── session_xxx_image1.jpg
│   └── documentation_xxx.pdf
│
└── billeder/                   # Original billeder mappe
```

## ⚙️ Teknisk information

### Framework og biblioteker

- **Flask 3.0.0**: Python web framework
- **ReportLab**: PDF generering
- **Pillow**: Billedbehandling
- **JavaScript (Vanilla)**: Drag-and-drop funktionalitet
- **CSS3**: Moderne styling med gradients og animationer

### Features

#### 🔐 Session-baseret filhåndtering
- Hver bruger får et unikt session ID
- Billeder isoleres per session
- Automatisk cleanup mulig

#### 📤 Upload håndtering
- Max filstørrelse: 16MB per fil
- Understøttede formater: JPG, JPEG, PNG, GIF, BMP
- Sikker filnavns-håndtering med `secure_filename()`

#### 🎨 Moderne UI/UX
- Responsivt design (virker på mobil og desktop)
- Drag-and-drop interface
- Progress bars ved upload
- Toast notifications for feedback
- Modal billedvisning
- Smooth animationer

#### 📄 PDF generation
- Identisk layout som original version
- Forside med logo og metadata
- 2x2 grid layout
- Editerbare tekstfelter med pre-fyldt beskrivelse
- Header og footer på hver side

## 🔧 Konfiguration

### Ændre port

I `app_web.py` linje 233:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Skift port her
```

### Ændre upload størrelse

I `app_web.py` linje 17:

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Ændre PDF layout

Samme konstanter som i `app.py`:

```python
IMAGE_MAX_WIDTH = 260
IMAGE_MAX_HEIGHT = 260
COLUMNS = 2
ROWS = 2
```

## 🌐 Deployment

### Lokal netværk

For at tilgå appen fra andre enheder på dit netværk:

1. Start appen (den lytter allerede på `0.0.0.0`)
2. Find din IP-adresse:
   ```bash
   # Linux/macOS
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```
3. Andre på netværket kan tilgå: `http://DIN-IP:5000`

### Production deployment

⚠️ **Vigtigt**: Den nuværende konfiguration er til udvikling. Til production:

#### Med Gunicorn (anbefalet)

```bash
# Installer Gunicorn
pip install gunicorn

# Start med Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_web:app
```

#### Med Docker

Opret `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app_web:app"]
```

Build og kør:

```bash
docker build -t fotodokumentation .
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads fotodokumentation
```

#### Sikkerhedsovervejelser for production

1. **Skift secret key**: Brug en sikker, tilfældig key
   ```python
   app.secret_key = os.environ.get('SECRET_KEY', 'din-sikre-key')
   ```

2. **Disable debug mode**:
   ```python
   app.run(debug=False)
   ```

3. **Tilføj rate limiting**:
   ```bash
   pip install Flask-Limiter
   ```

4. **Upload validation**: Tjek filindhold, ikke kun extension

5. **HTTPS**: Brug SSL/TLS certifikat

6. **Session cleanup**: Implementer automatisk sletning af gamle filer

## 🆚 Web version vs. Kommandolinje version

| Feature | app.py (CLI) | app_web.py (Web) |
|---------|--------------|------------------|
| Interface | Kommandolinje | Browser |
| Billedvalg | Fra mappe | Upload interface |
| Rækkefølge | Filnavn | Drag-and-drop |
| Beskrivelser | Kun editerbart felt | Pre-filled + editerbart |
| Platform | Lokal maskine | Multi-bruger muligt |
| Setup | Ingen server | Flask server |

## 💡 Tips og tricks

### Batch processing

Upload mange billeder på én gang ved at:
1. Vælge alle billeder i fil-browseren (Ctrl+A / Cmd+A)
2. Trække hele mapper til upload-zonen

### Keyboard shortcuts

- **ESC**: Luk billedforhåndsvisning
- **Tab**: Naviger mellem beskrivelsesfelter

### Performance

For hurtigere upload af mange billeder:
- Reducer billedstørrelse før upload
- Brug JPEG i stedet for PNG
- Komprimer billeder med ImageMagick:
  ```bash
  mogrify -resize 1920x1920 -quality 85 *.jpg
  ```

### Cleanup gamle uploads

For at rydde op i uploads mappen:

```bash
# Slet alle filer ældre end 7 dage
find uploads/ -type f -mtime +7 -delete
```

Eller tilføj automatisk cleanup i `app_web.py`:

```python
import time

def cleanup_old_files():
    now = time.time()
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filepath):
            if os.stat(filepath).st_mtime < now - 7 * 86400:  # 7 dage
                os.remove(filepath)
```

## 🐛 Fejlfinding

### Appen starter ikke

**Problem**: `ModuleNotFoundError: No module named 'flask'`

**Løsning**:
```bash
pip install -r requirements.txt
```

### Billeder uploades ikke

**Problem**: Ingen respons ved upload

**Løsning**:
1. Tjek konsollen for fejl
2. Kontrollér at `uploads/` mappen eksisterer
3. Verificér filstørrelse er under 16MB

### PDF genereres ikke

**Problem**: "Kunne ikke generere PDF"

**Løsning**:
1. Tjek at `logo.png` findes
2. Verificér ReportLab er installeret
3. Se server logs for fejlmeddelelser

### Port allerede i brug

**Problem**: `Address already in use`

**Løsning**:
```bash
# Find proces på port 5000
lsof -i :5000

# Dræb processen
kill -9 PID
```

Eller skift til anden port i `app_web.py`

## 🔮 Fremtidige forbedringer

- [ ] Bruger-autentifikation
- [ ] Gem projekter til senere redigering
- [ ] Export til flere formater (Word, PowerPoint)
- [ ] Billedredigering (crop, rotate, filters)
- [ ] Template system med flere layouts
- [ ] API endpoints til integration
- [ ] Real-time samarbejde (multiple users)
- [ ] Cloud storage integration (Dropbox, Google Drive)
- [ ] Automatisk backup af projekter

## 📞 Support

Har du problemer eller forslag?

1. Check denne dokumentation
2. Se hovedfilen [README.md](README.md)
3. Opret et issue på GitHub

## 🙌 Sammenligning af workflow

### Original (app.py):
```
1. Læg billeder i billeder/ mappe
2. Kør python app.py
3. PDF genereres automatisk
```

### Web version (app_web.py):
```
1. Start serveren: python app_web.py
2. Åbn browser: http://localhost:5000
3. Upload billeder via drag-and-drop
4. Omorganisér og tilføj beskrivelser
5. Klik "Generer PDF"
6. Download færdig PDF
```

---

**Web version udviklet med ❤️ - Nem, moderne og brugervenlig!**

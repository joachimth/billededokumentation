from flask import Flask, render_template, request, send_file, jsonify, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
import tempfile
from PIL import Image
from datetime import datetime
import secrets
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Konstanter
PAGE_WIDTH, PAGE_HEIGHT = A4
IMAGE_MAX_WIDTH = 260
IMAGE_MAX_HEIGHT = 260
MARGIN_X = 30
MARGIN_Y = 60
COLUMNS = 2
ROWS = 2
LOGO_PATH = "logo.png"
HEADER_LOGO_WIDTH = 100
HEADER_LOGO_HEIGHT = 30
JPEG_QUALITY = 85

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_header(c):
    """Tilføj header med logo"""
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 20,
                   width=HEADER_LOGO_WIDTH, height=HEADER_LOGO_HEIGHT, mask='auto')
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN_X + HEADER_LOGO_WIDTH + 10, PAGE_HEIGHT - MARGIN_Y + 30, "Fotodokumentation")

def add_footer(c):
    """Tilføj footer med sidetal"""
    c.setFont("Helvetica", 10)
    page_number_text = f"Side {c.getPageNumber()}"
    c.drawRightString(PAGE_WIDTH - MARGIN_X, 15, page_number_text)

def create_pdf_from_uploaded_images(images_data, output_pdf="photo_documentation.pdf"):
    """
    Generer PDF fra uploaded billeder og tekst
    images_data: Liste af dicts med 'path' og 'description'
    """
    if not images_data:
        return None

    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.setTitle("Fotodokumentation")
    c.setAuthor("Joachim Thirsbro")
    c._pageNumber = 1

    # Forside
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, PAGE_WIDTH / 2 - 314 / 2, PAGE_HEIGHT / 2,
                   width=314, height=98, mask='auto')
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 150, "Fotodokumentation")
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 180,
                       f"Rapport genereret {datetime.now().strftime('%b %Y')}")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 210, "Joachim Thirsbro")

    c.showPage()
    add_header(c)

    # Beregn layout
    gap_x = (PAGE_WIDTH - 2 * MARGIN_X - COLUMNS * IMAGE_MAX_WIDTH) / (COLUMNS - 1) if COLUMNS > 1 else 0
    gap_y = (PAGE_HEIGHT - 2 * MARGIN_Y - ROWS * (IMAGE_MAX_HEIGHT + 30)) / (ROWS - 1) if ROWS > 1 else 0

    image_counter = 0
    for i, image_info in enumerate(images_data):
        image_path = image_info['path']
        description = image_info.get('description', '')

        # Beregn position
        row = image_counter // COLUMNS % ROWS
        col = image_counter % COLUMNS

        # Ny side når nødvendigt
        if image_counter != 0 and image_counter % (COLUMNS * ROWS) == 0:
            add_footer(c)
            c.showPage()
            add_header(c)
            row = 0

        x = MARGIN_X + col * (IMAGE_MAX_WIDTH + gap_x)
        y = PAGE_HEIGHT - MARGIN_Y - row * (IMAGE_MAX_HEIGHT + 0 + gap_y) - IMAGE_MAX_HEIGHT

        try:
            # Indsæt billede
            with Image.open(image_path) as img:
                img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT))
                img_width, img_height = img.size

                x_adjusted = x + (IMAGE_MAX_WIDTH - img_width) / 2
                y_adjusted = y + (IMAGE_MAX_HEIGHT - img_height) / 2

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                    temp_image_path = tmp_file.name
                    img.save(temp_image_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)

            c.drawImage(temp_image_path, x_adjusted, y_adjusted, width=img_width, height=img_height)
            os.remove(temp_image_path)
        except Exception as e:
            print(f"Fejl ved behandling af billedet '{image_path}': {e}")
            continue

        # Tilføj beskrivelse hvis den findes
        comment_y_position = y - 15
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.line(x + 10, comment_y_position, x + IMAGE_MAX_WIDTH - 10, comment_y_position)

        # Tilføj editerbart tekstfelt med pre-filled tekst hvis der er nogen
        c.acroForm.textfield(
            name=f"comment_{i}",
            x=x + 10,
            y=comment_y_position - 35,
            width=IMAGE_MAX_WIDTH - 10,
            height=20,
            textColor=colors.black,
            borderColor=colors.gray,
            fillColor=colors.white,
            value=description  # Pre-fill med brugerens beskrivelse
        )

        image_counter += 1

    add_footer(c)
    c.save()
    return output_pdf

@app.route('/')
def index():
    """Hovedside med upload interface"""
    # Initialiser session hvis nødvendigt
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Håndter fil upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'Ingen fil uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Ingen fil valgt'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Tilføj session ID for at undgå konflikter
        unique_filename = f"{session['session_id']}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_name': filename
        })

    return jsonify({'error': 'Ikke tilladt filtype'}), 400

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generer PDF fra uploaded billeder"""
    try:
        data = request.json
        images = data.get('images', [])

        if not images:
            return jsonify({'error': 'Ingen billeder at generere PDF fra'}), 400

        # Forbered billeddata
        images_data = []
        for img in images:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], img['filename'])
            if os.path.exists(filepath):
                images_data.append({
                    'path': filepath,
                    'description': img.get('description', '')
                })

        if not images_data:
            return jsonify({'error': 'Ingen gyldige billeder fundet'}), 400

        # Generer PDF
        output_filename = f"documentation_{session['session_id']}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        result = create_pdf_from_uploaded_images(images_data, output_path)

        if result:
            return jsonify({
                'success': True,
                'download_url': f'/download/{output_filename}'
            })
        else:
            return jsonify({'error': 'Kunne ikke generere PDF'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download genereret PDF"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name='photo_documentation.pdf')
    return "Fil ikke fundet", 404

@app.route('/delete-image', methods=['POST'])
def delete_image():
    """Slet et uploaded billede"""
    try:
        data = request.json
        filename = data.get('filename')

        if not filename or not filename.startswith(session.get('session_id', '')):
            return jsonify({'error': 'Ugyldigt filnavn'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True})

        return jsonify({'error': 'Fil ikke fundet'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Opret uploads mappe hvis den ikke findes
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    print("\n" + "="*60)
    print("🌐 Fotodokumentation Web App")
    print("="*60)
    print("\n📋 Sådan bruger du appen:")
    print("  1. Åbn din browser på http://localhost:5000")
    print("  2. Upload dine billeder (træk og slip eller klik)")
    print("  3. Omorganisér billeder ved at trække dem")
    print("  4. Tilføj beskrivelser til hvert billede")
    print("  5. Klik 'Generer PDF' for at oprette din rapport")
    print("\n✨ PDF'en vil være redigérbar med felter til kommentarer!")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)

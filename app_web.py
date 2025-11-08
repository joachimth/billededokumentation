#!/usr/bin/env python3
"""
Optimized Web Application for Photo Documentation Generator
Enhanced version with better security, performance, and user experience
"""

from flask import Flask, render_template, request, send_file, jsonify, session
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
import tempfile
import logging
import time
import secrets
import hashlib
import mimetypes
from datetime import datetime, timedelta
from PIL import Image
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import threading
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webapp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # More secure
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# File cleanup settings
CLEANUP_INTERVAL = 3600  # 1 hour
OLD_FILE_THRESHOLD = 7 * 24 * 3600  # 7 days

# PDF Generation Constants
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

# Supported file types with MIME type validation
ALLOWED_EXTENSIONS = {
    'png': 'image/png',
    'jpg': 'image/jpeg', 
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'bmp': 'image/bmp'
}

# In-memory session storage for better performance
session_data = {}

def is_valid_image_file(file_path):
    """Enhanced file validation with MIME type checking"""
    try:
        # Check file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')
        
        if ext not in ALLOWED_EXTENSIONS:
            return False, "Unsupported file extension"
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type != ALLOWED_EXTENSIONS[ext]:
            return False, "MIME type mismatch"
        
        # Additional PIL validation
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
        
        return True, "Valid image file"
        
    except Exception as e:
        return False, f"File validation error: {str(e)}"

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_header(c):
    """Add header with logo to PDF"""
    try:
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 20,
                       width=HEADER_LOGO_WIDTH, height=HEADER_LOGO_HEIGHT, mask='auto')
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_X + HEADER_LOGO_WIDTH + 10, PAGE_HEIGHT - MARGIN_Y + 30, "Fotodokumentation")
    except Exception as e:
        logger.warning(f"Could not add header: {e}")

def add_footer(c):
    """Add footer with page number to PDF"""
    try:
        c.setFont("Helvetica", 10)
        page_number_text = f"Side {c.getPageNumber()}"
        c.drawRightString(PAGE_WIDTH - MARGIN_X, 15, page_number_text)
    except Exception as e:
        logger.warning(f"Could not add footer: {e}")

def create_pdf_from_uploaded_images(images_data, output_pdf="photo_documentation.pdf"):
    """
    Enhanced PDF generation with better error handling and performance
    """
    if not images_data:
        logger.warning("No images provided for PDF generation")
        return None

    try:
        c = canvas.Canvas(output_pdf, pagesize=A4)
        c.setTitle("Fotodokumentation")
        c.setAuthor("Joachim Thirsbro")
        c._pageNumber = 1

        # Create cover page
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

        # Calculate layout
        gap_x = (PAGE_WIDTH - 2 * MARGIN_X - COLUMNS * IMAGE_MAX_WIDTH) / (COLUMNS - 1) if COLUMNS > 1 else 0
        gap_y = (PAGE_HEIGHT - 2 * MARGIN_Y - ROWS * (IMAGE_MAX_HEIGHT + 30)) / (ROWS - 1) if ROWS > 1 else 0

        image_counter = 0
        processed_images = 0
        
        for i, image_info in enumerate(images_data):
            image_path = image_info['path']
            description = image_info.get('description', '')

            # Calculate position
            row = image_counter // COLUMNS % ROWS
            col = image_counter % COLUMNS

            # New page when needed
            if image_counter != 0 and image_counter % (COLUMNS * ROWS) == 0:
                add_footer(c)
                c.showPage()
                add_header(c)
                row = 0

            x = MARGIN_X + col * (IMAGE_MAX_WIDTH + gap_x)
            y = PAGE_HEIGHT - MARGIN_Y - row * (IMAGE_MAX_HEIGHT + 0 + gap_y) - IMAGE_MAX_HEIGHT

            try:
                # Enhanced image processing with better error handling
                is_valid, validation_msg = is_valid_image_file(image_path)
                if not is_valid:
                    logger.warning(f"Skipping invalid image {image_path}: {validation_msg}")
                    continue

                with Image.open(image_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparency
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT))
                    img_width, img_height = img.size

                    x_adjusted = x + (IMAGE_MAX_WIDTH - img_width) / 2
                    y_adjusted = y + (IMAGE_MAX_HEIGHT - img_height) / 2

                    # Optimize image processing
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                        temp_image_path = tmp_file.name
                        img.save(temp_image_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)

                c.drawImage(temp_image_path, x_adjusted, y_adjusted, width=img_width, height=img_height)
                os.remove(temp_image_path)
                processed_images += 1
                
            except Exception as e:
                logger.error(f"Error processing image {image_path}: {e}")
                continue

            # Add description if provided
            comment_y_position = y - 15
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 10)
            c.line(x + 10, comment_y_position, x + IMAGE_MAX_WIDTH - 10, comment_y_position)

            # Add editable text field
            c.acroForm.textfield(
                name=f"comment_{i}",
                x=x + 10,
                y=comment_y_position - 35,
                width=IMAGE_MAX_WIDTH - 10,
                height=20,
                textColor=colors.black,
                borderColor=colors.gray,
                fillColor=colors.white,
                value=description
            )

            image_counter += 1

        add_footer(c)
        c.save()
        
        logger.info(f"PDF generated successfully: {output_pdf} with {processed_images} images")
        return output_pdf

    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        return None

def cleanup_old_files():
    """Background cleanup of old uploaded files"""
    try:
        current_time = time.time()
        cleaned_count = 0
        
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.stat(filepath).st_mtime
                if file_age > OLD_FILE_THRESHOLD:
                    try:
                        os.remove(filepath)
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Could not remove old file {filepath}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old files")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def start_cleanup_task():
    """Start the background cleanup task"""
    def cleanup_worker():
        while True:
            time.sleep(CLEANUP_INTERVAL)
            cleanup_old_files()
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()
    logger.info("Background cleanup task started")

# Routes
@app.route('/')
def index():
    """Main page with upload interface"""
    try:
        # Initialize session with better tracking
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
            session['created_at'] = datetime.now().isoformat()
        
        # Initialize session data
        if session['session_id'] not in session_data:
            session_data[session['session_id']] = {
                'created_at': datetime.now(),
                'images': []
            }
        
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {e}")
        return "Server fejl", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Enhanced file upload with better validation"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'Ingen fil uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Ingen fil valgt'}), 400

        # Enhanced file validation
        if not allowed_file(file.filename):
            return jsonify({'error': 'Ikke tilladt filtype'}), 400

        # Additional security checks
        if not file.filename:
            return jsonify({'error': 'Ugyldigt filnavn'}), 400

        # Create secure filename
        original_filename = secure_filename(file.filename)
        if not original_filename:
            return jsonify({'error': 'Ugyldigt filnavn'}), 400

        # Create unique filename with session ID
        session_id = session.get('session_id', 'unknown')
        file_hash = hashlib.md5(file.read()).hexdigest()[:8]
        file.seek(0)  # Reset file pointer
        
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{session_id}_{file_hash}_{secrets.token_hex(4)}.{file_extension}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(filepath)

        # Validate saved file
        is_valid, validation_msg = is_valid_image_file(filepath)
        if not is_valid:
            os.remove(filepath)  # Remove invalid file
            return jsonify({'error': f'Ugyldigt billede: {validation_msg}'}), 400

        # Add to session data
        if session_id in session_data:
            session_data[session_id]['images'].append({
                'filename': unique_filename,
                'original_name': original_filename,
                'upload_time': datetime.now()
            })

        logger.info(f"File uploaded: {original_filename} -> {unique_filename}")

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_name': original_filename,
            'file_size': os.path.getsize(filepath)
        })

    except RequestEntityTooLarge:
        return jsonify({'error': 'Filen er for stor (Max 16MB)'}), 413
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': f'Upload fejl: {str(e)}'}), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """Enhanced PDF generation with better error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Ingen data modtaget'}), 400

        images = data.get('images', [])
        if not images:
            return jsonify({'error': 'Ingen billeder at generere PDF fra'}), 400

        # Prepare image data
        images_data = []
        for img in images:
            filename = img.get('filename')
            if not filename:
                continue
                
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                images_data.append({
                    'path': filepath,
                    'description': img.get('description', '')
                })
            else:
                logger.warning(f"File not found: {filename}")

        if not images_data:
            return jsonify({'error': 'Ingen gyldige billeder fundet'}), 400

        # Generate unique PDF filename
        session_id = session.get('session_id', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"documentation_{session_id}_{timestamp}.pdf"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Generate PDF
        logger.info(f"Starting PDF generation for {len(images_data)} images")
        result = create_pdf_from_uploaded_images(images_data, output_path)

        if result and os.path.exists(result):
            # Clean up the generated PDF after download
            download_url = f'/download/{output_filename}'
            
            logger.info(f"PDF generated successfully: {output_filename}")
            return jsonify({
                'success': True,
                'download_url': download_url,
                'file_size': os.path.getsize(result)
            })
        else:
            logger.error("PDF generation failed")
            return jsonify({'error': 'Kunne ikke generere PDF'}), 500

    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return jsonify({'error': f'PDF generering fejl: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Enhanced file download with security checks"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Security check: only allow downloads from own session
        session_id = session.get('session_id', '')
        if not filename.startswith(session_id):
            logger.warning(f"Unauthorized download attempt: {filename} from session {session_id}")
            return "Uautoriseret adgang", 403

        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filename}")
            return "Fil ikke fundet", 404

        if not os.path.isfile(filepath):
            logger.warning(f"Invalid file path: {filename}")
            return "Ugyldig fil", 400

        # Set appropriate headers
        response = send_file(
            filepath, 
            as_attachment=True, 
            download_name='photo_documentation.pdf',
            mimetype='application/pdf'
        )
        
        # Add security headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        logger.info(f"File downloaded: {filename}")
        return response

    except Exception as e:
        logger.error(f"Download error: {e}")
        return f"Download fejl: {str(e)}", 500

@app.route('/delete-image', methods=['POST'])
def delete_image():
    """Enhanced image deletion with better security"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Ingen data modtaget'}), 400

        filename = data.get('filename')
        if not filename:
            return jsonify({'error': 'Intet filnavn angivet'}), 400

        # Security check: only allow deletion of own files
        session_id = session.get('session_id', '')
        if not filename.startswith(session_id):
            logger.warning(f"Unauthorized delete attempt: {filename} from session {session_id}")
            return jsonify({'error': 'Uautoriseret adgang'}), 403

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                
                # Remove from session data
                if session_id in session_data and 'images' in session_data[session_id]:
                    session_data[session_id]['images'] = [
                        img for img in session_data[session_id]['images'] 
                        if img['filename'] != filename
                    ]
                
                logger.info(f"File deleted: {filename}")
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {e}")
                return jsonify({'error': 'Kunne ikke slette fil'}), 500
        else:
            return jsonify({'error': 'Fil ikke fundet'}), 404

    except Exception as e:
        logger.error(f"Delete error: {e}")
        return jsonify({'error': f'Slet fejl: {str(e)}'}), 500

@app.route('/session-info')
def session_info():
    """Get session information for debugging"""
    try:
        session_id = session.get('session_id', 'unknown')
        session_images = session_data.get(session_id, {}).get('images', [])
        
        return jsonify({
            'session_id': session_id,
            'image_count': len(session_images),
            'created_at': session.get('created_at', 'unknown')
        })
    except Exception as e:
        logger.error(f"Session info error: {e}")
        return jsonify({'error': 'Session info fejl'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint ikke fundet'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Intern server fejl'}), 500

@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors"""
    return jsonify({'error': 'Filen er for stor (Max 16MB)'}), 413

def print_startup_info():
    """Print startup information"""
    print("\n" + "="*60)
    print("🌐 Fotodokumentation Web App - Optimeret Version")
    print("="*60)
    print("\n📋 Forbedringer i denne version:")
    print("  ✅ Forbedret sikkerhed med filvalidering")
    print("  ✅ Session-baseret filhåndtering")
    print("  ✅ Automatisk rengøring af gamle filer")
    print("  ✅ Forbedret fejlhåndtering og logging")
    print("  ✅ Moderne responsivt web interface")
    print("  ✅ Drag-and-drop med progress indicators")
    print("  ✅ Auto-download af PDF")
    print("\n🚀 Sådan bruger du appen:")
    print("  1. Åbn din browser på http://localhost:5000")
    print("  2. Upload dine billeder (træk og slip eller klik)")
    print("  3. Omorganisér billeder ved at trække dem")
    print("  4. Tilføj beskrivelser til hvert billede")
    print("  5. Klik 'Generer PDF' for at oprette din rapport")
    print("\n✨ PDF'en vil være redigérbar med felter til kommentarer!")
    print("🛡️  Automatisk rengøring af filer ældre end 7 dage")
    print("📊 Server logger alle aktiviteter til 'webapp.log'")
    print("="*60 + "\n")

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Start background cleanup task
    start_cleanup_task()
    
    # Register cleanup on exit
    atexit.register(cleanup_old_files)
    
    # Print startup information
    print_startup_info()
    
    # Run the app
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        threaded=True,  # Better performance for concurrent requests
        use_reloader=False  # Avoid duplicate logging
    )
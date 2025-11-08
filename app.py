#!/usr/bin/env python3
"""
Photo Documentation Generator - Command Line Version
Optimized version with better error handling and code structure
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
import tempfile
import logging
from PIL import Image
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PDF Configuration Constants
PAGE_WIDTH, PAGE_HEIGHT = A4
IMAGE_MAX_WIDTH = 260  # Maksimal bredde for hvert billede
IMAGE_MAX_HEIGHT = 260  # Maksimal højde for hvert billede
MARGIN_X = 30  # Horisontal margen
MARGIN_Y = 60  # Vertikal margen
COLUMNS = 2  # Antal kolonner
ROWS = 2  # Antal rækker
LOGO_PATH = "logo.png"  # Sti til logoet
HEADER_LOGO_WIDTH = 100  # Bredde af logo i header
HEADER_LOGO_HEIGHT = 30  # Højde af logo i header
JPEG_QUALITY = 85  # JPEG-kvalitet for komprimering (0-100)

def add_header(c):
    """Tilføj header med logo"""
    try:
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 20, 
                       width=HEADER_LOGO_WIDTH, height=HEADER_LOGO_HEIGHT, mask='auto')
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_X + HEADER_LOGO_WIDTH + 10, PAGE_HEIGHT - MARGIN_Y + 30, "Fotodokumentation")
    except Exception as e:
        logger.warning(f"Kunne ikke tilføje header: {e}")

def add_footer(c):
    """Tilføj footer med sidetal"""
    try:
        c.setFont("Helvetica", 10)
        page_number_text = f"Side {c.getPageNumber()}"
        c.drawRightString(PAGE_WIDTH - MARGIN_X, 15, page_number_text)
    except Exception as e:
        logger.warning(f"Kunne ikke tilføje footer: {e}")

def create_pdf_with_grid_layout(folder_path, output_pdf="photo_documentation.pdf"):
    """
    Generer PDF med billeder og kommentarfelter
    Forbedret version med bedre fejlhåndtering
    """
    # Find alle billedfiler
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_paths = []
    
    try:
        for f in os.listdir(folder_path):
            if f.lower().endswith(image_extensions):
                image_paths.append(os.path.join(folder_path, f))
        
        if not image_paths:
            print("❌ Ingen billeder fundet i mappen.")
            logger.warning("No images found in folder: %s", folder_path)
            return None
        
        logger.info("Found %d images for processing", len(image_paths))
        
    except FileNotFoundError:
        print(f"❌ Mappen '{folder_path}' eksisterer ikke.")
        return None
    except Exception as e:
        print(f"❌ Fejl ved læsning af mappe: {e}")
        logger.error("Error reading folder %s: %s", folder_path, e)
        return None
    
    try:
        # Opret PDF
        c = canvas.Canvas(output_pdf, pagesize=A4)
        c.setTitle("Fotodokumentation")
        c.setAuthor("Joachim Thirsbro")
        c._pageNumber = 1

        # Opret forside
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, PAGE_WIDTH / 2 - 314 / 2, PAGE_HEIGHT / 2, 
                       width=314, height=98, mask='auto')
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 150, "Fotodokumentation")
        c.setFont("Helvetica", 16)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 180, 
                           f"Rapport genereret {datetime.now().strftime('%b %Y')}")
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 210, "Joachim Thirsbro")

        # Flyt til næste side
        c.showPage()
        add_header(c)

        # Beregn layout
        gap_x = (PAGE_WIDTH - 2 * MARGIN_X - COLUMNS * IMAGE_MAX_WIDTH) / (COLUMNS - 1) if COLUMNS > 1 else 0
        gap_y = (PAGE_HEIGHT - 2 * MARGIN_Y - ROWS * (IMAGE_MAX_HEIGHT + 30)) / (ROWS - 1) if ROWS > 1 else 0

        image_counter = 0
        processed_images = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                # Beregn position
                row = image_counter // COLUMNS % ROWS
                col = image_counter % COLUMNS

                # Hvis vi når enden af en side, skift side
                if image_counter != 0 and image_counter % (COLUMNS * ROWS) == 0:
                    add_footer(c)
                    c.showPage()
                    add_header(c)
                    row = 0

                x = MARGIN_X + col * (IMAGE_MAX_WIDTH + gap_x)
                y = PAGE_HEIGHT - MARGIN_Y - row * (IMAGE_MAX_HEIGHT + 0 + gap_y) - IMAGE_MAX_HEIGHT

                # Indsæt billede
                with Image.open(image_path) as img:
                    # Konverter til RGB hvis nødvendigt
                    if img.mode in ('RGBA', 'LA', 'P'):
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
                    
                    # Gem billede midlertidigt for PDF
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                        temp_image_path = tmp_file.name
                        img.save(temp_image_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
                
                c.drawImage(temp_image_path, x_adjusted, y_adjusted, width=img_width, height=img_height)
                os.remove(temp_image_path)
                processed_images += 1
                
                # Tilføj kommentarlinje
                comment_y_position = y - 15
                c.setFillColor(colors.black)
                c.setFont("Helvetica", 10)
                c.line(x + 10, comment_y_position, x + IMAGE_MAX_WIDTH - 10, comment_y_position)
                
                # Tilføj editerbart tekstfelt
                c.acroForm.textfield(
                    name=f"comment_{i}",
                    x=x + 10,
                    y=comment_y_position - 35,
                    width=IMAGE_MAX_WIDTH - 10,
                    height=20,
                    textColor=colors.black,
                    borderColor=colors.gray,
                    fillColor=colors.white,
                )
                
                image_counter += 1
                print(f"✅ Behandlet: {os.path.basename(image_path)}")
                
            except Exception as e:
                print(f"⚠️  Fejl ved behandling af '{os.path.basename(image_path)}': {e}")
                logger.error("Error processing image %s: %s", image_path, e)
                continue

        # Tilføj footer på sidste side
        add_footer(c)
        c.save()
        
        print(f"✅ PDF genereret succesfuldt!")
        print(f"📊 Billeder behandlet: {processed_images}/{len(image_paths)}")
        logger.info("PDF generated successfully: %s with %d images", output_pdf, processed_images)
        return output_pdf
        
    except Exception as e:
        print(f"❌ Fejl ved PDF-generering: {e}")
        logger.error("Error generating PDF: %s", e)
        return None

def validate_environment():
    """Valider at miljøet er korrekt konfigureret"""
    errors = []
    
    # Tjek at logo eksisterer
    if not os.path.exists(LOGO_PATH):
        errors.append(f"Logo ikke fundet: {LOGO_PATH}")
    
    # Tjek at billedmappen eksisterer
    if not os.path.exists("billeder"):
        errors.append("Billedmappen 'billeder' eksisterer ikke")
    
    return errors

def main():
    """Hovedfunktion"""
    print("📸 Fotodokumentation Generator - Kommandolinje Version")
    print("="*50)
    
    # Valider miljø
    errors = validate_environment()
    if errors:
        print("❌ Konfigurationsfejl:")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 Løsninger:")
        print("   • Tilføj dit logo som 'logo.png' i denne mappe")
        print("   • Opret en 'billeder' mappe med dine billeder")
        print("   • Genkør scriptet")
        return
    
    # Find billeder
    folder_path = "billeder"
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    
    try:
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
        if not image_files:
            print(f"❌ Ingen billeder fundet i '{folder_path}' mappe")
            print(f"💡 Understøttede formater: {', '.join(image_extensions)}")
            return
        
        print(f"📂 Fundet {len(image_files)} billeder i '{folder_path}' mappe")
        
    except Exception as e:
        print(f"❌ Fejl ved læsning af billedmappe: {e}")
        return
    
    # Generer PDF
    print("\n🔄 Starter PDF-generering...")
    output_pdf_path = create_pdf_with_grid_layout(folder_path, output_pdf="photo_documentation.pdf")

    if output_pdf_path:
        print(f"\n🎉 SUCCESS!")
        print(f"📄 PDF-fil genereret: {output_pdf_path}")
        print(f"📍 Fuld sti: {os.path.abspath(output_pdf_path)}")
        
        # Vis filstørrelse
        try:
            file_size = os.path.getsize(output_pdf_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"💾 Filstørrelse: {file_size_mb:.2f} MB")
        except:
            pass
    else:
        print("\n❌ PDF-filen blev ikke oprettet.")
        print("🔧 Tjek konsoloutput for fejlmeddelelser")

if __name__ == "__main__":
    main()
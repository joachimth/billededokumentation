from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
import tempfile
from PIL import Image
from datetime import datetime

# Konstanter
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
JPEG_QUALITY = 85  # Justeret kvalitet for JPEG-komprimering (0-100)

# Funktion til at tilføje en header med logo
def add_header(c):
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, MARGIN_X, PAGE_HEIGHT - MARGIN_Y + 20, width=HEADER_LOGO_WIDTH, height=HEADER_LOGO_HEIGHT, mask='auto')
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN_X + HEADER_LOGO_WIDTH + 10, PAGE_HEIGHT - MARGIN_Y + 30, "Fotodokumentation")

# Funktion til at tilføje en footer med sidetal
def add_footer(c):
    c.setFont("Helvetica", 10)
    page_number_text = f"Side {c.getPageNumber()}"
    c.drawRightString(PAGE_WIDTH - MARGIN_X, 15, page_number_text)

# Funktion til at generere PDF med billeder og kommentarfelter
def create_pdf_with_grid_layout(folder_path, output_pdf="photo_documentation.pdf"):
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]
    
    if not image_paths:
        print("Ingen billeder fundet i mappen.")
        return None
    
    c = canvas.Canvas(output_pdf, pagesize=A4)
    c.setTitle("Fotodokumentation")
    c.setAuthor("Joachim Thirsbro")
    c._pageNumber = 1  # Initialisering af sidetæller

    # Opret forside med logo uden at kalde c.showPage() før det er nødvendigt
    if os.path.exists(LOGO_PATH):
        c.drawImage(LOGO_PATH, PAGE_WIDTH / 2 - 314 / 2, PAGE_HEIGHT / 2, width=314, height=98, mask='auto')
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 150, "Fotodokumentation")
    c.setFont("Helvetica", 16)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 180, f"Rapport genereret {datetime.now().strftime('%b %Y')}")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 210, "Joachim Thirsbro")

    # Tilføj footer på forsiden
    #add_footer(c)
    
    # Flyt til næste side for at begynde at indsætte billeder
    c.showPage()
    add_header(c)  # Tilføj header på den nye side

    # Beregning af plads til billeder og kommentarfelter
    gap_x = (PAGE_WIDTH - 2 * MARGIN_X - COLUMNS * IMAGE_MAX_WIDTH) / (COLUMNS - 1) if COLUMNS > 1 else 0
    gap_y = (PAGE_HEIGHT - 2 * MARGIN_Y - ROWS * (IMAGE_MAX_HEIGHT + 30)) / (ROWS - 1) if ROWS > 1 else 0

    image_counter = 0
    for i, image_path in enumerate(image_paths):
        # Beregn række- og kolonneindeks
        row = image_counter // COLUMNS % ROWS
        col = image_counter % COLUMNS

        # Hvis vi når enden af en side (dvs. ROWS * COLUMNS billeder), skift side
        if image_counter != 0 and image_counter % (COLUMNS * ROWS) == 0:
            add_footer(c)  # Tilføj footer før siden skiftes
            c.showPage()
            add_header(c)  # Tilføj header på den nye side
            row = 0  # Nulstil række for ny side

        x = MARGIN_X + col * (IMAGE_MAX_WIDTH + gap_x)
        y = PAGE_HEIGHT - MARGIN_Y - row * (IMAGE_MAX_HEIGHT + 0 + gap_y) - IMAGE_MAX_HEIGHT

        try:
            # Indsæt billedet i PDF'en med bevaret aspektforhold
            with Image.open(image_path) as img:
                img.thumbnail((IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT))  # Bevar aspektforholdet
                img_width, img_height = img.size
                
                # Beregn x- og y-justeringer for centreret placering
                x_adjusted = x + (IMAGE_MAX_WIDTH - img_width) / 2
                y_adjusted = y + (IMAGE_MAX_HEIGHT - img_height) / 2
                
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                    temp_image_path = tmp_file.name
                    img.save(temp_image_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            
            c.drawImage(temp_image_path, x_adjusted, y_adjusted, width=img_width, height=img_height)
            os.remove(temp_image_path)  # Slet den midlertidige fil efter brug
        except Exception as e:
            print(f"Fejl ved behandling af billedet '{image_path}': {e}")
            continue

        # Tilføj en skrivbar linje til kommentarer under billedet
        comment_y_position = y - 15
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.line(x + 10, comment_y_position, x + IMAGE_MAX_WIDTH - 10, comment_y_position)  # Skrivbar linje
        
        # Tilføj felt til at skrive tekst
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

    # Tilføj footer på den sidste side
    add_footer(c)
    c.save()
    return output_pdf

# Sti til undermappen "billeder"
folder_path = "billeder"

# Opret PDF'en med forside og billeder i rækker og kolonner
output_pdf_path = create_pdf_with_grid_layout(folder_path, output_pdf="photo_documentation.pdf")

if output_pdf_path:
    print(f"PDF-filen er genereret og gemt som: {output_pdf_path}")
else:
    print("PDF-filen blev ikke oprettet.")

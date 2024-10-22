import pytesseract
from PIL import Image
import io

def process_ocr(file):
    # Convert uploaded file into an image
    image = Image.open(io.BytesIO(file.read()))
    
    # Use Tesseract OCR to extract text
    ocr_text = pytesseract.image_to_string(image)

    # Return extracted text for further processing
    return ocr_text

# backend/modules/ai/ocr_engine.py

import pytesseract
from PIL import Image
import io

def ocr_image(image_bytes):
    """
    Performs OCR on an image byte stream and returns the extracted text.
    Requires Tesseract to be installed on the system.
    """
    try:
        # Open the image from the byte stream
        image = Image.open(io.BytesIO(image_bytes))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        return text
    except FileNotFoundError:
        return "Error: Tesseract is not installed or not in your PATH. Please install Tesseract."
    except Exception as e:
        return f"An error occurred during OCR: {e}"
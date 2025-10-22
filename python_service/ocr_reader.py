# python_service/ocr_reader.py
from PIL import Image
import pytesseract
import io

def extract_text(file_storage):
    # file_storage is Werkzeug FileStorage from Flask request.files
    img = Image.open(file_storage.stream).convert('RGB')
    # optionally resize/convert to better contrast
    text = pytesseract.image_to_string(img)
    return text

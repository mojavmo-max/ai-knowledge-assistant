import base64
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import cv2
import pytesseract


'''OCR Services'''
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def clean_text(t):
    lines = [l.strip() for l in t.splitlines()]
    return "\n".join(l for l in lines if len(l) > 2)

def run_ocr(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config = custom_config)

    cleaned = clean_text(text)
    return cleaned


'''LLM Services'''
load_dotenv()
client = OpenAI()

def resize_image(path):
    img = Image.open(path)
    img.thumbnail((1024, 1024))
    img.save("resized.png")
    return "resized.png"

def encode_image(path):
    resized_path = resize_image(path)
    with open(resized_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def run_vision(image_path):
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this document."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content

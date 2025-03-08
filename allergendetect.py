import cv2
import pytesseract
import spacy
import re
import numpy as np
from PIL import Image
import easyocr

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Allergen dictionary
FDA_ALLERGENS = {
    "milk": ["milk", "lactose", "butter", "cheese", "cream"],
    "eggs": ["eggs", "egg whites", "egg yolks", "albumin"],
    "fish": ["fish", "salmon", "tuna", "cod"],
    "shellfish": ["shrimp", "lobster", "crab", "shellfish"],
    "tree nuts": ["almonds", "cashews", "hazelnuts", "pistachios"],
    "peanuts": ["peanuts", "peanut butter"],
    "wheat": ["wheat", "gluten", "flour", "wheat gluten"],
    "soy": ["soy", "soybean", "tofu", "soya", "soy protein"],
    "sesame": ["sesame", "tahini"]
}

# Common ingredient keywords
COMMON_INGREDIENTS = set()
for allergen_list in FDA_ALLERGENS.values():
    COMMON_INGREDIENTS.update(allergen_list)
COMMON_INGREDIENTS.update(["sugar", "salt", "flour", "oil", "butter", "yeast", "cheese", "gluten"])

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"], gpu=False)

def preprocess_image(frame):
    """Preprocess the image for OCR."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, h=20)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return gray

def extract_text(frame):
    """Extract text from an image using Tesseract and EasyOCR."""
    processed_img = preprocess_image(frame)
    pil_image = Image.fromarray(processed_img)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(pil_image, config=custom_config)

    easy_text = " ".join(reader.readtext(frame, detail=0))
    text = text + " " + easy_text
    return text.lower()

def extract_ingredients(text):
    """Extract ingredient names from the text."""
    words = set(re.sub(r'[^a-z\s-]', '', text).split())
    return list(words.intersection(COMMON_INGREDIENTS))

def check_allergens(ingredients):
    """Check if the detected ingredients contain allergens."""
    allergens_found = []
    for allergen, synonyms in FDA_ALLERGENS.items():
        if any(ingredient in synonyms for ingredient in ingredients):
            allergens_found.append(allergen)
    return allergens_found

def main():
    """Main function to process webcam frames in real time."""
    cap = cv2.VideoCapture(0)  # Open webcam

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        text = extract_text(frame)
        ingredients = extract_ingredients(text)
        allergens_found = check_allergens(ingredients)

        # Overlay the results on the frame
        cv2.putText(frame, "Detected Ingredients:", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset = 80
        for ingredient in ingredients:
            cv2.putText(frame, f"- {ingredient}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_offset += 30

        if allergens_found:
            cv2.putText(frame, f"⚠️ Allergens: {', '.join(allergens_found)}", (10, y_offset + 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("Real-Time Allergen Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

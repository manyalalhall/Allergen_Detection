#!/usr/bin/env python
# coding: utf-8

# In[3]:


import cv2
import pytesseract
import spacy
import re
from PIL import Image
import numpy as np
from textblob import TextBlob
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

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Error: Image '{image_path}' not found.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    gray = cv2.fastNlMeansDenoising(gray, h=20)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return gray

def extract_text(image_path):
    processed_img = preprocess_image(image_path)
    pil_image = Image.fromarray(processed_img)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(pil_image, config=custom_config)

    reader = easyocr.Reader(["en"], gpu=False)
    easy_text = " ".join(reader.readtext(image_path, detail=0))

    text = text + " " + easy_text
    return text

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s-]', '', text)
    return text

def extract_ingredients(text):
    words = set(text.split())
    ingredients = words.intersection(COMMON_INGREDIENTS)
    return list(ingredients)

def check_allergens(ingredients):
    allergens_found = []
    for allergen, synonyms in FDA_ALLERGENS.items():
        if any(ingredient in synonyms for ingredient in ingredients):
            allergens_found.append(allergen)
    return allergens_found

def main(image_path):
    extracted_text = extract_text(image_path)
    cleaned_text = clean_text(extracted_text)
    ingredients = extract_ingredients(cleaned_text)

    print("Extracted Ingredients:", ingredients)
    allergens_found = check_allergens(ingredients)

    if allergens_found:
        print("⚠️ Contains Allergens:", allergens_found)
    else:
        print("✅ No Allergens Found")

image_path = "uncle-checkpoint.jpg"
main(image_path)


# In[ ]:





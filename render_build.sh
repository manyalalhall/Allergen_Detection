#!/bin/bash

# Update package lists
apt-get update

# Install Tesseract OCR
apt-get install -y tesseract-ocr

# Install required Python packages
pip install -r requirements.txt

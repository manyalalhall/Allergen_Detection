#!/bin/bash
set -o errexit  # Exit on error

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download and configure Tesseract manually
mkdir -p tesseract
curl -L -o tesseract/tesseract.tar.xz https://github.com/tesseract-ocr/tessdata_best/releases/download/latest/tessdata_best.tar.gz
tar -xf tesseract/tesseract.tar.xz -C tesseract/

# Set Tesseract environment variable
export TESSDATA_PREFIX=$(pwd)/tesseract

echo "Build completed successfully!"

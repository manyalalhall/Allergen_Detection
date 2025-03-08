#!/usr/bin/env bash
echo "Installing dependencies..."
apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

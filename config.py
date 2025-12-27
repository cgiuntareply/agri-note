"""
Configurazione AgriNote
Supporta variabili d'ambiente per facilitare migrazione a Supabase
"""
import os
from typing import Optional

# Database Configuration
# Per SQLite locale (default):
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agrinote.db")

# Per Supabase PostgreSQL (quando andrà online):
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

# Meteo Configuration
METEO_LAT = float(os.getenv("METEO_LAT", "45.4642"))  # Milano default
METEO_LNG = float(os.getenv("METEO_LNG", "9.1900"))

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "agrinote-secret-key-change-in-production")
ALGORITHM = "HS256"

# OCR Configuration
USE_TESSERACT = os.getenv("USE_TESSERACT", "false").lower() == "true"
# Tesseract richiede installazione sistema:
# macOS: brew install tesseract
# Linux: apt-get install tesseract-ocr
# Windows: scarica installer da GitHub

# File Upload
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10 MB default

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, production


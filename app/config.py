import os
from pathlib import Path

# Base directory path
BASE_DIR = Path(__file__).resolve().parent.parent

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
HASH_ALGORITHM = "sha256"

# DS Service configuration (to be updated when available)
DS_SERVICE_ENDPOINT = os.getenv("DS_SERVICE_ENDPOINT", "http://localhost:8001/analyze")

# App configuration
APPLICATION_NAME = "VibeCheck Business Platform"
VERSION = "1.0.0"
DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

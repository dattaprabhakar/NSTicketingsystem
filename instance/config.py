# instance/config.py
# You generally use .env instead, but this is a fallback
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'default_fallback_secret_key')
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/fallback_db')
# Add other config variables here if needed
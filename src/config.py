from dotenv import load_dotenv
import os

load_dotenv()  # Take environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key-here'

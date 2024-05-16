from dotenv import load_dotenv
import os

load_dotenv()  # Take environment variables from .env file

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        raise ValueError("No SECRET_KEY set for Flask application. Did you forget to create a .env file?")

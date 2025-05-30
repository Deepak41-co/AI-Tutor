# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # Database Config
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/AI_chatbot')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Logging Config
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')




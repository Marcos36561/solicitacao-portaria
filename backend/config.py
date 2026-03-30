import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/portaria')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'options': '-c timezone=America/Sao_Paulo'
        }
    }
    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    # Extensões permitidas
    IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
    PDF_EXTENSIONS = {'pdf'}
    ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | PDF_EXTENSIONS
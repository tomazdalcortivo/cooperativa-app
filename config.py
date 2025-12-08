import os

class Config:
    SECRET_KEY = "123456"
    SQLALCHEMY_DATABASE_URI = "sqlite:///cooperativa.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limite de 16MB por arquivo
import os

class Config:
    """Configuración base para Flask"""
    
    # Base de datos SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    JSON_SORT_KEYS = False
    
    # CORS
    CORS_HEADERS = 'Content-Type'

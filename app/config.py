import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///bicycle_store.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')  # Замените на ваш секретный ключ

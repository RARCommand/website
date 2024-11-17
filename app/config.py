import os

class Config:
    # Общие настройки
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Строка подключения к базе данных (подставьте External Database URL)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://bike_store_64y3_user:heCSFrdNYHiEYD7G8QPpuwNfeE2at9hg@dpg-csss8mggph6c7398j6fg-a.oregon-postgres.render.com/bike_store_64y3'
    )

    # Секретный ключ для безопасности
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')

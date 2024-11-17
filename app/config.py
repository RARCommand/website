import os

class Config:
    # Включаем/выключаем SQLAlchemy отслеживание изменений
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Строка подключения к базе данных (используем переменную окружения или значение по умолчанию)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://bike_store_64y3_user:heCSFrdNYHiEYD7G8QPpuwNfeE2at9hg@dpg-csss8mggph6c7398j6fg-a.oregon-postgres.render.com:5432/bike_store_64y3'
    )

    # Секретный ключ для безопасности
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')

from flask import Flask
from .extensions import db, migrate
from .main.routes import main, cart, profile
from .admin.routes import admin
from .auth.routes import auth
from flask_login import LoginManager
from .models.bicycle import User
from .config import Config  # Импортируем общий конфиг (без разделения на Development и Production)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Используем общий конфиг

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистрация blueprints
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(cart, url_prefix='/cart')
    app.register_blueprint(profile, url_prefix='/profile')

    return app

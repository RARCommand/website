from flask import Flask
from .extensions import db, migrate
from .main.routes import main, cart, profile
from .admin.routes import admin
from .auth.routes import auth
from flask_login import LoginManager
from .models.bicycle import User
from .config import DevelopmentConfig

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистрация blueprints
    app.register_blueprint(main)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(cart, url_prefix='/cart')  # Используем '/cart' для уникального префикса
    app.register_blueprint(profile, url_prefix='/profile')

    return app

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from os import environ
from .config import config, SECRET_KEY  # Берём SECRET_KEY из config.py

# Инициализация SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Настройки приложения
    app.config['SECRET_KEY'] = SECRET_KEY  # Используем SECRET_KEY из файла
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite?mode=rwc'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = environ.get('SQLALCHEMY_ECHO') in ('1', 'True')

    db.init_app(app)

    from .models import User, Role, Container, ContainerType

    # Настройки Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Разрешаем OAuth в небезопасном режиме (если нужно)
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Подключаем Blueprint'ы
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Создание БД и базового администратора
    with app.app_context():
        if not os.path.exists("db.sqlite"):
            db.create_all()
            app.logger.info("Database created.")

            # Создаем гостевой контейнер
            if not Container.query.filter_by(container_type=ContainerType.GUEST).first():
                try:
                    from .docker_manager import create_guest_container
                    create_guest_container()
                    app.logger.info("Guest container created.")
                except Exception as e:
                    app.logger.error(f"Failed to create guest container: {str(e)}")

            # Читаем данные администратора из config.ini
            admin_email = config['ADMIN']['email']
            admin_name = config['ADMIN']['name']
            admin_password = config['ADMIN']['password']

            if not User.query.filter_by(email=admin_email).first():
                hashed_password = generate_password_hash(admin_password)
                admin = User(email=admin_email, name=admin_name, password=hashed_password, role=Role.ADMIN)
                db.session.add(admin)
                db.session.commit()
                app.logger.info(f"Admin user {admin_email} created.")

    return app

# Создаём приложение
app = create_app()
# This file makes the directory a package

# You can import modules or initialize package-level variables here
# For example:
# from .module_name import some_function

# Initialize package-level variables if needed
# variable_name = value

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "tennissarja.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .models import Pelaaja

    with app.app_context():
        db.create_all()

    from .admin import admin
    from .auth import auth
    from .player import player

    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/')
    from .player import player as player_blueprint
    app.register_blueprint(player_blueprint, url_prefix='/')
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Pelaaja.query.get(int(id))

    print("TESTING! TESTING! TESTING!")
    print(app.url_map)
    return app

def create_database(app):
    if not path.exists('SarjaWeb/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')


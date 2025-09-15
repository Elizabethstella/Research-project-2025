from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = "dev_secret_change_me"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tutor.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = "dev_secret_change_me"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tutor.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Add this for building urls outside requests
    app.config["SERVER_NAME"] = "localhost:5000"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import and register blueprints AFTER app is created
    from .routes.auth import auth
    from .routes.core import core
    from .routes.api import api

    app.register_blueprint(auth)
    app.register_blueprint(core)
    app.register_blueprint(api)

    with app.app_context():
        from . import models
        db.create_all()

    return app

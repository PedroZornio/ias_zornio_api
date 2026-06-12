from flask import Flask
from app.db import init_db
from app.routes.users import users_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(users_bp)
    with app.app_context():
        init_db()
    return app

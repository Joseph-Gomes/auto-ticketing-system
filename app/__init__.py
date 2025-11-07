from flask import Flask
from src.config import Config  # your config file

def create_app():
    app = Flask(__name__)

    # Load SECRET_KEY from environment variable
    app.secret_key = Config.SECRET_KEY

    from app.routes import main
    app.register_blueprint(main)

    return app

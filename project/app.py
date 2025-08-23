# Initialize Flask app
import os

from flask import Flask
from dotenv import dotenv_values


from project.routes import main_bp, webhooks_bp

config = {
    **dotenv_values(".env.shared"),  # load shared development variables
    **dotenv_values(".env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
}

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp, url_prefix='')
    app.register_blueprint(webhooks_bp, url_prefix='/webhooks')

    return app
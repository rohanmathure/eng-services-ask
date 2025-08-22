# Initialize Flask app
import os

from flask import Flask

from project.routes import main_bp, webhooks_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp, url_prefix='')
    app.register_blueprint(webhooks_bp, url_prefix='/webhooks')

    return app
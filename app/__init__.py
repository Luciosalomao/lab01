from flask import Flask
from flasgger import Swagger
from .config import Config
import os

def create_app():
    app = Flask(__name__)
    swagger_path = os.path.join(os.path.dirname(__file__), '..', 'swagger_template.yaml')
    swagger_path = os.path.abspath(swagger_path)

    Swagger(app, template_file=swagger_path)

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

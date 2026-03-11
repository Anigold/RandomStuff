from flask import Flask
from pathlib import Path

def create_app():
    here = Path(__file__).parent
    app = Flask(__name__, template_folder=here / "templates", static_folder=here / "static")

    from .api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")

    from .routes import ui_blueprint
    app.register_blueprint(ui_blueprint)


    return app

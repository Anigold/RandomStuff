from flask import Flask
from pathlib import Path

def create_app():
    here = Path(__file__).parent
    app  = Flask(__name__, template_folder=here / "templates", static_folder=here / "static")

    from backend.storage.database import ensure_schema
    ensure_schema()

    from api.routes.orders import orders_bp
    app.register_blueprint(orders_bp, url_prefix="/api")
    
    from api.routes.items import items_bp
    app.register_blueprint(items_bp, url_prefix="/api")

    return app

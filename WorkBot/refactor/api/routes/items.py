from flask import Blueprint, jsonify, request
from backend.storage.database.item_database_handler import ItemDatabaseHandler

items_bp = Blueprint('items_bp', __name__, url_prefix='/api')
db_handler = ItemDatabaseHandler()

@items_bp.route('/items', methods=['GET'])
def get_items():
    return db_handler.get_items()
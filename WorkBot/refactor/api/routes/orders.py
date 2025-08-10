from flask import Blueprint, jsonify, request
from backend.storage.database.order_database_handler import OrderDatabaseHandler

orders_bp = Blueprint("orders_bp", __name__, url_prefix="/api")
db_handler = OrderDatabaseHandler()

@orders_bp.route("/orders")
def get_orders():
    orders = db_handler.get_all_orders_summary(limit=100)
    return jsonify(orders)

@orders_bp.route("/orders/<int:order_id>")
def get_order_by_id(order_id):
    summary = db_handler.get_order_summary_by_id(order_id)
    if not summary:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "id": summary["id"],
        "date": summary["date"],
        "placed": bool(summary["placed"]),
        "store_name": summary["store_name"],
        "vendor_name": summary["vendor_name"],
        "total_cost": summary["total_cost"] or 0
    })

@orders_bp.route('/orders/<int:order_id>/items')
def get_order_items(order_id):
    items = db_handler.get_order_items(order_id)
    return jsonify(items)

@orders_bp.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    store_id = data.get("store_id")
    vendor_id = data.get("vendor_id")
    date = data.get("date")

    if not all([store_id, vendor_id, date]):
        return jsonify({"error": "Missing required fields"}), 400

    order_id = db_handler.create_order(store_id, vendor_id, date)
    return jsonify({"message": "Order created", "order_id": order_id}), 201

@orders_bp.route("/orders/<int:order_id>/items", methods=["POST"])
def add_order_items(order_id):
    data = request.get_json()
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "No items provided"}), 400

    db_handler.add_order_items(order_id, items)
    return jsonify({"message": f"{len(items)} items added"}), 200

@orders_bp.route("/orders/<int:order_id>/items/<int:item_id>", methods=["PATCH"])
def update_order_item(order_id, item_id):
    data = request.get_json()
    quantity = data.get("quantity")
    cost_per = data.get("cost_per")

    if quantity is None or cost_per is None:
        return jsonify({"error": "Missing quantity or cost_per"}), 400

    db_handler.update_order_item(order_id, item_id, quantity, cost_per)
    return jsonify({"message": "Order item updated"}), 200

@orders_bp.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_order_item(order_id, item_id):
    db_handler.delete_order_item(order_id, item_id)
    return jsonify({"message": "Order item deleted"}), 200
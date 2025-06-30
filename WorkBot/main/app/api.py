from flask import Blueprint, jsonify, request
from backend.workbot.WorkBot import WorkBot
from database.db import get_connection

api_blueprint = Blueprint("api", __name__)
workbot = WorkBot()  # Uses same DB implicitly

@api_blueprint.route("/orders")
def list_orders():
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT Orders.id, Orders.date, Stores.store_name, Vendors.name AS vendor
        FROM Orders
        JOIN Stores ON Orders.store_id = Stores.id
        JOIN Vendors ON Orders.vendor_id = Vendors.id
        ORDER BY Orders.date DESC
    """).fetchall()
    conn.close()

    return jsonify([
        {
            "id": row["id"],
            "date": row["date"],
            "store": row["store_name"],
            "vendor": row["vendor"]
        }
        for row in rows
    ])

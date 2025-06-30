from flask import Blueprint, render_template
from database.db import get_connection

ui_blueprint = Blueprint("ui", __name__)

@ui_blueprint.route("/orders")
def show_orders():
    conn = get_connection()
    cursor = conn.cursor()

    orders = cursor.execute("""
        SELECT Orders.id, Orders.date, Stores.store_name AS store, Vendors.name AS vendor
        FROM Orders
        JOIN Stores ON Orders.store_id = Stores.id
        JOIN Vendors ON Orders.vendor_id = Vendors.id
        ORDER BY Orders.date DESC
    """).fetchall()

    return render_template("orders.html", orders=orders)

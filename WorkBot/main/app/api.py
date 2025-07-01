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

@api_blueprint.route('/items')
def get_items():
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute('''SELECT id, item_name FROM Items''')
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(items)

@api_blueprint.route("/items/<int:item_id>/details")
def get_item_details(item_id):
    conn = get_connection()
    # conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get basic item info
    cursor.execute("SELECT item_name FROM Items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Get vendor list for this item
    cursor.execute("""
        SELECT Vendors.name AS vendor_name, VendorItems.vendor_sku, VendorItems.price
        FROM VendorItems
        JOIN Vendors ON VendorItems.vendor_id = Vendors.id
        WHERE VendorItems.item_id = ?
    """, (item_id,))
    vendors = [dict(row) for row in cursor.fetchall()]

    # Get recent purchase history
    cursor.execute("""
        SELECT Orders.date, Stores.store_name AS store, OrderItems.quantity, OrderItems.cost_per
        FROM OrderItems
        JOIN Orders ON OrderItems.order_id = Orders.id
        JOIN Stores ON Orders.store_id = Stores.id
        WHERE OrderItems.item_id = ?
        ORDER BY Orders.date DESC
        LIMIT 20
    """, (item_id,))
    purchases = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "item_name": item["item_name"],
        "vendors": vendors,
        "purchase_history": purchases
    })

@api_blueprint.route("/vendors", methods=["GET"])
def get_vendors():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, minimum_order_cost, minimum_order_cases
        FROM Vendors
        ORDER BY name
    """)
    vendors = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(vendors)




@api_blueprint.route("/add_item", methods=["POST"])
def add_item():
    data = request.get_json()
    name = data.get("item_name")
    if not name:
        return jsonify({"error": "Missing item name"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Items (item_name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@api_blueprint.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.get_json()
    item_name = data.get("item_name")

    if not item_name:
        return jsonify({"error": "Missing item name"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Items
        SET item_name = ?
        WHERE id = ?
    """, (item_name, item_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@api_blueprint.route("/add_store", methods=["POST"])
def add_store():
    data = request.get_json()
    name = data.get("store_name")
    address = data.get("address")
    if not name or not address:
        return jsonify({"error": "Missing name or address"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Stores (store_name, address) VALUES (?, ?)", (name, address))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@api_blueprint.route("/add_vendor", methods=["POST"])
def add_vendor():
    data = request.get_json()
    name = data.get("name")
    min_cost = int(data.get("minimum_order_cost", 0))
    min_cases = int(data.get("minimum_order_cases", 0))

    if not name:
        return jsonify({"error": "Missing vendor name"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Vendors (name, minimum_order_cost, minimum_order_cases)
        VALUES (?, ?, ?)
    """, (name, min_cost, min_cases))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

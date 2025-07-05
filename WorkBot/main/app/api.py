from flask import Blueprint, jsonify, request
from backend.workbot.WorkBot import WorkBot
from database.db import get_connection

api_blueprint = Blueprint("api", __name__)
workbot = WorkBot()  # Uses same DB implicitly


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


@api_blueprint.route("/orders")
def get_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, s.store_name, v.name, o.date,
               COUNT(oi.id) AS item_count,
               SUM(oi.quantity * oi.cost_per) AS total_cost,
                o.placed
        FROM Orders o
        JOIN Stores s ON o.store_id = s.id
        JOIN Vendors v ON o.vendor_id = v.id
        LEFT JOIN OrderItems oi ON oi.order_id = o.id
        GROUP BY o.id
        ORDER BY o.date DESC
        LIMIT 100
    """)
    
    rows = cursor.fetchall()
    return jsonify([
        {
            "id": row[0],
            "store_name": row[1],
            "vendor_name": row[2],
            "date": row[3],
            "item_count": row[4],
            "total_cost": row[5] or 0,
            'placed': bool(row[6])
        }
        for row in rows
    ])

@api_blueprint.route("/orders/<int:order_id>")
def get_order_summary(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.id, o.date, o.placed, s.store_name, v.name,
               SUM(oi.quantity * oi.cost_per) AS total_cost
        FROM Orders o
        JOIN Stores s ON o.store_id = s.id
        JOIN Vendors v ON o.vendor_id = v.id
        JOIN OrderItems oi ON oi.order_id = o.id
        WHERE o.id = ?
    """, (order_id,))
    
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "id": row[0],
        "date": row[1],
        "placed": bool(row[2]),
        "store_name": row[3],
        "vendor_name": row[4],
        "total_cost": row[5] or 0
    })

@api_blueprint.route('/orders/<int:order_id>/items')
def get_order_items(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.item_name, oi.quantity, oi.cost_per
        FROM OrderItems oi
        JOIN Items i ON oi.item_id = i.id
        WHERE oi.order_id = ?
    """, (order_id,))

    items = [
        {"name": row[0], "quantity": row[1], "cost_per": row[2]}
        for row in cursor.fetchall()
    ]

    conn.close()
    return jsonify(items)


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

@api_blueprint.route("/items/update/<int:item_id>", methods=["PATCH"])
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


@api_blueprint.route("/vendors/<int:vendor_id>/items")
def get_vendor_items(vendor_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.id, i.item_name, vi.vendor_sku, vi.price
        FROM VendorItems vi
        JOIN Items i ON vi.item_id = i.id
        WHERE vi.vendor_id = ?
    """, (vendor_id,))
    
    items = [
        {
            "id": row[0],
            "name": row[1],
            "sku": row[2],
            "price": row[3]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    print(jsonify(items))
    return jsonify(items)

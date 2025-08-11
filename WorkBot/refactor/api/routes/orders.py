from flask import Blueprint, jsonify, request
from backend.storage.database.order_database_handler import OrderDatabaseHandler
from backend.bots.workbot.work_bot import WorkBot
from datetime import datetime
from typing import Optional, List, Dict, Any
from http import HTTPStatus

orders_bp = Blueprint('orders_bp', __name__, url_prefix='/api')
db_handler = OrderDatabaseHandler()
workbot = WorkBot()

@orders_bp.route('/orders')
def get_orders():
    orders = db_handler.get_all_orders_summary(limit=100)
    return jsonify(orders)

@orders_bp.route('/orders/<int:order_id>')
def get_order_by_id(order_id):
    summary = db_handler.get_order_summary_by_id(order_id)
    if not summary:
        return jsonify({'error': 'Order not found'}), 404

    return jsonify({
        'id': summary['id'],
        'date': summary['date'],
        'placed': bool(summary['placed']),
        'store_name': summary['store_name'],
        'vendor_name': summary['vendor_name'],
        'total_cost': summary['total_cost'] or 0
    })

@orders_bp.route('/orders/<int:order_id>/items')
def get_order_items(order_id):
    items = db_handler.get_order_items(order_id)
    return jsonify(items)

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    store_id = data.get('store_id')
    vendor_id = data.get('vendor_id')
    date = data.get('date')

    if not all([store_id, vendor_id, date]):
        return jsonify({'error': 'Missing required fields'}), 400

    order_id = db_handler.create_order(store_id, vendor_id, date)
    return jsonify({'message': 'Order created', 'order_id': order_id}), 201

@orders_bp.route('/orders/<int:order_id>/items', methods=['POST'])
def add_order_items(order_id):
    data = request.get_json()
    items = data.get('items', [])

    if not items:
        return jsonify({'error': 'No items provided'}), 400

    db_handler.add_order_items(order_id, items)
    return jsonify({'message': f'{len(items)} items added'}), 200

@orders_bp.route('/orders/<int:order_id>/items/<int:item_id>', methods=['PATCH'])
def update_order_item(order_id, item_id):
    data = request.get_json()
    quantity = data.get('quantity')
    cost_per = data.get('cost_per')

    if quantity is None or cost_per is None:
        return jsonify({'error': 'Missing quantity or cost_per'}), 400

    db_handler.update_order_item(order_id, item_id, quantity, cost_per)
    return jsonify({'message': 'Order item updated'}), 200

@orders_bp.route('/orders/<int:order_id>/items/<int:item_id>', methods=['DELETE'])
def delete_order_item(order_id, item_id):
    db_handler.delete_order_item(order_id, item_id)
    return jsonify({'message': 'Order item deleted'}), 200


def upsert_order(self, store_id: int, vendor_id: int, date: str) -> int:
    '''
    Ensure an order row exists; return its id.
    If it exists, keep it and return the existing id.
    '''
    # Try SQLite UPSERT first (requires SQLite ≥ 3.24; Python 3.13 ships a new enough sqlite)
    try:
        query = '''
            INSERT INTO Orders (store_id, vendor_id, date)
            VALUES (?, ?, ?)
            ON CONFLICT(store_id, vendor_id, date) DO NOTHING
        '''
        self.execute(query, (store_id, vendor_id, date))
    except Exception:
        # Fallback path if ON CONFLICT isn't available in your runtime
        pass

    # Return the id (existing or just inserted)
    row = self.fetch_one(
        'SELECT id FROM Orders WHERE store_id = ? AND vendor_id = ? AND date = ?',
        (store_id, vendor_id, date),
    )
    return row['id']

def replace_order_items(self, order_id: int, items: list[dict]) -> None:
    # wipe and reinsert (transaction handled by DatabaseHandler)
    self.execute('DELETE FROM OrderItems WHERE order_id = ?', (order_id,))
    if items:
        self.execute_many(
            'INSERT INTO OrderItems (order_id, item_id, quantity, cost_per) VALUES (?, ?, ?, ?)',
            [(order_id, it['item_id'], it['quantity'], it['cost_per']) for it in items],
        )


@orders_bp.route('/orders/download')
def download_orders():

    body = request.get_json(force=True) or {}
    stores = _ensure_list(body.get('stores'))
    vendors = _ensure_list(body.get('vendors'))
    start_date = _parse_date(body.get('start_date'))
    end_date = _parse_date(body.get('end_date'))

    try:
        # log.info(f'download_orders requested: stores={stores} vendors={vendors} {start_date=} {end_date=}')
        result = workbot.download_orders(
            stores=stores or None,
            vendors=vendors or None,
            start_date=start_date,
            end_date=end_date,
        )
        downloaded_count = getattr(result, 'count', None)
        if downloaded_count is None and isinstance(result, (list, tuple)):
            downloaded_count = len(result)

        # Return the updated view. You can choose to re-use the same filters here.
        rows = _fetch_orders_with_filters(
            store=None,
            vendor=None,
            start_date=start_date,
            end_date=end_date,
            placed=None,
            limit=100,
            offset=0,
        )
        return jsonify({
            'downloaded': downloaded_count,
            'orders': [_to_ui_summary(r) for r in rows],
        }), HTTPStatus.OK
    except Exception as e:
        # log.exception('WorkBot.download_orders failed')
        return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
    



def _parse_date(s: Optional[str]) -> Optional[datetime.date]:
    if not s:
        return None
    return datetime.strptime(s, '%Y-%m-%d').date()

def _parse_bool(s: Optional[str]) -> Optional[bool]:
    if s is None:
        return None
    return s.lower() in {'1', 'true', 't', 'yes', 'y'}

def _ensure_list(v: Any) -> List[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]

def _to_ui_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Normalize DB rows to the UI shape consistently. Keep keys you already expose.
    '''
    return {
        'id': row['id'],
        'date': row['date'],
        'placed': bool(row.get('placed', False)),
        'store_name': row.get('store_name'),
        'vendor_name': row.get('vendor_name'),
        'total_cost': row.get('total_cost') or 0,
        # Feel free to add 'item_count' if you have it in your summary view
        **({'item_count': row['item_count']} if 'item_count' in row else {}),
    }

def _fetch_orders_with_filters(
    store: Optional[str],
    vendor: Optional[str],
    start_date: Optional[datetime.date],
    end_date: Optional[datetime.date],
    placed: Optional[bool],
    limit: Optional[int],
    offset: Optional[int],
) -> List[Dict[str, Any]]:
    '''
    Call into the DB handler. If your handler already has a filtered query, use it.
    Otherwise fall back to get_all_orders_summary and filter in Python (less efficient).
    '''
    # Prefer DB-side filtering if available
    if hasattr(db_handler, 'get_orders_summary'):
        # log.debug('Using db_handler.get_orders_summary with filters')
        rows = db_handler.get_orders_summary(
            store=store,
            vendor=vendor,
            start_date=start_date,
            end_date=end_date,
            placed=placed,
            limit=limit,
            offset=offset,
        )
        return rows

    # Fallback: simple Python-side filtering
    # log.warning('get_orders_summary not found; falling back to Python-side filtering')
    rows = db_handler.get_all_orders_summary(limit=10_000)  # grab large set; trim below
    out = []
    for r in rows:
        if store and r.get('store_name') != store:
            continue
        if vendor and r.get('vendor_name') != vendor:
            continue
        if placed is not None and bool(r.get('placed')) != placed:
            continue
        if start_date or end_date:
            # r['date'] is assumed 'YYYY-MM-DD'
            try:
                rd = datetime.strptime(r['date'], '%Y-%m-%d').date()
            except Exception:
                continue
            if start_date and rd < start_date:
                continue
            if end_date and rd > end_date:
                continue
        out.append(r)
    if offset:
        out = out[offset:]
    if limit:
        out = out[:limit]
    return out
# endregion

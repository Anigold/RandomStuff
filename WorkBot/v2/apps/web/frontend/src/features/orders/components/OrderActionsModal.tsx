import type { OrderDto } from "../../../api/ordersApi";
import {
  canCancelOrder,
  formatDate,
  formatDateTime,
  formatOrderLineQuantity,
  formatOrderStatus,
  formatOrderTitle,
  getOrderStatusBadgeClass,
  getOrderLines,
  getOrderLineName,
} from "../orderHelpers";

type OrderActionsModalProps = {
  order: OrderDto;
  onClose: () => void;
  onCancel: (order: OrderDto) => void;
};

export function OrderActionsModal({
  order,
  onClose,
  onCancel,
}: OrderActionsModalProps) {
    const lines = getOrderLines(order);

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card item-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="order-actions-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div className="modal-title-group">
            <span className="modal-eyebrow">Order details</span>

            <div className="modal-title-row">
              <h3 id="order-actions-title">{formatOrderTitle(order)}</h3>

              <span className={getOrderStatusBadgeClass(order.status)}>
                {formatOrderStatus(order.status)}
              </span>
            </div>

            <p>{order.store_name || order.store_id || "Unknown store"}</p>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </header>

        <div className="modal-body">
          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Order information</h4>
              <p>Vendor, store, status, and dates.</p>
            </div>

            <dl className="detail-grid">
              <DetailItem
                label="Vendor"
                value={order.vendor_name || order.vendor_id}
              />
              <DetailItem
                label="Store"
                value={order.store_name || order.store_id}
              />
              <DetailItem label="Order date" value={formatDate(order.order_date)} />
              <DetailItem
                label="Created"
                value={formatDateTime(order.created_at)}
              />
              <DetailItem
                label="Updated"
                value={formatDateTime(order.updated_at)}
              />
              <DetailItem label="Order ID" value={order.id} />
            </dl>
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Order lines</h4>
              <p>Items included in this order.</p>
            </div>

            {lines.length === 0 ? (
              <div className="detail-note-card">No order lines found.</div>
            ) : (
              <div className="detail-list">
                {lines.map((line, index) => (
                  <div key={line.id || index} className="detail-list-row">
                    <strong>{getOrderLineName(line)}</strong>
                    <span>{formatOrderLineQuantity(line)}</span>
                    {line.notes && <span>{line.notes}</span>}
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Notes</h4>
              <p>Additional notes for this order.</p>
            </div>

            <div className="detail-note-card">
              {order.notes?.trim() || "No notes."}
            </div>
          </section>
        </div>

        <footer className="modal-actions">
          <button type="button" onClick={onClose}>
            Close
          </button>

          {canCancelOrder(order) && (
            <button
              type="button"
              className="button-danger"
              onClick={() => onCancel(order)}
            >
              Cancel order
            </button>
          )}
        </footer>
      </section>
    </div>
  );
}

type DetailItemProps = {
  label: string;
  value?: string | number | null;
};

function DetailItem({ label, value }: DetailItemProps) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value ? String(value) : "—"}</dd>
    </div>
  );
}
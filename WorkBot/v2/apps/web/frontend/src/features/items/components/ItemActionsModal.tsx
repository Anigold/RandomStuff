import type { ItemDto } from "../../../api/itemsApi";

type ItemActionsModalProps = {
  item: ItemDto;
  canManageItems: boolean;
  onClose: () => void;
  onEdit: (item: ItemDto) => void;
  onDeactivate: (item: ItemDto) => void;
};

export function ItemActionsModal({
  item,
  canManageItems,
  onClose,
  onEdit,
  onDeactivate,
}: ItemActionsModalProps) {
  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={onClose}
    >
      <section
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="item-actions-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div>
            <h3 id="item-actions-title">{item.name}</h3>
            <p>{item.is_active ? "Active item" : "Inactive item"}</p>
          </div>

          <button type="button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <dl className="detail-grid">
          <div>
            <dt>Category</dt>
            <dd>{item.category ?? "—"}</dd>
          </div>

          <div>
            <dt>Subcategory</dt>
            <dd>{item.subcategory ?? "—"}</dd>
          </div>

          <div>
            <dt>Count unit</dt>
            <dd>{formatQuantity(item.count_unit_quantity, item.count_unit_measure)}</dd>
          </div>

          <div>
            <dt>Each</dt>
            <dd>
              {item.custom_each_name
                ? item.custom_each_name
                : formatQuantity(item.each_quantity, item.each_measure)}
            </dd>
          </div>

          <div>
            <dt>Weight</dt>
            <dd>{formatQuantity(item.weight_quantity, item.weight_measure)}</dd>
          </div>

          <div>
            <dt>Volume</dt>
            <dd>{formatQuantity(item.volume_quantity, item.volume_measure)}</dd>
          </div>
        </dl>

        {canManageItems ? (
          <footer className="modal-actions">
            <button type="button" onClick={() => onEdit(item)}>
              Edit item
            </button>

            {item.is_active && (
              <button type="button" onClick={() => onDeactivate(item)}>
                Mark inactive
              </button>
            )}

            <button type="button" onClick={onClose}>
              Close
            </button>
          </footer>
        ) : (
          <footer className="modal-actions">
            <button type="button" onClick={onClose}>
              Close
            </button>
          </footer>
        )}
      </section>
    </div>
  );
}

function formatQuantity(
  quantity?: string | null,
  measure?: string | null,
): string {
  const parts = [quantity, measure].filter(Boolean);

  return parts.length ? parts.join(" ") : "—";
}
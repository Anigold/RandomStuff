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
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card item-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="item-actions-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div className="modal-title-group">
            <span className="modal-eyebrow">Item details</span>

            <div className="modal-title-row">
              <h3 id="item-actions-title">{item.name}</h3>

              <span
                className={
                  item.is_active
                    ? "status-badge status-badge-active"
                    : "status-badge status-badge-inactive"
                }
              >
                {item.is_active ? "Active" : "Inactive"}
              </span>
            </div>

            <p>
              {[item.category, item.subcategory].filter(Boolean).join(" / ") ||
                "Uncategorized item"}
            </p>
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
              <h4>Catalog information</h4>
              <p>Basic item classification and counting setup.</p>
            </div>

            <dl className="detail-grid">
              <DetailItem label="Category" value={item.category} />
              <DetailItem label="Subcategory" value={item.subcategory} />
              <DetailItem
                label="Count unit"
                value={formatQuantity(
                  item.count_unit_quantity,
                  item.count_unit_measure,
                )}
              />
              <DetailItem
                label="Each"
                value={
                  item.custom_each_name
                    ? item.custom_each_name
                    : formatQuantity(item.each_quantity, item.each_measure)
                }
              />
            </dl>
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Measurement details</h4>
              <p>Optional weight and volume references for this item.</p>
            </div>

            <dl className="detail-grid">
              <DetailItem
                label="Weight"
                value={formatQuantity(item.weight_quantity, item.weight_measure)}
              />
              <DetailItem
                label="Volume"
                value={formatQuantity(item.volume_quantity, item.volume_measure)}
              />
            </dl>
          </section>
        </div>

        <footer className="modal-actions">
          <button type="button" onClick={onClose}>
            Close
          </button>

          {canManageItems && (
            <>
              <button type="button" onClick={() => onEdit(item)}>
                Edit item
              </button>

              {item.is_active && (
                <button
                  type="button"
                  className="button-danger"
                  onClick={() => onDeactivate(item)}
                >
                  Mark inactive
                </button>
              )}
            </>
          )}
        </footer>
      </section>
    </div>
  );
}

type DetailItemProps = {
  label: string;
  value?: string | null;
};

function DetailItem({ label, value }: DetailItemProps) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value || "—"}</dd>
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
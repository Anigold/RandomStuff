import type { StoreDto } from "../../../api/storesApi";

type StoreActionsModalProps = {
  store: StoreDto;
  onClose: () => void;
  onEdit: (store: StoreDto) => void;
  onDeactivate: (store: StoreDto) => void;
};

export function StoreActionsModal({
  store,
  onClose,
  onEdit,
  onDeactivate,
}: StoreActionsModalProps) {
  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card item-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="store-actions-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div className="modal-title-group">
            <span className="modal-eyebrow">Store details</span>

            <div className="modal-title-row">
              <h3 id="store-actions-title">{store.name}</h3>

              <span
                className={
                  store.is_active
                    ? "status-badge status-badge-active"
                    : "status-badge status-badge-inactive"
                }
              >
                {store.is_active ? "Active" : "Inactive"}
              </span>
            </div>

            <p>{store.address || "No address on file"}</p>
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
              <h4>Store information</h4>
              <p>Primary contact and location details.</p>
            </div>

            <dl className="detail-grid">
              <DetailItem label="General manager" value={store.general_manager} />
              <DetailItem label="Inventory clerk" value={store.inventory_clerk} />
              <DetailItem label="Phone number" value={store.phone_number} />
              <DetailItem label="Address" value={store.address} />
            </dl>
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Notes</h4>
              <p>Operational notes for this store.</p>
            </div>

            <div className="detail-note-card">
              {store.special_notes?.trim() || "No special notes."}
            </div>
          </section>
        </div>

        <footer className="modal-actions">
          <button type="button" onClick={onClose}>
            Close
          </button>

          <button type="button" onClick={() => onEdit(store)}>
            Edit store
          </button>

          {store.is_active && (
            <button
              type="button"
              className="button-danger"
              onClick={() => onDeactivate(store)}
            >
              Deactivate store
            </button>
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
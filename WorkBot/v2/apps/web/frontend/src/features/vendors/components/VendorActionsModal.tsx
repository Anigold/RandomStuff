import type { StoreDto } from "../../../api/storesApi";
import type { VendorDto } from "../../../api/vendorsApi";

type VendorActionsModalProps = {
  vendor: VendorDto;
  stores: StoreDto[];
  onClose: () => void;
  onEdit: (vendor: VendorDto) => void;
  onDeactivate: (vendor: VendorDto) => void;
  onActivate: (vendor: VendorDto) => void;
};

export function VendorActionsModal({
  vendor,
  stores,
  onClose,
  onEdit,
  onDeactivate,
  onActivate,
}: VendorActionsModalProps) {
  const storeNameById = new Map(stores.map((store) => [store.id, store.name]));

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card item-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="vendor-actions-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div className="modal-title-group">
            <span className="modal-eyebrow">Vendor details</span>

            <div className="modal-title-row">
              <h3 id="vendor-actions-title">{vendor.name}</h3>

              <span
                className={
                  vendor.is_active
                    ? "status-badge status-badge-active"
                    : "status-badge status-badge-inactive"
                }
              >
                {vendor.is_active ? "Active" : "Inactive"}
              </span>
            </div>

            <p>{vendor.order_format || "No order format on file"}</p>
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
              <h4>Ordering information</h4>
              <p>How orders are placed with this vendor.</p>
            </div>

            <dl className="detail-grid">
              <DetailItem
                label="Methods"
                value={vendor.ordering.method.join(", ")}
              />
              <DetailItem label="Email" value={vendor.ordering.email} />
              <DetailItem label="Portal" value={vendor.ordering.portal_url} />
              <DetailItem
                label="Phone"
                value={vendor.ordering.phone_number}
              />
              <DetailItem
                label="Minimum value"
                value={formatCurrencyish(vendor.min_order_value)}
              />
              <DetailItem
                label="Minimum cases"
                value={
                  vendor.min_order_cases > 0
                    ? String(vendor.min_order_cases)
                    : "—"
                }
              />
            </dl>
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Internal contacts</h4>
              <p>People or teams used for vendor communication.</p>
            </div>

            {vendor.internal_contacts.length === 0 ? (
              <div className="detail-note-card">No contacts on file.</div>
            ) : (
              <div className="detail-list">
                {vendor.internal_contacts.map((contact, index) => (
                  <div
                    key={`${contact.name}-${index}`}
                    className="detail-list-row"
                  >
                    <strong>{contact.name}</strong>
                    <span>{contact.title || "—"}</span>
                    <span>{contact.email || "—"}</span>
                    <span>{contact.phone || "—"}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Schedule</h4>
              <p>Order and delivery timing.</p>
            </div>

            {vendor.ordering.schedule.length === 0 ? (
              <div className="detail-note-card">No schedule on file.</div>
            ) : (
              <div className="detail-list">
                {vendor.ordering.schedule.map((entry, index) => (
                  <div
                    key={`${entry.order_day}-${index}`}
                    className="detail-list-row"
                  >
                    <strong>{entry.order_day}</strong>
                    <span>
                      Delivers:{" "}
                      {entry.delivery_days.length
                        ? entry.delivery_days.join(", ")
                        : "—"}
                    </span>
                    <span>Cutoff: {entry.cutoff_time || "—"}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Store references</h4>
              <p>Vendor account or reference values by store.</p>
            </div>

            {vendor.store_references.length === 0 ? (
              <div className="detail-note-card">
                No store references on file.
              </div>
            ) : (
              <div className="detail-list">
                {vendor.store_references.map((reference) => (
                  <div key={reference.store_id} className="detail-list-row">
                    <strong>
                      {storeNameById.get(reference.store_id) ??
                        reference.store_id}
                    </strong>
                    <span>{reference.vendor_store_reference || "—"}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="modal-section">
            <div className="modal-section-header">
              <h4>Notes</h4>
              <p>Operational notes for this vendor.</p>
            </div>

            <div className="detail-note-card">
              {vendor.special_notes?.trim() || "No special notes."}
            </div>
          </section>
        </div>

        <footer className="modal-actions">
          <button type="button" onClick={onClose}>
            Close
          </button>

          <button type="button" onClick={() => onEdit(vendor)}>
            Edit vendor
          </button>

          {vendor.is_active ? (
            <button
              type="button"
              className="button-danger"
              onClick={() => onDeactivate(vendor)}
            >
              Deactivate vendor
            </button>
          ) : (
            <button type="button" onClick={() => onActivate(vendor)}>
              Reactivate vendor
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

function formatCurrencyish(value: string | number): string {
  const text = String(value ?? "0");

  if (text === "0" || text === "0.00") {
    return "—";
  }

  return `$${text}`;
}
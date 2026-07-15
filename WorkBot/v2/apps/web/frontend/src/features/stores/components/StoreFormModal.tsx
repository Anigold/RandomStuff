import { useState, type FormEvent } from "react";

import type { StoreDto, StoreWriteDto } from "../../../api/storesApi";

type StoreFormModalProps = {
  initialStore?: StoreDto | null;
  title: string;
  submitLabel: string;
  onSubmit: (store: StoreWriteDto) => Promise<void>;
  onClose: () => void;
};

type StoreFormState = {
  name: string;
  is_active: boolean;
  general_manager: string;
  inventory_clerk: string;
  address: string;
  phone_number: string;
  special_notes: string;
};

export function StoreFormModal({
  initialStore,
  title,
  submitLabel,
  onSubmit,
  onClose,
}: StoreFormModalProps) {

  const [form, setForm] = useState<StoreFormState>(() => ({
    name:            initialStore?.name ?? "",
    is_active:       initialStore?.is_active ?? true,
    general_manager: initialStore?.general_manager ?? "",
    inventory_clerk: initialStore?.inventory_clerk ?? "",
    address:         initialStore?.address ?? "",
    phone_number:    initialStore?.phone_number ?? "",
    special_notes:   initialStore?.special_notes ?? "",
  }));

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function updateField<K extends keyof StoreFormState>(
    key: K,
    value: StoreFormState[K],
  ) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.name.trim()) {
      setErrorMessage("Store name is required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      console.log("Updating store payload:", form);
      await onSubmit({
        name:            form.name.trim(),
        is_active:       form.is_active,
        general_manager: emptyToNull(form.general_manager),
        inventory_clerk: emptyToNull(form.inventory_clerk),
        address:         emptyToNull(form.address),
        phone_number:    emptyToNull(form.phone_number),
        special_notes:   form.special_notes.trim() || "",
      });
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to save store.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card edit-item-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="store-form-title"
        onClick={(event) => event.stopPropagation()}
      >
        <form className="modal-form" onSubmit={handleSubmit}>
          <header className="modal-header">
            <div className="modal-title-group">
              <span className="modal-eyebrow">Store management</span>

              <div className="modal-title-row">
                <h3 id="store-form-title">{title}</h3>

                <span
                  className={
                    form.is_active
                      ? "status-badge status-badge-active"
                      : "status-badge status-badge-inactive"
                  }
                >
                  {form.is_active ? "Active" : "Inactive"}
                </span>
              </div>

              <p>
                {initialStore
                  ? "Update this store's operating information."
                  : "Create a new store for WorkBot operations."}
              </p>
            </div>

            <button
              type="button"
              className="modal-close-button"
              onClick={onClose}
              aria-label="Close"
              disabled={isSubmitting}
            >
              ×
            </button>
          </header>

          <div className="modal-body">
            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Basic information</h4>
                <p>Name, status, and store contacts.</p>
              </div>

              <div className="form-grid">
                <TextField
                  label="Store name"
                  value={form.name}
                  required
                  disabled={isSubmitting}
                  onChange={(value) => updateField("name", value)}
                />

                <TextField
                  label="General manager"
                  value={form.general_manager}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("general_manager", value)}
                />

                <TextField
                  label="Inventory clerk"
                  value={form.inventory_clerk}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("inventory_clerk", value)}
                />

                <TextField
                  label="Phone number"
                  value={form.phone_number}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("phone_number", value)}
                />
              </div>

              <label className="checkbox-row item-active-row">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  disabled={isSubmitting}
                  onChange={(event) =>
                    updateField("is_active", event.target.checked)
                  }
                />

                <span>
                  <strong>Active store</strong>
                  <small>
                    Active stores can appear in operational workflows.
                  </small>
                </span>
              </label>
            </section>

            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Location and notes</h4>
                <p>Optional address and operational notes.</p>
              </div>

              <div className="form-grid">
                <label className="form-field form-field-wide">
                  <span>Address</span>

                  <textarea
                    value={form.address}
                    disabled={isSubmitting}
                    rows={3}
                    onChange={(event) =>
                      updateField("address", event.target.value)
                    }
                  />
                </label>

                <label className="form-field form-field-wide">
                  <span>Special notes</span>

                  <textarea
                    value={form.special_notes}
                    disabled={isSubmitting}
                    rows={4}
                    onChange={(event) =>
                      updateField("special_notes", event.target.value)
                    }
                  />
                </label>
              </div>
            </section>

            {errorMessage && (
              <div className="error-card" role="alert">
                {errorMessage}
              </div>
            )}
          </div>

          <footer className="modal-actions">
            <button type="button" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : submitLabel}
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
}

type TextFieldProps = {
  label: string;
  value: string;
  required?: boolean;
  disabled?: boolean;
  onChange: (value: string) => void;
};

function TextField({
  label,
  value,
  required = false,
  disabled = false,
  onChange,
}: TextFieldProps) {
  return (
    <label className="form-field">
      <span>{label}</span>

      <input
        value={value}
        required={required}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();

  return trimmed ? trimmed : null;
}
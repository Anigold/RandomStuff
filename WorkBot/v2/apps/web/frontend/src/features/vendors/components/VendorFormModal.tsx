import { useMemo, useState, type FormEvent } from "react";

import type { StoreDto } from "../../../api/storesApi";
import type {
  ContactInfoDto,
  ScheduleEntryDto,
  VendorDto,
  VendorStoreReferenceDto,
  VendorWriteDto,
} from "../../../api/vendorsApi";

type VendorFormModalProps = {
  initialVendor?: VendorDto | null;
  stores: StoreDto[];
  title: string;
  submitLabel: string;
  onSubmit: (vendor: VendorWriteDto) => Promise<void>;
  onClose: () => void;
};

type ContactFormState = ContactInfoDto;

type ScheduleFormState = {
  order_day: string;
  delivery_days_text: string;
  cutoff_time: string;
};

type StoreReferenceFormState = VendorStoreReferenceDto;

type VendorFormState = {
  name: string;
  is_active: boolean;
  order_format: string;
  special_notes: string;
  min_order_value: string;
  min_order_cases: string;
  ordering_methods_text: string;
  ordering_email: string;
  ordering_portal_url: string;
  ordering_phone_number: string;
  internal_contacts: ContactFormState[];
  schedule: ScheduleFormState[];
  store_references: StoreReferenceFormState[];
};

export function VendorFormModal({
  initialVendor,
  stores,
  title,
  submitLabel,
  onSubmit,
  onClose,
}: VendorFormModalProps) {
  const [form, setForm] = useState<VendorFormState>(() =>
    vendorToFormState(initialVendor, stores),
  );

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const activeStoreReferenceCount = useMemo(
    () =>
      form.store_references.filter((reference) =>
        reference.vendor_store_reference.trim(),
      ).length,
    [form.store_references],
  );

  function updateField<K extends keyof VendorFormState>(
    key: K,
    value: VendorFormState[K],
  ) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function updateContact(
    index: number,
    key: keyof ContactFormState,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      internal_contacts: current.internal_contacts.map((contact, contactIndex) =>
        contactIndex === index
          ? {
              ...contact,
              [key]: value,
            }
          : contact,
      ),
    }));
  }

  function addContact() {
    setForm((current) => ({
      ...current,
      internal_contacts: [
        ...current.internal_contacts,
        {
          name: "",
          title: "",
          email: "",
          phone: "",
        },
      ],
    }));
  }

  function removeContact(index: number) {
    setForm((current) => ({
      ...current,
      internal_contacts: current.internal_contacts.filter(
        (_, contactIndex) => contactIndex !== index,
      ),
    }));
  }

  function updateSchedule(
    index: number,
    key: keyof ScheduleFormState,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      schedule: current.schedule.map((entry, entryIndex) =>
        entryIndex === index
          ? {
              ...entry,
              [key]: value,
            }
          : entry,
      ),
    }));
  }

  function addScheduleEntry() {
    setForm((current) => ({
      ...current,
      schedule: [
        ...current.schedule,
        {
          order_day: "",
          delivery_days_text: "",
          cutoff_time: "",
        },
      ],
    }));
  }

  function removeScheduleEntry(index: number) {
    setForm((current) => ({
      ...current,
      schedule: current.schedule.filter(
        (_, entryIndex) => entryIndex !== index,
      ),
    }));
  }

  function updateStoreReference(storeId: string, value: string) {
    setForm((current) => ({
      ...current,
      store_references: current.store_references.map((reference) =>
        reference.store_id === storeId
          ? {
              ...reference,
              vendor_store_reference: value,
            }
          : reference,
      ),
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.name.trim()) {
      setErrorMessage("Vendor name is required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await onSubmit(formStateToWriteDto(form));
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to save vendor.",
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
        aria-labelledby="vendor-form-title"
        onClick={(event) => event.stopPropagation()}
      >
        <form className="modal-form" onSubmit={handleSubmit}>
          <header className="modal-header">
            <div className="modal-title-group">
              <span className="modal-eyebrow">Vendor management</span>

              <div className="modal-title-row">
                <h3 id="vendor-form-title">{title}</h3>

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
                {initialVendor
                  ? "Update vendor ordering and reference information."
                  : "Create a new vendor for purchasing workflows."}
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
                <p>Name, status, format, and minimum order rules.</p>
              </div>

              <div className="form-grid">
                <TextField
                  label="Vendor name"
                  value={form.name}
                  required
                  disabled={isSubmitting}
                  onChange={(value) => updateField("name", value)}
                />

                <TextField
                  label="Order format"
                  value={form.order_format}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("order_format", value)}
                />

                <TextField
                  label="Minimum order value"
                  value={form.min_order_value}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("min_order_value", value)}
                />

                <TextField
                  label="Minimum order cases"
                  value={form.min_order_cases}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("min_order_cases", value)}
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
                  <strong>Active vendor</strong>
                  <small>
                    Active vendors can be used in purchasing workflows.
                  </small>
                </span>
              </label>
            </section>

            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Ordering information</h4>
                <p>Email, portal, phone, and supported ordering methods.</p>
              </div>

              <div className="form-grid">
                <TextField
                  label="Methods"
                  value={form.ordering_methods_text}
                  disabled={isSubmitting}
                  placeholder="Email, Portal, Phone"
                  onChange={(value) =>
                    updateField("ordering_methods_text", value)
                  }
                />

                <TextField
                  label="Order email"
                  value={form.ordering_email}
                  disabled={isSubmitting}
                  onChange={(value) => updateField("ordering_email", value)}
                />

                <TextField
                  label="Portal URL"
                  value={form.ordering_portal_url}
                  disabled={isSubmitting}
                  onChange={(value) =>
                    updateField("ordering_portal_url", value)
                  }
                />

                <TextField
                  label="Phone number"
                  value={form.ordering_phone_number}
                  disabled={isSubmitting}
                  onChange={(value) =>
                    updateField("ordering_phone_number", value)
                  }
                />
              </div>
            </section>

            <section className="modal-section">
              <div className="modal-section-header form-section-header-row">
                <div>
                  <h4>Internal contacts</h4>
                  <p>People or teams used for vendor communication.</p>
                </div>

                <button
                  type="button"
                  onClick={addContact}
                  disabled={isSubmitting}
                >
                  Add contact
                </button>
              </div>

              {form.internal_contacts.length === 0 ? (
                <p className="form-muted">No contacts added.</p>
              ) : (
                <div className="nested-form-list">
                  {form.internal_contacts.map((contact, index) => (
                    <div key={index} className="nested-form-row">
                      <div className="nested-form-row-header">
                        <strong>Contact {index + 1}</strong>

                        <button
                          type="button"
                          onClick={() => removeContact(index)}
                          disabled={isSubmitting}
                        >
                          Remove
                        </button>
                      </div>

                      <div className="form-grid">
                        <TextField
                          label="Name"
                          value={contact.name}
                          disabled={isSubmitting}
                          onChange={(value) =>
                            updateContact(index, "name", value)
                          }
                        />

                        <TextField
                          label="Title"
                          value={contact.title}
                          disabled={isSubmitting}
                          onChange={(value) =>
                            updateContact(index, "title", value)
                          }
                        />

                        <TextField
                          label="Email"
                          value={contact.email}
                          disabled={isSubmitting}
                          onChange={(value) =>
                            updateContact(index, "email", value)
                          }
                        />

                        <TextField
                          label="Phone"
                          value={contact.phone}
                          disabled={isSubmitting}
                          onChange={(value) =>
                            updateContact(index, "phone", value)
                          }
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="modal-section">
              <div className="modal-section-header form-section-header-row">
                <div>
                  <h4>Ordering schedule</h4>
                  <p>Order days, delivery days, and cutoff times.</p>
                </div>

                <button
                  type="button"
                  onClick={addScheduleEntry}
                  disabled={isSubmitting}
                >
                  Add schedule
                </button>
              </div>

              {form.schedule.length === 0 ? (
                <p className="form-muted">No schedule entries added.</p>
              ) : (
                <div className="nested-form-list">
                  {form.schedule.map((entry, index) => (
                    <div key={index} className="nested-form-row">
                      <div className="nested-form-row-header">
                        <strong>Schedule {index + 1}</strong>

                        <button
                          type="button"
                          onClick={() => removeScheduleEntry(index)}
                          disabled={isSubmitting}
                        >
                          Remove
                        </button>
                      </div>

                      <div className="form-grid">
                        <TextField
                          label="Order day"
                          value={entry.order_day}
                          disabled={isSubmitting}
                          placeholder="Monday"
                          onChange={(value) =>
                            updateSchedule(index, "order_day", value)
                          }
                        />

                        <TextField
                          label="Delivery days"
                          value={entry.delivery_days_text}
                          disabled={isSubmitting}
                          placeholder="Tuesday, Thursday"
                          onChange={(value) =>
                            updateSchedule(index, "delivery_days_text", value)
                          }
                        />

                        <TextField
                          label="Cutoff time"
                          value={entry.cutoff_time}
                          disabled={isSubmitting}
                          placeholder="2:00 PM"
                          onChange={(value) =>
                            updateSchedule(index, "cutoff_time", value)
                          }
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="modal-section">
              <details className="store-availability-disclosure">
                <summary className="store-availability-summary">
                  <div>
                    <h4>Store references</h4>
                    <p>
                      {activeStoreReferenceCount} of {stores.length} stores have
                      vendor references
                    </p>
                  </div>

                  <div className="store-availability-summary-meta">
                    <span className="disclosure-caret" aria-hidden="true">
                      ▾
                    </span>
                  </div>
                </summary>

                <div className="store-availability-panel">
                  <p className="form-muted">
                    Add store-specific account numbers or vendor reference names.
                  </p>

                  {stores.length === 0 ? (
                    <p className="form-muted">
                      No stores are available for this scope.
                    </p>
                  ) : (
                    <div className="vendor-store-reference-grid">
                      {form.store_references.map((reference) => {
                        const store = stores.find(
                          (candidate) => candidate.id === reference.store_id,
                        );

                        return (
                          <TextField
                            key={reference.store_id}
                            label={store?.name ?? reference.store_id}
                            value={reference.vendor_store_reference}
                            disabled={isSubmitting}
                            onChange={(value) =>
                              updateStoreReference(reference.store_id, value)
                            }
                          />
                        );
                      })}
                    </div>
                  )}
                </div>
              </details>
            </section>

            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Notes</h4>
                <p>Optional operational notes for this vendor.</p>
              </div>

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
  placeholder?: string;
  onChange: (value: string) => void;
};

function TextField({
  label,
  value,
  required = false,
  disabled = false,
  placeholder,
  onChange,
}: TextFieldProps) {
  return (
    <label className="form-field">
      <span>{label}</span>

      <input
        value={value}
        required={required}
        disabled={disabled}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
      />
    </label>
  );
}

function vendorToFormState(
  vendor: VendorDto | null | undefined,
  stores: StoreDto[],
): VendorFormState {
  const referenceByStoreId = new Map(
    (vendor?.store_references ?? []).map((reference) => [
      reference.store_id,
      reference.vendor_store_reference,
    ]),
  );

  return {
    name: vendor?.name ?? "",
    is_active: vendor?.is_active ?? true,
    order_format: vendor?.order_format ?? "",
    special_notes: vendor?.special_notes ?? "",
    min_order_value: String(vendor?.min_order_value ?? "0"),
    min_order_cases: String(vendor?.min_order_cases ?? 0),
    ordering_methods_text: vendor?.ordering.method.join(", ") ?? "",
    ordering_email: vendor?.ordering.email ?? "",
    ordering_portal_url: vendor?.ordering.portal_url ?? "",
    ordering_phone_number: vendor?.ordering.phone_number ?? "",
    internal_contacts: vendor?.internal_contacts ?? [],
    schedule:
      vendor?.ordering.schedule.map((entry) => ({
        order_day: entry.order_day,
        delivery_days_text: entry.delivery_days.join(", "),
        cutoff_time: entry.cutoff_time,
      })) ?? [],
    store_references: stores.map((store) => ({
      store_id: store.id,
      vendor_store_reference: referenceByStoreId.get(store.id) ?? "",
    })),
  };
}

function formStateToWriteDto(form: VendorFormState): VendorWriteDto {
  return {
    name: form.name.trim(),
    is_active: form.is_active,
    order_format: form.order_format.trim(),
    special_notes: form.special_notes.trim(),
    min_order_value: normalizeDecimalText(form.min_order_value),
    min_order_cases: normalizeIntegerText(form.min_order_cases),
    internal_contacts: form.internal_contacts
      .map((contact) => ({
        name: contact.name.trim(),
        title: contact.title.trim(),
        email: contact.email.trim(),
        phone: contact.phone.trim(),
      }))
      .filter((contact) => contact.name),
    ordering: {
      method: splitList(form.ordering_methods_text),
      email: form.ordering_email.trim(),
      portal_url: form.ordering_portal_url.trim(),
      phone_number: form.ordering_phone_number.trim(),
      schedule: form.schedule
        .map((entry): ScheduleEntryDto => ({
          order_day: entry.order_day.trim(),
          delivery_days: splitList(entry.delivery_days_text),
          cutoff_time: entry.cutoff_time.trim(),
        }))
        .filter((entry) => entry.order_day),
    },
    store_references: form.store_references
      .map((reference) => ({
        store_id: reference.store_id,
        vendor_store_reference: reference.vendor_store_reference.trim(),
      }))
      .filter((reference) => reference.vendor_store_reference),
  };
}

function splitList(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

function normalizeDecimalText(value: string): string {
  const trimmed = value.trim();

  return trimmed ? trimmed : "0";
}

function normalizeIntegerText(value: string): number {
  const parsed = Number.parseInt(value.trim(), 10);

  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}
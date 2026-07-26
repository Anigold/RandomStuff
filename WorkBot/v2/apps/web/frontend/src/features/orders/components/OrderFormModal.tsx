import { useMemo, useState, type FormEvent } from "react";

import type { OrderLineWriteDto, OrderWriteDto } from "../../../api/ordersApi";
import type { StoreDto } from "../../../api/storesApi";
import type { VendorDto } from "../../../api/vendorsApi";
import { useOrderItemOptions } from "../hooks/useOrderItemOptions";
import {
  formatOrderItemOptionLabel,
  getOrderItemOptionKey,
  getOrderItemOptionUnit,
  getOrderItemOptionUnitPrice,
  getOrderItemOptionVendorSku,
  sortOrderItemOptions,
} from "../orderItemOptions";

type OrderFormModalProps = {
  stores: StoreDto[];
  vendors: VendorDto[];
  defaultStoreId: string | null;
  requireStoreSelection: boolean;
  onSubmit: (order: OrderWriteDto) => Promise<void>;
  onClose: () => void;
};

type OrderLineFormState = {
  item_option_key: string;
  item_id: string;
  item_vendor_info_id: string;
  item_name_snapshot: string;
  vendor_sku_snapshot: string;
  unit_price_snapshot: string;
  quantity: string;
  unit: string;
  notes: string;
};

type OrderFormState = {
  store_id: string;
  vendor_id: string;
  order_date: string;
  delivery_date: string;
  notes: string;
  lines: OrderLineFormState[];
};

export function OrderFormModal({
  stores,
  vendors,
  defaultStoreId,
  requireStoreSelection,
  onSubmit,
  onClose,
}: OrderFormModalProps) {
  const [form, setForm] = useState<OrderFormState>(() => ({
    store_id: defaultStoreId ?? "",
    vendor_id: "",
    order_date: getTodayDateInputValue(),
    delivery_date: "",
    notes: "",
    lines: [createEmptyLine()],
  }));

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const activeVendors = useMemo(
    () => vendors.filter((vendor) => vendor.is_active),
    [vendors],
  );

  const {
    itemOptions: loadedItemOptions,
    isLoadingItemOptions,
    itemOptionsErrorMessage,
  } = useOrderItemOptions({
    storeId: form.store_id,
    vendorId: form.vendor_id,
  });

  const itemOptions = useMemo(
    () => sortOrderItemOptions(loadedItemOptions),
    [loadedItemOptions],
  );

  const itemOptionByKey = useMemo(
    () =>
      new Map(
        itemOptions.map((option) => [getOrderItemOptionKey(option), option]),
      ),
    [itemOptions],
  );

  function updateField<K extends keyof OrderFormState>(
    key: K,
    value: OrderFormState[K],
  ) {
    setForm((current) => {
      const next: OrderFormState = {
        ...current,
        [key]: value,
      };

      if (key === "store_id" || key === "vendor_id") {
        next.lines = [createEmptyLine()];
        setErrorMessage(null);
      }

      return next;
    });
  }

  function updateLine(
    index: number,
    key: keyof OrderLineFormState,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      lines: current.lines.map((line, lineIndex) =>
        lineIndex === index
          ? {
              ...line,
              [key]: value,
            }
          : line,
      ),
    }));
  }

  function selectLineItem(index: number, optionKey: string) {
    const option = itemOptionByKey.get(optionKey);

    setForm((current) => ({
      ...current,
      lines: current.lines.map((line, lineIndex) => {
        if (lineIndex !== index) {
          return line;
        }

        if (!option) {
          return createEmptyLine();
        }

        return {
          ...line,
          item_option_key: getOrderItemOptionKey(option),
          item_id: option.item_id,
          item_vendor_info_id: option.item_vendor_info_id,
          item_name_snapshot: option.item_name,
          vendor_sku_snapshot: getOrderItemOptionVendorSku(option),
          unit_price_snapshot: getOrderItemOptionUnitPrice(option) ?? "",
          unit: getOrderItemOptionUnit(option),
        };
      }),
    }));
  }

  function addLine() {
    setForm((current) => ({
      ...current,
      lines: [...current.lines, createEmptyLine()],
    }));
  }

  function removeLine(index: number) {
    setForm((current) => {
      const nextLines = current.lines.filter(
        (_, lineIndex) => lineIndex !== index,
      );

      return {
        ...current,
        lines: nextLines.length ? nextLines : [createEmptyLine()],
      };
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.store_id) {
      setErrorMessage("Store is required.");
      return;
    }

    if (!form.vendor_id) {
      setErrorMessage("Vendor is required.");
      return;
    }

    if (!form.order_date) {
      setErrorMessage("Order date is required.");
      return;
    }

    if (isLoadingItemOptions) {
      setErrorMessage("Orderable items are still loading.");
      return;
    }

    if (itemOptionsErrorMessage) {
      setErrorMessage("Orderable items could not be loaded.");
      return;
    }

    const lines = form.lines
      .map(formLineToWriteDto)
      .filter((line) => line.item_id && line.item_vendor_info_id);

    if (lines.length === 0) {
      setErrorMessage("Add at least one mapped item line.");
      return;
    }

    if (lines.some((line) => !isPositiveDecimalText(line.quantity))) {
      setErrorMessage("Each order line needs a quantity greater than zero.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await onSubmit({
        store_id: form.store_id,
        vendor_id: form.vendor_id,
        order_date: form.order_date,
        delivery_date: emptyToNull(form.delivery_date),
        notes: form.notes.trim(),
        lines,
      });
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to create order.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  const hasSelectedStoreAndVendor = Boolean(form.store_id && form.vendor_id);

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card edit-item-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="order-form-title"
        onClick={(event) => event.stopPropagation()}
      >
        <form className="modal-form" onSubmit={handleSubmit}>
          <header className="modal-header">
            <div className="modal-title-group">
              <span className="modal-eyebrow">Order management</span>

              <div className="modal-title-row">
                <h3 id="order-form-title">New order</h3>

                <span className="status-badge status-badge-active">
                  Pending
                </span>
              </div>

              <p>Create a mapped vendor order for the active operating scope.</p>
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
                <h4>Order information</h4>
                <p>Choose the store, vendor, and order dates.</p>
              </div>

              <div className="form-grid">
                {requireStoreSelection && (
                  <label className="form-field">
                    <span>Store</span>

                    <select
                      value={form.store_id}
                      disabled={isSubmitting}
                      required
                      onChange={(event) =>
                        updateField("store_id", event.target.value)
                      }
                    >
                      <option value="">Select store</option>

                      {stores.map((store) => (
                        <option key={store.id} value={store.id}>
                          {store.name}
                        </option>
                      ))}
                    </select>
                  </label>
                )}

                <label className="form-field">
                  <span>Vendor</span>

                  <select
                    value={form.vendor_id}
                    disabled={isSubmitting}
                    required
                    onChange={(event) =>
                      updateField("vendor_id", event.target.value)
                    }
                  >
                    <option value="">Select vendor</option>

                    {activeVendors.map((vendor) => (
                      <option key={vendor.id} value={vendor.id}>
                        {vendor.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="form-field">
                  <span>Order date</span>

                  <input
                    type="date"
                    value={form.order_date}
                    disabled={isSubmitting}
                    required
                    onChange={(event) =>
                      updateField("order_date", event.target.value)
                    }
                  />
                </label>

                <label className="form-field">
                  <span>Delivery date</span>

                  <input
                    type="date"
                    value={form.delivery_date}
                    disabled={isSubmitting}
                    onChange={(event) =>
                      updateField("delivery_date", event.target.value)
                    }
                  />
                </label>
              </div>
            </section>

            <section className="modal-section">
              <div className="modal-section-header form-section-header-row">
                <div>
                  <h4>Order lines</h4>
                  <p>
                    Add items available to the selected store and mapped to the
                    selected vendor.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={addLine}
                  disabled={
                    isSubmitting ||
                    !hasSelectedStoreAndVendor ||
                    isLoadingItemOptions ||
                    itemOptions.length === 0
                  }
                >
                  Add line
                </button>
              </div>

              {!hasSelectedStoreAndVendor && (
                <div className="empty-card">
                  <strong>Select a store and vendor.</strong>
                  <p>
                    Orderable items will load after both selections are made.
                  </p>
                </div>
              )}

              {hasSelectedStoreAndVendor && isLoadingItemOptions && (
                <div className="empty-card">
                  <strong>Loading orderable items...</strong>
                  <p>Checking store availability and vendor mappings.</p>
                </div>
              )}

              {itemOptionsErrorMessage && (
                <div className="error-card" role="alert">
                  <strong>Unable to load orderable items.</strong>
                  <p>{itemOptionsErrorMessage}</p>
                </div>
              )}

              {hasSelectedStoreAndVendor &&
                !isLoadingItemOptions &&
                !itemOptionsErrorMessage &&
                itemOptions.length === 0 && (
                  <div className="empty-card">
                    <strong>No orderable items found.</strong>
                    <p>
                      This vendor has no active item mappings available to the
                      selected store.
                    </p>
                  </div>
                )}

              <div className="nested-form-list">
                {form.lines.map((line, index) => (
                  <div key={index} className="nested-form-row">
                    <div className="nested-form-row-header">
                      <strong>Line {index + 1}</strong>

                      <button
                        type="button"
                        onClick={() => removeLine(index)}
                        disabled={isSubmitting || form.lines.length === 1}
                      >
                        Remove
                      </button>
                    </div>

                    <div className="form-grid">
                      <label className="form-field form-field-wide">
                        <span>Item</span>

                        <select
                          value={line.item_option_key}
                          disabled={
                            isSubmitting ||
                            !hasSelectedStoreAndVendor ||
                            isLoadingItemOptions ||
                            itemOptions.length === 0
                          }
                          required={index === 0}
                          onChange={(event) =>
                            selectLineItem(index, event.target.value)
                          }
                        >
                          <option value="">
                            {hasSelectedStoreAndVendor
                              ? "Select item"
                              : "Select store and vendor first"}
                          </option>

                          {itemOptions.map((option) => {
                            const optionKey = getOrderItemOptionKey(option);

                            return (
                              <option key={optionKey} value={optionKey}>
                                {formatOrderItemOptionLabel(option)}
                              </option>
                            );
                          })}
                        </select>
                      </label>

                      <TextField
                        label="Vendor SKU"
                        value={line.vendor_sku_snapshot}
                        disabled
                        onChange={() => undefined}
                      />

                      <TextField
                        label="Quantity"
                        value={line.quantity}
                        disabled={isSubmitting}
                        required={index === 0}
                        onChange={(value) =>
                          updateLine(index, "quantity", value)
                        }
                      />

                      <TextField
                        label="Unit"
                        value={line.unit}
                        disabled={isSubmitting}
                        placeholder="case, each, lb..."
                        onChange={(value) => updateLine(index, "unit", value)}
                      />

                      <label className="form-field form-field-wide">
                        <span>Line notes</span>

                        <textarea
                          value={line.notes}
                          disabled={isSubmitting}
                          rows={2}
                          onChange={(event) =>
                            updateLine(index, "notes", event.target.value)
                          }
                        />
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Notes</h4>
                <p>Optional notes for the overall order.</p>
              </div>

              <label className="form-field form-field-wide">
                <span>Order notes</span>

                <textarea
                  value={form.notes}
                  disabled={isSubmitting}
                  rows={4}
                  onChange={(event) => updateField("notes", event.target.value)}
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
              {isSubmitting ? "Creating..." : "Create order"}
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

function createEmptyLine(): OrderLineFormState {
  return {
    item_option_key: "",
    item_id: "",
    item_vendor_info_id: "",
    item_name_snapshot: "",
    vendor_sku_snapshot: "",
    unit_price_snapshot: "",
    quantity: "",
    unit: "",
    notes: "",
  };
}

function formLineToWriteDto(line: OrderLineFormState): OrderLineWriteDto {
  return {
    source_item_name: null,
    source_vendor_sku: null,

    item_id: emptyToNull(line.item_id),
    item_vendor_info_id: emptyToNull(line.item_vendor_info_id),

    item_name_snapshot: emptyToNull(line.item_name_snapshot),
    vendor_sku_snapshot: emptyToNull(line.vendor_sku_snapshot),
    unit_price_snapshot: emptyToNull(line.unit_price_snapshot),

    quantity: normalizeDecimalText(line.quantity),
    unit: emptyToNull(line.unit),

    notes: line.notes.trim(),
  };
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();

  return trimmed ? trimmed : null;
}

function normalizeDecimalText(value: string): string {
  const trimmed = value.trim();

  return trimmed ? trimmed : "0";
}

function isPositiveDecimalText(value: string): boolean {
  const parsedValue = Number(value);

  return Number.isFinite(parsedValue) && parsedValue > 0;
}

function getTodayDateInputValue(): string {
  return new Date().toISOString().slice(0, 10);
}
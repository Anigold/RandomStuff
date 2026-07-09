import { useEffect, useMemo, useState, type FormEvent } from "react";

import {
  addItemStoreInfo,
  deactivateItemStoreInfo,
  getItem,
  updateItem,
  updateItemStoreInfo,
  type ItemDetailDto,
  type ItemDto,
  type ItemStoreInfoDto,
  type ItemWriteDto,
} from "../../../api/itemsApi";
import { listStores, type StoreDto } from "../../../api/storesApi";

type EditItemModalProps = {
  item: ItemDto;
  accessToken: string;
  scopeId: string;
  canManageStoreAvailability: boolean;
  onClose: () => void;
  onSaved: () => Promise<void>;
};

type ItemFormState = {
  name: string;
  category: string;
  subcategory: string;
  count_unit_quantity: string;
  count_unit_measure: string;
  custom_each_name: string;
  each_quantity: string;
  each_measure: string;
  weight_quantity: string;
  weight_measure: string;
  volume_quantity: string;
  volume_measure: string;
  is_active: boolean;
};

export function EditItemModal({
  item,
  accessToken,
  scopeId,
  canManageStoreAvailability,
  onClose,
  onSaved,
}: EditItemModalProps) {
  const [form, setForm] = useState<ItemFormState>(() => itemToFormState(item));
  const [stores, setStores] = useState<StoreDto[]>([]);
  const [itemDetail, setItemDetail] = useState<ItemDetailDto | null>(null);
  const [draftActiveStoreIds, setDraftActiveStoreIds] = useState<Set<string>>(
    () => new Set(),
  );
  const [isLoadingAvailability, setIsLoadingAvailability] = useState(
    canManageStoreAvailability,
  );
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    setForm(itemToFormState(item));
  }, [item]);

  useEffect(() => {
    if (!canManageStoreAvailability) {
      return;
    }

    async function loadAvailability() {
      setIsLoadingAvailability(true);
      setErrorMessage(null);

      try {
        const [loadedStores, loadedItem] = await Promise.all([
          listStores({
            accessToken,
            scopeId,
          }),
          getItem({
            accessToken,
            scopeId,
            itemId: item.id,
          }),
        ]);

        const activeStoreIds = new Set(
          loadedItem.store_info
            .filter((info) => info.is_active)
            .map((info) => info.store_id),
        );

        setStores(loadedStores);
        setItemDetail(loadedItem);
        setDraftActiveStoreIds(activeStoreIds);
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "Unable to load store availability.",
        );
      } finally {
        setIsLoadingAvailability(false);
      }
    }

    void loadAvailability();
  }, [accessToken, scopeId, item.id, canManageStoreAvailability]);

  const storeInfoByStoreId = useMemo(() => {
    const map = new Map<string, ItemStoreInfoDto>();

    for (const info of itemDetail?.store_info ?? []) {
      map.set(info.store_id, info);
    }

    return map;
  }, [itemDetail]);

  const originalActiveStoreIds = useMemo(() => {
    return new Set(
      (itemDetail?.store_info ?? [])
        .filter((info) => info.is_active)
        .map((info) => info.store_id),
    );
  }, [itemDetail]);

  function updateField<K extends keyof ItemFormState>(
    key: K,
    value: ItemFormState[K],
  ) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function toggleStore(storeId: string, checked: boolean) {
    setDraftActiveStoreIds((current) => {
      const next = new Set(current);

      if (checked) {
        next.add(storeId);
      } else {
        next.delete(storeId);
      }

      return next;
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.name.trim()) {
      setErrorMessage("Item name is required.");
      return;
    }

    setIsSaving(true);
    setErrorMessage(null);

    try {
      const itemPayload = formStateToWriteDto(form);

      await updateItem({
        accessToken,
        scopeId,
        itemId: item.id,
        item: itemPayload,
      });

      if (canManageStoreAvailability && itemDetail) {
        await saveAvailabilityChanges({
          accessToken,
          scopeId,
          item,
          originalActiveStoreIds,
          draftActiveStoreIds,
          storeInfoByStoreId,
        });
      }

      await onSaved();
      onClose();
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to save item.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="modal-card edit-item-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-item-title"
        onClick={(event) => event.stopPropagation()}
      >
        <form className="modal-form" onSubmit={handleSubmit}>
          <header className="modal-header">
            <div className="modal-title-group">
              <span className="modal-eyebrow">Edit item</span>

              <div className="modal-title-row">
                <h3 id="edit-item-title">{item.name}</h3>

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

              <p>{formatItemPath(form.category, form.subcategory)}</p>
            </div>

            <button
              type="button"
              className="modal-close-button"
              onClick={onClose}
              aria-label="Close"
              disabled={isSaving}
            >
              ×
            </button>
          </header>

          <div className="modal-body">
            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Basic information</h4>
                <p>Name, classification, and active status.</p>
              </div>

              <div className="form-grid">
                <TextField
                  label="Name"
                  value={form.name}
                  required
                  disabled={isSaving}
                  onChange={(value) => updateField("name", value)}
                />

                <TextField
                  label="Category"
                  value={form.category}
                  disabled={isSaving}
                  onChange={(value) => updateField("category", value)}
                />

                <TextField
                  label="Subcategory"
                  value={form.subcategory}
                  disabled={isSaving}
                  onChange={(value) => updateField("subcategory", value)}
                />
              </div>

              <label className="checkbox-row item-active-row">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  disabled={isSaving}
                  onChange={(event) =>
                    updateField("is_active", event.target.checked)
                  }
                />

                <span>
                  <strong>Active item</strong>
                  <small>
                    Active items are available for normal catalog workflows.
                  </small>
                </span>
              </label>
            </section>

            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Count setup</h4>
                <p>How this item is counted, purchased, or represented.</p>
              </div>

              <div className="form-grid">
                <TextField
                  label="Count unit quantity"
                  value={form.count_unit_quantity}
                  disabled={isSaving}
                  onChange={(value) =>
                    updateField("count_unit_quantity", value)
                  }
                />

                <TextField
                  label="Count unit measure"
                  value={form.count_unit_measure}
                  disabled={isSaving}
                  onChange={(value) =>
                    updateField("count_unit_measure", value)
                  }
                />

                <TextField
                  label="Custom each name"
                  value={form.custom_each_name}
                  disabled={isSaving}
                  onChange={(value) => updateField("custom_each_name", value)}
                />

                <TextField
                  label="Each quantity"
                  value={form.each_quantity}
                  disabled={isSaving}
                  onChange={(value) => updateField("each_quantity", value)}
                />

                <TextField
                  label="Each measure"
                  value={form.each_measure}
                  disabled={isSaving}
                  onChange={(value) => updateField("each_measure", value)}
                />
              </div>
            </section>

            <section className="modal-section">
              <div className="modal-section-header">
                <h4>Measurement references</h4>
                <p>Optional weight and volume references for conversions.</p>
              </div>

              <div className="form-grid">
                <TextField
                  label="Weight quantity"
                  value={form.weight_quantity}
                  disabled={isSaving}
                  onChange={(value) => updateField("weight_quantity", value)}
                />

                <TextField
                  label="Weight measure"
                  value={form.weight_measure}
                  disabled={isSaving}
                  onChange={(value) => updateField("weight_measure", value)}
                />

                <TextField
                  label="Volume quantity"
                  value={form.volume_quantity}
                  disabled={isSaving}
                  onChange={(value) => updateField("volume_quantity", value)}
                />

                <TextField
                  label="Volume measure"
                  value={form.volume_measure}
                  disabled={isSaving}
                  onChange={(value) => updateField("volume_measure", value)}
                />
              </div>
            </section>

            {canManageStoreAvailability && (
              <StoreAvailabilitySection
                stores={stores}
                isLoading={isLoadingAvailability}
                isSaving={isSaving}
                draftActiveStoreIds={draftActiveStoreIds}
                originalActiveStoreIds={originalActiveStoreIds}
                onToggleStore={toggleStore}
              />
            )}

            {errorMessage && (
              <div className="error-card" role="alert">
                {errorMessage}
              </div>
            )}
          </div>

          <footer className="modal-actions">
            <button type="button" onClick={onClose} disabled={isSaving}>
              Cancel
            </button>

            <button type="submit" disabled={isSaving || isLoadingAvailability}>
              {isSaving ? "Saving..." : "Save item"}
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

type StoreAvailabilitySectionProps = {
  stores: StoreDto[];
  isLoading: boolean;
  isSaving: boolean;
  draftActiveStoreIds: Set<string>;
  originalActiveStoreIds: Set<string>;
  onToggleStore: (storeId: string, checked: boolean) => void;
};

function StoreAvailabilitySection({
  stores,
  isLoading,
  isSaving,
  draftActiveStoreIds,
  originalActiveStoreIds,
  onToggleStore,
}: StoreAvailabilitySectionProps) {
  const changedStoreCount = stores.filter((store) => {
    const checked = draftActiveStoreIds.has(store.id);
    const originalChecked = originalActiveStoreIds.has(store.id);

    return checked !== originalChecked;
  }).length;

  const activeStoreCount = stores.filter((store) =>
    draftActiveStoreIds.has(store.id),
  ).length;

  return (
    <section className="modal-section item-availability-section">
      <details className="store-availability-disclosure">
        <summary className="store-availability-summary">
          <div>
            <h4>Store availability</h4>

            <p>
              {isLoading
                ? "Loading store availability..."
                : `${activeStoreCount} of ${stores.length} stores active`}
            </p>
          </div>

          <div className="store-availability-summary-meta">
            {changedStoreCount > 0 && (
              <span className="unsaved-badge">
                {changedStoreCount} unsaved
              </span>
            )}

            <span className="disclosure-caret" aria-hidden="true">
              ▾
            </span>
          </div>
        </summary>

        <div className="store-availability-panel">
          <p className="form-muted">
            Choose which stores can use this item. These changes are saved
            together with the item.
          </p>

          {isLoading ? (
            <p className="form-muted">Loading store availability...</p>
          ) : stores.length === 0 ? (
            <p className="form-muted">No stores are available for this scope.</p>
          ) : (
            <div className="checkbox-list store-availability-list">
              {stores.map((store) => {
                const checked = draftActiveStoreIds.has(store.id);
                const originalChecked = originalActiveStoreIds.has(store.id);
                const changed = checked !== originalChecked;

                return (
                  <label
                    key={store.id}
                    className={
                      changed
                        ? "checkbox-row store-availability-row changed"
                        : "checkbox-row store-availability-row"
                    }
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      disabled={isSaving}
                      onChange={(event) =>
                        onToggleStore(store.id, event.target.checked)
                      }
                    />

                    <span>
                      <strong>{store.name}</strong>

                      {changed && <small>Unsaved</small>}
                    </span>
                  </label>
                );
              })}
            </div>
          )}
        </div>
      </details>
    </section>
  );
}

async function saveAvailabilityChanges({
  accessToken,
  scopeId,
  item,
  originalActiveStoreIds,
  draftActiveStoreIds,
  storeInfoByStoreId,
}: {
  accessToken: string;
  scopeId: string;
  item: ItemDto;
  originalActiveStoreIds: Set<string>;
  draftActiveStoreIds: Set<string>;
  storeInfoByStoreId: Map<string, ItemStoreInfoDto>;
}) {
  const storesToActivate = [...draftActiveStoreIds].filter(
    (storeId) => !originalActiveStoreIds.has(storeId),
  );

  const storesToDeactivate = [...originalActiveStoreIds].filter(
    (storeId) => !draftActiveStoreIds.has(storeId),
  );

  for (const storeId of storesToActivate) {
    const existingInfo = storeInfoByStoreId.get(storeId);

    if (existingInfo) {
      await updateItemStoreInfo({
        accessToken,
        scopeId,
        itemId: item.id,
        infoId: existingInfo.id,
        storeInfo: {
          count_unit: existingInfo.count_unit,
          par: existingInfo.par,
          is_active: true,
        },
      });
    } else {
      await addItemStoreInfo({
        accessToken,
        scopeId,
        itemId: item.id,
        storeInfo: {
          store_id: storeId,
          count_unit: item.count_unit_measure ?? null,
          par: null,
          is_active: true,
        },
      });
    }
  }

  for (const storeId of storesToDeactivate) {
    const existingInfo = storeInfoByStoreId.get(storeId);

    if (!existingInfo) {
      continue;
    }

    await deactivateItemStoreInfo({
      accessToken,
      scopeId,
      itemId: item.id,
      infoId: existingInfo.id,
    });
  }
}

function itemToFormState(item: ItemDto): ItemFormState {
  return {
    name: item.name ?? "",
    category: item.category ?? "",
    subcategory: item.subcategory ?? "",
    count_unit_quantity: item.count_unit_quantity ?? "",
    count_unit_measure: item.count_unit_measure ?? "",
    custom_each_name: item.custom_each_name ?? "",
    each_quantity: item.each_quantity ?? "",
    each_measure: item.each_measure ?? "",
    weight_quantity: item.weight_quantity ?? "",
    weight_measure: item.weight_measure ?? "",
    volume_quantity: item.volume_quantity ?? "",
    volume_measure: item.volume_measure ?? "",
    is_active: item.is_active,
  };
}

function formStateToWriteDto(form: ItemFormState): ItemWriteDto {
  return {
    name: form.name.trim(),
    category: emptyToNull(form.category),
    subcategory: emptyToNull(form.subcategory),
    count_unit_quantity: emptyToNull(form.count_unit_quantity),
    count_unit_measure: emptyToNull(form.count_unit_measure),
    custom_each_name: emptyToNull(form.custom_each_name),
    each_quantity: emptyToNull(form.each_quantity),
    each_measure: emptyToNull(form.each_measure),
    weight_quantity: emptyToNull(form.weight_quantity),
    weight_measure: emptyToNull(form.weight_measure),
    volume_quantity: emptyToNull(form.volume_quantity),
    volume_measure: emptyToNull(form.volume_measure),
    is_active: form.is_active,
  };
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();

  return trimmed ? trimmed : null;
}

function formatItemPath(category: string, subcategory: string): string {
  return [category, subcategory].filter(Boolean).join(" / ") || "Uncategorized item";
}
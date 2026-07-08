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
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="edit-item-title"
        onClick={(event) => event.stopPropagation()}
      >
        <form onSubmit={handleSubmit}>
          <header className="modal-header">
            <div>
              <h3 id="edit-item-title">Edit Item</h3>
              <p>{item.name}</p>
            </div>

            <button type="button" onClick={onClose} aria-label="Close">
              ×
            </button>
          </header>

          <div className="form-grid">
            <label>
              Name
              <input
                value={form.name}
                onChange={(event) => updateField("name", event.target.value)}
                required
              />
            </label>

            <label>
              Category
              <input
                value={form.category}
                onChange={(event) =>
                  updateField("category", event.target.value)
                }
              />
            </label>

            <label>
              Subcategory
              <input
                value={form.subcategory}
                onChange={(event) =>
                  updateField("subcategory", event.target.value)
                }
              />
            </label>

            <label>
              Count unit quantity
              <input
                value={form.count_unit_quantity}
                onChange={(event) =>
                  updateField("count_unit_quantity", event.target.value)
                }
              />
            </label>

            <label>
              Count unit measure
              <input
                value={form.count_unit_measure}
                onChange={(event) =>
                  updateField("count_unit_measure", event.target.value)
                }
              />
            </label>

            <label>
              Custom each name
              <input
                value={form.custom_each_name}
                onChange={(event) =>
                  updateField("custom_each_name", event.target.value)
                }
              />
            </label>

            <label>
              Each quantity
              <input
                value={form.each_quantity}
                onChange={(event) =>
                  updateField("each_quantity", event.target.value)
                }
              />
            </label>

            <label>
              Each measure
              <input
                value={form.each_measure}
                onChange={(event) =>
                  updateField("each_measure", event.target.value)
                }
              />
            </label>

            <label>
              Weight quantity
              <input
                value={form.weight_quantity}
                onChange={(event) =>
                  updateField("weight_quantity", event.target.value)
                }
              />
            </label>

            <label>
              Weight measure
              <input
                value={form.weight_measure}
                onChange={(event) =>
                  updateField("weight_measure", event.target.value)
                }
              />
            </label>

            <label>
              Volume quantity
              <input
                value={form.volume_quantity}
                onChange={(event) =>
                  updateField("volume_quantity", event.target.value)
                }
              />
            </label>

            <label>
              Volume measure
              <input
                value={form.volume_measure}
                onChange={(event) =>
                  updateField("volume_measure", event.target.value)
                }
              />
            </label>
          </div>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(event) =>
                updateField("is_active", event.target.checked)
              }
            />
            Active
          </label>

          {canManageStoreAvailability && (
            <section className="form-section">
              <div>
                <h4>Store Availability</h4>
                <p>
                  Choose which stores can use this item. These changes are saved
                  together with the item.
                </p>
              </div>

              {isLoadingAvailability ? (
                <p>Loading store availability...</p>
              ) : (
                <div className="checkbox-list">
                  {stores.map((store) => {
                    const checked = draftActiveStoreIds.has(store.id);
                    const originalChecked = originalActiveStoreIds.has(store.id);
                    const changed = checked !== originalChecked;

                    return (
                      <label key={store.id} className="checkbox-row">
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={isSaving}
                          onChange={(event) =>
                            toggleStore(store.id, event.target.checked)
                          }
                        />

                        <span>
                          {store.name}
                          {changed ? " — unsaved" : ""}
                        </span>
                      </label>
                    );
                  })}
                </div>
              )}
            </section>
          )}

          {errorMessage && (
            <div className="error-card" role="alert">
              {errorMessage}
            </div>
          )}

          <footer className="modal-actions">
            <button
              type="submit"
              disabled={isSaving || isLoadingAvailability}
            >
              {isSaving ? "Saving..." : "Save item"}
            </button>

            <button type="button" onClick={onClose} disabled={isSaving}>
              Cancel
            </button>
          </footer>
        </form>
      </section>
    </div>
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
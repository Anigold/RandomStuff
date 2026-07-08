import { useState, type FormEvent } from "react";

import type { ItemDto, ItemWriteDto } from "../../../api/itemsApi";

type ItemFormProps = {
  initialItem?: ItemDto | null;
  submitLabel: string;
  onSubmit: (item: ItemWriteDto) => Promise<void>;
  onCancel: () => void;
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

export function ItemForm({
  initialItem,
  submitLabel,
  onSubmit,
  onCancel,
}: ItemFormProps) {
  const [form, setForm] = useState<ItemFormState>(() => ({
    name: initialItem?.name ?? "",
    category: initialItem?.category ?? "",
    subcategory: initialItem?.subcategory ?? "",
    count_unit_quantity: initialItem?.count_unit_quantity ?? "",
    count_unit_measure: initialItem?.count_unit_measure ?? "",
    custom_each_name: initialItem?.custom_each_name ?? "",
    each_quantity: initialItem?.each_quantity ?? "",
    each_measure: initialItem?.each_measure ?? "",
    weight_quantity: initialItem?.weight_quantity ?? "",
    weight_measure: initialItem?.weight_measure ?? "",
    volume_quantity: initialItem?.volume_quantity ?? "",
    volume_measure: initialItem?.volume_measure ?? "",
    is_active: initialItem?.is_active ?? true,
  }));

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function updateField<K extends keyof ItemFormState>(
    key: K,
    value: ItemFormState[K],
  ) {
    setForm((current) => ({
      ...current,
      [key]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!form.name.trim()) {
      setErrorMessage("Item name is required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await onSubmit({
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
      });
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to save item.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
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
            onChange={(event) => updateField("category", event.target.value)}
          />
        </label>

        <label>
          Subcategory
          <input
            value={form.subcategory}
            onChange={(event) => updateField("subcategory", event.target.value)}
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
            onChange={(event) => updateField("each_measure", event.target.value)}
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
          onChange={(event) => updateField("is_active", event.target.checked)}
        />
        Active
      </label>

      {errorMessage && (
        <div className="error-card" role="alert">
          {errorMessage}
        </div>
      )}

      <div className="button-row">
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </button>

        <button type="button" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </button>
      </div>
    </form>
  );
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();

  return trimmed ? trimmed : null;
}
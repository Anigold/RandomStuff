import type { InventoryItemDto } from "../../../api/inventoryApi";
import type { DraftLineState } from "../types";

type InventoryDraftEditorProps = {
  items: InventoryItemDto[];
  activeDraftId: string | null;
  activeDraftStatus: "draft" | "submitted" | null;
  countDate: string;
  notes: string;
  draftLines: Record<string, DraftLineState>;
  isSaving: boolean;
  onCountDateChange: (value: string) => void;
  onNotesChange: (value: string) => void;
  onDraftLineChange: (
    item: InventoryItemDto,
    patch: Partial<DraftLineState>,
  ) => void;
  onSaveDraft: () => void;
  onSubmitDraft: () => void;
};

export function InventoryDraftEditor({
  items,
  activeDraftId,
  activeDraftStatus,
  countDate,
  notes,
  draftLines,
  isSaving,
  onCountDateChange,
  onNotesChange,
  onDraftLineChange,
  onSaveDraft,
  onSubmitDraft,
}: InventoryDraftEditorProps) {
  const isSubmitted = activeDraftStatus === "submitted";

  return (
    <section className="form-card-stack">
      <div className="form-card">
        <h3>{activeDraftId ? "Edit inventory draft" : "New inventory count"}</h3>

        <div className="form-grid">
          <label>
            Count date
            <input
              type="date"
              value={countDate}
              disabled={isSaving || isSubmitted}
              onChange={(event) => onCountDateChange(event.target.value)}
            />
          </label>

          <label>
            Notes
            <input
              type="text"
              value={notes}
              disabled={isSaving || isSubmitted}
              onChange={(event) => onNotesChange(event.target.value)}
              placeholder="Optional notes"
            />
          </label>
        </div>

        {items.length === 0 ? (
          <div className="empty-card">
            <strong>No inventory items found.</strong>
            <p>No active items are available for this store scope.</p>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Category</th>
                <th>Quantity</th>
                <th>Unit</th>
                <th>Notes</th>
              </tr>
            </thead>

            <tbody>
              {items.map((item) => {
                const draftLine = draftLines[item.id];

                return (
                  <tr key={item.id}>
                    <td>{item.name}</td>
                    <td>
                      {[item.category, item.subcategory]
                        .filter(Boolean)
                        .join(" / ")}
                    </td>
                    <td>
                      <input
                        type="number"
                        min="0"
                        step="0.001"
                        value={draftLine?.quantity ?? ""}
                        disabled={isSaving || isSubmitted}
                        onChange={(event) =>
                          onDraftLineChange(item, {
                            quantity: event.target.value,
                          })
                        }
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        value={
                          draftLine?.unit ?? item.count_unit_measure ?? ""
                        }
                        disabled={isSaving || isSubmitted}
                        onChange={(event) =>
                          onDraftLineChange(item, {
                            unit: event.target.value,
                          })
                        }
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        value={draftLine?.notes ?? ""}
                        disabled={isSaving || isSubmitted}
                        onChange={(event) =>
                          onDraftLineChange(item, {
                            notes: event.target.value,
                          })
                        }
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        <div className="button-row">
          <button
            type="button"
            onClick={onSaveDraft}
            disabled={isSaving || isSubmitted}
          >
            {activeDraftId ? "Update draft" : "Save draft"}
          </button>

          <button
            type="button"
            onClick={onSubmitDraft}
            disabled={isSaving || !activeDraftId || isSubmitted}
          >
            Submit count
          </button>
        </div>
      </div>
    </section>
  );
}
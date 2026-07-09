import { useEffect, useMemo, useState } from "react";

import {
  createInventoryCount,
  submitInventoryCount,
  updateInventoryCount,
  type InventoryCountDto,
  type InventoryCountLineWriteDto,
  type InventoryItemDto,
  type InventoryCountWriteDto,
} from "../../../api/inventoryApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";
import { InventoryCountHistory } from "../components/InventoryCountHistory";
import { InventoryDraftEditor } from "../components/InventoryDraftEditor";
import { useInventory } from "../hooks/useInventory";
import type { DraftLineState } from "../types";

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}

export function InventoryPage() {
  const accessToken = useAccessToken();
  const { activeScope, activeScopeId } = useStoreScope();

  const {
    inventoryItems,
    inventoryCounts,
    isLoading,
    errorMessage,
    reloadInventory,
  } = useInventory();

  const [activeDraftId, setActiveDraftId] = useState<string | null>(null);
  const [countDate, setCountDate] = useState(todayIsoDate());
  const [notes, setNotes] = useState("");
  const [draftLines, setDraftLines] = useState<Record<string, DraftLineState>>(
    {},
  );
  const [isSaving, setIsSaving] = useState(false);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(
    null,
  );
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const canCountInventory = activeScope?.type === "store";

  const activeDraft = useMemo(
    () =>
      inventoryCounts.find((count) => count.id === activeDraftId) ?? null,
    [inventoryCounts, activeDraftId],
  );

  useEffect(() => {
    startNewDraft();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeScopeId]);

  function startNewDraft() {
    setActiveDraftId(null);
    setCountDate(todayIsoDate());
    setNotes("");
    setDraftLines({});
    setActionErrorMessage(null);
    setSuccessMessage(null);
  }

  function editDraft(count: InventoryCountDto) {
    const nextDraftLines: Record<string, DraftLineState> = {};

    for (const line of count.lines) {
      nextDraftLines[line.item_id] = {
        itemId: line.item_id,
        quantity: line.quantity,
        unit: line.unit,
        notes: line.notes ?? "",
      };
    }

    setActiveDraftId(count.id);
    setCountDate(count.count_date);
    setNotes(count.notes ?? "");
    setDraftLines(nextDraftLines);
    setActionErrorMessage(null);
    setSuccessMessage(null);
  }

  function updateDraftLine(
    item: InventoryItemDto,
    patch: Partial<DraftLineState>,
  ) {
    setDraftLines((current) => {
      const existing = current[item.id] ?? {
        itemId: item.id,
        quantity: "",
        unit: item.count_unit_measure ?? "",
        notes: "",
      };

      return {
        ...current,
        [item.id]: {
          ...existing,
          ...patch,
        },
      };
    });
  }

  function buildLinesForSave(): InventoryCountLineWriteDto[] {
    return Object.values(draftLines)
      .filter((line) => line.quantity.trim() !== "")
      .map((line) => ({
        item_id: line.itemId,
        quantity: line.quantity.trim(),
        unit: line.unit.trim(),
        notes: line.notes.trim() === "" ? null : line.notes.trim(),
      }));
  }

  function buildCountForSave(): InventoryCountWriteDto | null {
    const lines = buildLinesForSave();

    if (lines.length === 0) {
      setActionErrorMessage(
        "Enter at least one quantity before saving inventory.",
      );
      return null;
    }

    if (lines.some((line) => line.unit.trim() === "")) {
      setActionErrorMessage("Each counted item needs a unit.");
      return null;
    }

    return {
      count_date: countDate,
      notes: notes.trim() === "" ? null : notes.trim(),
      lines,
    };
  }

  async function handleSaveDraft() {
    if (!activeScopeId || !canCountInventory) {
      setActionErrorMessage(
        "Select a store operating scope before saving inventory.",
      );
      return;
    }

    const count = buildCountForSave();

    if (!count) {
      return;
    }

    setIsSaving(true);
    setActionErrorMessage(null);
    setSuccessMessage(null);

    try {
      if (activeDraftId) {
        await updateInventoryCount({
          accessToken,
          scopeId: activeScopeId,
          countId: activeDraftId,
          count,
        });

        setSuccessMessage("Inventory draft updated.");
      } else {
        const created = await createInventoryCount({
          accessToken,
          scopeId: activeScopeId,
          count,
        });

        setActiveDraftId(created.id);
        setSuccessMessage("Inventory draft saved.");
      }

      await reloadInventory();
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to save inventory draft.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSubmitDraft() {
    if (!activeScopeId || !canCountInventory) {
      setActionErrorMessage(
        "Select a store operating scope before submitting inventory.",
      );
      return;
    }

    if (!activeDraftId) {
      setActionErrorMessage("Save a draft before submitting inventory.");
      return;
    }

    const confirmed = window.confirm(
      "Submit this inventory count? Submitted counts cannot be edited.",
    );

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setActionErrorMessage(null);
    setSuccessMessage(null);

    try {
      await submitInventoryCount({
        accessToken,
        scopeId: activeScopeId,
        countId: activeDraftId,
      });

      startNewDraft();
      setSuccessMessage("Inventory count submitted.");
      await reloadInventory();
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to submit inventory count.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <h2>Inventory</h2>

          <p>
            {activeScope
              ? `${activeScope.name} inventory count.`
              : "Select an operating scope to count inventory."}
          </p>
        </div>

        <div className="button-row">
          <button type="button" onClick={() => void reloadInventory()}>
            Refresh
          </button>

          {canCountInventory && (
            <button type="button" onClick={startNewDraft}>
              New Count
            </button>
          )}
        </div>
      </header>

      {!canCountInventory && activeScope && (
        <div className="info-card">
          Inventory counts require a single store operating scope.
        </div>
      )}

      {actionErrorMessage && (
        <div className="error-card" role="alert">
          {actionErrorMessage}
        </div>
      )}

      {successMessage && (
        <div className="info-card" role="status">
          {successMessage}
        </div>
      )}

      {isLoading && <p>Loading inventory...</p>}

      {errorMessage && (
        <div className="error-card" role="alert">
          <strong>Unable to load inventory.</strong>
          <p>{errorMessage}</p>
        </div>
      )}

      {!isLoading && !errorMessage && canCountInventory && (
        <InventoryDraftEditor
          items={inventoryItems}
          activeDraftId={activeDraftId}
          activeDraftStatus={activeDraft?.status ?? null}
          countDate={countDate}
          notes={notes}
          draftLines={draftLines}
          isSaving={isSaving}
          onCountDateChange={setCountDate}
          onNotesChange={setNotes}
          onDraftLineChange={updateDraftLine}
          onSaveDraft={() => void handleSaveDraft()}
          onSubmitDraft={() => void handleSubmitDraft()}
        />
      )}

      {!isLoading && !errorMessage && canCountInventory && (
        <InventoryCountHistory
          counts={inventoryCounts}
          onEditDraft={editDraft}
        />
      )}
    </section>
  );
}
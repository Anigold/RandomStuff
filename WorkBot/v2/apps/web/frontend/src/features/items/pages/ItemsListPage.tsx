import { useState } from "react";

import {
  createItem,
  deactivateItem,
  updateItem,
  type ItemDto,
  type ItemWriteDto,
} from "../../../api/itemsApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";
import { ItemActionsModal } from "../components/ItemActionsModal";
import { EditItemModal } from "../components/EditItemModal";


import { ItemForm } from "../components/ItemForm";
import { ItemsTable } from "../components/ItemsTable";
import { useItems } from "../hooks/useItems";

type FormMode =
  | { type: "closed" }
  | { type: "create" }
  | { type: "edit"; item: ItemDto };

export function ItemsListPage() {
  const accessToken = useAccessToken();
  const { activeScope, activeScopeId } = useStoreScope();
  const { items, isLoading, errorMessage, reloadItems } = useItems();

  const [editingItem, setEditingItem] = useState<ItemDto | null>(null);
  const [formMode, setFormMode] = useState<FormMode>({ type: "closed" });
  const [selectedItem, setSelectedItem] = useState<ItemDto | null>(null);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(
    null,
  );

  const canManageItems = activeScope?.type === "supervisor";

  async function handleCreateItem(item: ItemWriteDto) {
    if (!activeScopeId) {
      setActionErrorMessage("Select an operating scope before creating items.");
      return;
    }

    await createItem({
      accessToken,
      scopeId: activeScopeId,
      item,
    });

    setFormMode({ type: "closed" });
    await reloadItems();
  }

  async function handleUpdateItem(item: ItemWriteDto) {
    if (!activeScopeId) {
      setActionErrorMessage("Select an operating scope before updating items.");
      return;
    }

    if (formMode.type !== "edit") {
      return;
    }

    await updateItem({
      accessToken,
      scopeId: activeScopeId,
      itemId: formMode.item.id,
      item,
    });

    setFormMode({ type: "closed" });
    setSelectedItem(null);
    await reloadItems();
  }

  async function handleDeactivateItem(item: ItemDto) {
    if (!activeScopeId) {
      setActionErrorMessage(
        "Select an operating scope before marking items inactive.",
      );
      return;
    }

    const confirmed = window.confirm(
      `Mark "${item.name}" as inactive? This will not permanently delete it.`,
    );

    if (!confirmed) {
      return;
    }

    setActionErrorMessage(null);

    try {
      await deactivateItem({
        accessToken,
        scopeId: activeScopeId,
        itemId: item.id,
      });

      setSelectedItem(null);
      await reloadItems();
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to mark item inactive.",
      );
    }
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <h2>
            {activeScope?.type === "supervisor"
              ? "Item Catalog"
              : "Store Items"}
          </h2>

          <p>
            {activeScope
              ? `${activeScope.name} item view.`
              : "Select an operating scope to view items."}
          </p>
        </div>

        <div className="button-row">
          <button type="button" onClick={() => void reloadItems()}>
            Refresh
          </button>

          {canManageItems && formMode.type === "closed" && (
            <button
              type="button"
              onClick={() => {
                setActionErrorMessage(null);
                setSelectedItem(null);
                setFormMode({ type: "create" });
              }}
            >
              New Item
            </button>
          )}
        </div>
      </header>

      {!canManageItems && activeScope && (
        <div className="info-card">
          Item catalog management is available from the Supervisor operating
          scope.
        </div>
      )}

      {actionErrorMessage && (
        <div className="error-card" role="alert">
          {actionErrorMessage}
        </div>
      )}

      {formMode.type === "create" && (
        <ItemForm
          submitLabel="Create item"
          onSubmit={handleCreateItem}
          onCancel={() => setFormMode({ type: "closed" })}
        />
      )}

      {formMode.type === "edit" && (
        <div className="form-card-stack">
          <ItemForm
            initialItem={formMode.item}
            submitLabel="Save item"
            onSubmit={handleUpdateItem}
            onCancel={() => setFormMode({ type: "closed" })}
          />
        </div>
      )}

      {isLoading && <p>Loading items...</p>}

      {errorMessage && (
        <div className="error-card" role="alert">
          <strong>Unable to load items.</strong>
          <p>{errorMessage}</p>
        </div>
      )}

      {!isLoading && !errorMessage && items.length === 0 && (
        <div className="empty-card">
          <strong>No items found.</strong>
          <p>No items are available for this operating scope.</p>
        </div>
      )}

      {!isLoading && !errorMessage && items.length > 0 && (
        <ItemsTable
          items={items}
          onSelectItem={(item) => {
            setActionErrorMessage(null);
            setSelectedItem(item);
          }}
        />
      )}

      {editingItem && activeScopeId && (
        <EditItemModal
          item={editingItem}
          accessToken={accessToken}
          scopeId={activeScopeId}
          canManageStoreAvailability={canManageItems}
          onClose={() => setEditingItem(null)}
          onSaved={reloadItems}
        />
      )}
      {selectedItem && formMode.type === "closed" && (
        <ItemActionsModal
          item={selectedItem}
          canManageItems={canManageItems}
          onClose={() => setSelectedItem(null)}
          onEdit={(item) => {
            setSelectedItem(null);
            setEditingItem(item);
          }}
          onDeactivate={(item) => void handleDeactivateItem(item)}
        />
      )}
    </section>
  );
}
import { useState } from "react";

import {
  createStore,
  deleteStore,
  updateStore,
  type StoreDto,
  type StoreWriteDto,
} from "../../../api/storesApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../hooks/useStoreScope";
import { StoreActionsModal } from "../components/StoreActionsModal";
import { StoreFormModal } from "../components/StoreFormModal";
import { StoresTable } from "../components/StoresTable";
import { useStoresManagement } from "../hooks/useStoresManagement";

type FormMode =
  | { type: "closed" }
  | { type: "create" }
  | { type: "edit"; store: StoreDto };

export function StoresManagementPage() {
  const accessToken = useAccessToken();
  const { activeScopeId } = useStoreScope();
  const {
    stores,
    isLoadingStores,
    storeErrorMessage,
    canManageStores,
    reloadStores,
  } = useStoresManagement();

  const [formMode, setFormMode] = useState<FormMode>({ type: "closed" });
  const [selectedStore, setSelectedStore] = useState<StoreDto | null>(null);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(
    null,
  );

  async function handleCreateStore(store: StoreWriteDto) {
    if (!activeScopeId) {
      throw new Error("Select a supervisor scope before creating a store.");
    }

    await createStore({
      accessToken,
      scopeId: activeScopeId,
      store,
    });

    await reloadStores();
    setFormMode({ type: "closed" });
  }

  async function handleUpdateStore(store: StoreWriteDto) {
    if (!activeScopeId) {
      throw new Error("Select a supervisor scope before updating a store.");
    }

    if (formMode.type !== "edit") {
      throw new Error("No store is selected for editing.");
    }

    await updateStore({
      accessToken,
      scopeId: activeScopeId,
      storeId: formMode.store.id,
      store,
    });

    await reloadStores();
    setSelectedStore(null);
    setFormMode({ type: "closed" });
  }

  async function handleDeactivateStore(store: StoreDto) {
    if (!activeScopeId) {
      setActionErrorMessage(
        "Select a supervisor scope before deactivating a store.",
      );
      return;
    }

    const confirmed = window.confirm(
      `Deactivate ${store.name}? This will hide it from normal store workflows but preserve historical records.`,
    );

    if (!confirmed) {
      return;
    }

    setActionErrorMessage(null);

    try {
      await deleteStore({
        accessToken,
        scopeId: activeScopeId,
        storeId: store.id,
      });

      await reloadStores();
      setSelectedStore(null);
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error ? error.message : "Unable to deactivate store.",
      );
    }
  }

  if (!canManageStores) {
    return (
      <section className="page-stack">
        <header className="page-header">
          <div>
            <h2>Stores</h2>
            <p>Manage store records and operating information.</p>
          </div>
        </header>

        <div className="info-card">
          <strong>Supervisor scope required.</strong>
          <p>
            Switch to the supervisor operating scope to manage stores.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <h2>Stores</h2>
          <p>Manage store records and operating information.</p>
        </div>

        <button
          type="button"
          onClick={() => {
            setActionErrorMessage(null);
            setSelectedStore(null);
            setFormMode({ type: "create" });
          }}
        >
          Add store
        </button>
      </header>

      {actionErrorMessage && (
        <div className="error-card" role="alert">
          {actionErrorMessage}
        </div>
      )}

      {isLoadingStores && <p>Loading stores...</p>}

      {storeErrorMessage && (
        <div className="error-card" role="alert">
          <strong>Unable to load stores.</strong>
          <p>{storeErrorMessage}</p>
        </div>
      )}

      {!isLoadingStores && !storeErrorMessage && stores.length === 0 && (
        <div className="empty-card">
          <strong>No stores found.</strong>
          <p>Add the first store to begin managing store data.</p>
        </div>
      )}

      {!isLoadingStores && !storeErrorMessage && stores.length > 0 && (
        <StoresTable
          stores={stores}
          onSelectStore={(store) => {
            setActionErrorMessage(null);
            setSelectedStore(store);
            setFormMode({ type: "closed" });
          }}
        />
      )}

      {selectedStore && formMode.type === "closed" && (
        <StoreActionsModal
          store={selectedStore}
          onClose={() => setSelectedStore(null)}
          onEdit={(store) => {
            setSelectedStore(null);
            setFormMode({ type: "edit", store });
          }}
          onDeactivate={handleDeactivateStore}
        />
      )}

      {formMode.type === "create" && (
        <StoreFormModal
          title="Add store"
          submitLabel="Create store"
          onSubmit={handleCreateStore}
          onClose={() => setFormMode({ type: "closed" })}
        />
      )}

      {formMode.type === "edit" && (
        <StoreFormModal
          initialStore={formMode.store}
          title="Edit store"
          submitLabel="Save store"
          onSubmit={handleUpdateStore}
          onClose={() => setFormMode({ type: "closed" })}
        />
      )}
    </section>
  );
}
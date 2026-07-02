import { useStoreScope } from "../hooks/useStoreScope";

export function StoreSelector() {
  const {
    stores,
    activeStoreId,
    isLoadingStores,
    storeErrorMessage,
    setActiveStoreId,
  } = useStoreScope();

  if (isLoadingStores) {
    return <p className="sidebar-muted">Loading stores...</p>;
  }

  if (storeErrorMessage) {
    return <p className="sidebar-error">Unable to load stores.</p>;
  }

  if (stores.length === 0) {
    return <p className="sidebar-muted">No stores available.</p>;
  }

  return (
    <label className="store-selector">
      Store
      <select
        value={activeStoreId ?? ""}
        onChange={(event) => setActiveStoreId(event.target.value)}
      >
        {stores.map((store) => (
          <option key={store.id} value={store.id}>
            {store.name}
          </option>
        ))}
      </select>
    </label>
  );
}
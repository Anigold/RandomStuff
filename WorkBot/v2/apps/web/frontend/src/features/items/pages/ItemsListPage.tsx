import { ItemsTable } from "../components/ItemsTable";
import { useItems } from "../hooks/useItems";

export function ItemsListPage() {
  const { items, isLoading, errorMessage, reloadItems } = useItems();

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <h2>Items</h2>
          <p>View the current item catalog.</p>
        </div>

        <button type="button" onClick={() => void reloadItems()}>
          Refresh
        </button>
      </header>

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
          <p>The item catalog is empty.</p>
        </div>
      )}

      {!isLoading && !errorMessage && items.length > 0 && (
        <ItemsTable items={items} />
      )}
    </section>
  );
}
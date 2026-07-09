import type { StoreDto } from "../../../api/storesApi";

type StoresTableProps = {
  stores: StoreDto[];
  onSelectStore: (store: StoreDto) => void;
};

export function StoresTable({ stores, onSelectStore }: StoresTableProps) {
  return (
    <div className="table-card">
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>General Manager</th>
            <th>Inventory Clerk</th>
            <th>Phone</th>
          </tr>
        </thead>

        <tbody>
          {stores.map((store) => (
            <tr
              key={store.id}
              className="clickable-row"
              tabIndex={0}
              role="button"
              onClick={() => onSelectStore(store)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onSelectStore(store);
                }
              }}
            >
              <td>
                <strong>{store.name}</strong>
              </td>

              <td>
                <span
                  className={
                    store.is_active
                      ? "status-badge status-badge-active"
                      : "status-badge status-badge-inactive"
                  }
                >
                  {store.is_active ? "Active" : "Inactive"}
                </span>
              </td>

              <td>{store.general_manager || "—"}</td>
              <td>{store.inventory_clerk || "—"}</td>
              <td>{store.phone_number || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
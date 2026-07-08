import type { ItemDto } from "../../../api/itemsApi";

type ItemsTableProps = {
  items: ItemDto[];
  onSelectItem: (item: ItemDto) => void;
};

export function ItemsTable({ items, onSelectItem }: ItemsTableProps) {
  return (
    <div className="table-card">
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Subcategory</th>
            <th>Count Unit</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {items.map((item) => (
            <tr
              key={item.id}
              className="clickable-row"
              tabIndex={0}
              onClick={() => onSelectItem(item)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onSelectItem(item);
                }
              }}
            >
              <td>
                <strong>{item.name}</strong>
              </td>
              <td>{item.category ?? "—"}</td>
              <td>{item.subcategory ?? "—"}</td>
              <td>{formatCountUnit(item)}</td>
              <td>{item.is_active ? "Active" : "Inactive"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCountUnit(item: ItemDto): string {
  const parts = [
    item.count_unit_quantity,
    item.count_unit_measure,
  ].filter(Boolean);

  return parts.length ? parts.join(" ") : "—";
}
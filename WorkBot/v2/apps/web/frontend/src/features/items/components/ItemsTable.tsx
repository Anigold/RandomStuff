import type { ItemDto } from "../../../api/itemsApi";

type ItemsTableProps = {
  items: ItemDto[];
};

function formatUnitQuantity(item: ItemDto): string {
  const quantity = item.count_unit_quantity;
  const measure = item.count_unit_measure;

  if (!quantity && !measure) {
    return "—";
  }

  return [quantity, measure].filter(Boolean).join(" ");
}

export function ItemsTable({ items }: ItemsTableProps) {
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
            <tr key={item.id}>
              <td>
                <strong>{item.name}</strong>
              </td>
              <td>{item.category ?? "—"}</td>
              <td>{item.subcategory ?? "—"}</td>
              <td>{formatUnitQuantity(item)}</td>
              <td>{item.is_active ? "Active" : "Inactive"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
import type { VendorDto } from "../../../api/vendorsApi";

type VendorsTableProps = {
  vendors: VendorDto[];
  onSelectVendor: (vendor: VendorDto) => void;
};

export function VendorsTable({ vendors, onSelectVendor }: VendorsTableProps) {
  return (
    <div className="table-card">
      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Order Methods</th>
            <th>Order Email</th>
            <th>Minimum</th>
          </tr>
        </thead>

        <tbody>
          {vendors.map((vendor) => (
            <tr
              key={vendor.id}
              className="clickable-row"
              tabIndex={0}
              role="button"
              onClick={() => onSelectVendor(vendor)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  onSelectVendor(vendor);
                }
              }}
            >
              <td>
                <strong>{vendor.name}</strong>
              </td>

              <td>
                <span
                  className={
                    vendor.is_active
                      ? "status-badge status-badge-active"
                      : "status-badge status-badge-inactive"
                  }
                >
                  {vendor.is_active ? "Active" : "Inactive"}
                </span>
              </td>

              <td>{formatList(vendor.ordering.method)}</td>
              <td>{vendor.ordering.email || "—"}</td>
              <td>{formatMinimum(vendor)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatList(values: string[]): string {
  return values.length ? values.join(", ") : "—";
}

function formatMinimum(vendor: VendorDto): string {
  const parts: string[] = [];

  const minOrderValue = String(vendor.min_order_value ?? "0");

  if (minOrderValue !== "0" && minOrderValue !== "0.00") {
    parts.push(`$${minOrderValue}`);
  }

  if (vendor.min_order_cases > 0) {
    parts.push(`${vendor.min_order_cases} cases`);
  }

  return parts.length ? parts.join(" / ") : "—";
}
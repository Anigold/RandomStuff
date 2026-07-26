import {
  formatStatusLabel,
  getOrdersResultSummary,
  type OrderStatusFilter,
} from "../orderTableHelpers";

type OrdersTableToolbarProps = {
  orderCount: number;
  visibleOrderCount: number;
  searchText: string;
  statusFilter: OrderStatusFilter;
  availableStatuses: string[];
  onSearchTextChange: (value: string) => void;
  onStatusFilterChange: (value: OrderStatusFilter) => void;
  onClearFilters: () => void;
};

export function OrdersTableToolbar({
  orderCount,
  visibleOrderCount,
  searchText,
  statusFilter,
  availableStatuses,
  onSearchTextChange,
  onStatusFilterChange,
  onClearFilters,
}: OrdersTableToolbarProps) {
  const hasActiveFilters = searchText.trim() !== "" || statusFilter !== "open";

  return (
    <div className="table-toolbar orders-table-toolbar">
      <div className="table-toolbar-main">
        <div className="table-search-box">
          <span className="table-search-icon" aria-hidden="true">
            ⌕
          </span>

          <input
            type="search"
            aria-label="Search orders"
            value={searchText}
            onChange={(event) => onSearchTextChange(event.target.value)}
            placeholder="Search orders..."
          />
        </div>

        <div className="table-result-summary">
          {getOrdersResultSummary({
            visibleCount: visibleOrderCount,
            totalCount: orderCount,
            statusFilter,
          })}
        </div>
      </div>

      <div className="table-filter-row">
        <label className="table-filter-control">
          <span>Status</span>

          <select
            value={statusFilter}
            onChange={(event) =>
              onStatusFilterChange(event.target.value as OrderStatusFilter)
            }
          >
            <option value="open">Open</option>
            <option value="all">All</option>

            {availableStatuses.map((status) => (
              <option key={status} value={status}>
                {formatStatusLabel(status)}
              </option>
            ))}
          </select>
        </label>

        {hasActiveFilters && (
          <button
            type="button"
            className="table-clear-button"
            onClick={onClearFilters}
          >
            Reset
          </button>
        )}
      </div>
    </div>
  );
}
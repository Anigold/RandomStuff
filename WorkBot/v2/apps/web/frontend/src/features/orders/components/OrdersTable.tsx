import type { OrderDto } from "../../../api/ordersApi";
import {
  formatOrderStatus,
  getOrderLineCount,
  getOrderStatusBadgeClass,
} from "../orderHelpers";
import {
  formatOrderDateForTable,
  getOrderSortLabel,
  type OrderSortKey,
} from "../orderTableHelpers";
import { useOrdersTable } from "../hooks/useOrdersTable";
import { OrdersTableToolbar } from "./OrdersTableToolbar";

type OrdersTableProps = {
  orders: OrderDto[];
  onSelectOrder: (order: OrderDto) => void;
};

export function OrdersTable({ orders, onSelectOrder }: OrdersTableProps) {
  const {
    visibleOrders,
    searchText,
    statusFilter,
    sortState,
    availableStatuses,
    setSearchText,
    setStatusFilter,
    updateSort,
    clearFilters,
  } = useOrdersTable(orders);

  return (
    <div className="table-card">
      <OrdersTableToolbar
        orderCount={orders.length}
        visibleOrderCount={visibleOrders.length}
        searchText={searchText}
        statusFilter={statusFilter}
        availableStatuses={availableStatuses}
        onSearchTextChange={setSearchText}
        onStatusFilterChange={setStatusFilter}
        onClearFilters={clearFilters}
      />

      {visibleOrders.length === 0 ? (
        <div className="empty-card">
          <strong>No matching orders found.</strong>
          <p>Try changing the search or status filter.</p>
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <SortableHeader
                label="Order Date"
                sortKey="orderDate"
                sortState={sortState}
                onUpdateSort={updateSort}
              />

              <SortableHeader
                label="Vendor"
                sortKey="vendor"
                sortState={sortState}
                onUpdateSort={updateSort}
              />

              <SortableHeader
                label="Store"
                sortKey="store"
                sortState={sortState}
                onUpdateSort={updateSort}
              />

              <SortableHeader
                label="Status"
                sortKey="status"
                sortState={sortState}
                onUpdateSort={updateSort}
              />

              <SortableHeader
                label="Lines"
                sortKey="lineCount"
                sortState={sortState}
                onUpdateSort={updateSort}
              />
            </tr>
          </thead>

          <tbody>
            {visibleOrders.map((order) => (
              <tr
                key={order.id}
                className="clickable-row"
                tabIndex={0}
                role="button"
                onClick={() => onSelectOrder(order)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onSelectOrder(order);
                  }
                }}
              >
                <td>
                  <strong>{formatOrderDateForTable(order)}</strong>
                </td>

                <td>{order.vendor_name || order.vendor_id || "—"}</td>
                <td>{order.store_name || order.store_id || "—"}</td>

                <td>
                  <span className={getOrderStatusBadgeClass(order.status)}>
                    {formatOrderStatus(order.status)}
                  </span>
                </td>

                <td>{getOrderLineCount(order)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

type SortableHeaderProps = {
  label: string;
  sortKey: OrderSortKey;
  sortState: {
    key: OrderSortKey;
    direction: "asc" | "desc";
  };
  onUpdateSort: (key: OrderSortKey) => void;
};

function SortableHeader({
  label,
  sortKey,
  sortState,
  onUpdateSort,
}: SortableHeaderProps) {
  return (
    <th>
      <button
        type="button"
        className="table-sort-button"
        onClick={() => onUpdateSort(sortKey)}
      >
        {label}
        {getOrderSortLabel(sortKey, sortState)}
      </button>
    </th>
  );
}
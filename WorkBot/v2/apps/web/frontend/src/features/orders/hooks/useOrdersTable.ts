import { useCallback, useMemo, useState } from "react";

import type { OrderDto } from "../../../api/ordersApi";
import {
  getUniqueOrderStatuses,
  orderMatchesSearch,
  orderMatchesStatusFilter,
  sortOrders,
  type OrderSortKey,
  type OrderSortState,
  type OrderStatusFilter,
} from "../orderTableHelpers";

type UseOrdersTableResult = {
  visibleOrders: OrderDto[];
  searchText: string;
  statusFilter: OrderStatusFilter;
  sortState: OrderSortState;
  availableStatuses: string[];
  setSearchText: (value: string) => void;
  setStatusFilter: (value: OrderStatusFilter) => void;
  updateSort: (key: OrderSortKey) => void;
  clearFilters: () => void;
};

export function useOrdersTable(orders: OrderDto[]): UseOrdersTableResult {
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<OrderStatusFilter>("open");
  const [sortState, setSortState] = useState<OrderSortState>({
    key: "orderDate",
    direction: "desc",
  });

  const availableStatuses = useMemo(
    () => getUniqueOrderStatuses(orders),
    [orders],
  );

  const visibleOrders = useMemo(() => {
    const filteredOrders = orders.filter((order) => {
      const matchesSearch = orderMatchesSearch(order, searchText);
      const matchesStatus = orderMatchesStatusFilter(order, statusFilter);

      return matchesSearch && matchesStatus;
    });

    return sortOrders(filteredOrders, sortState);
  }, [orders, searchText, statusFilter, sortState]);

  const updateSort = useCallback((key: OrderSortKey) => {
    setSortState((current) => {
      if (current.key !== key) {
        return {
          key,
          direction: key === "orderDate" ? "desc" : "asc",
        };
      }

      return {
        key,
        direction: current.direction === "asc" ? "desc" : "asc",
      };
    });
  }, []);

  const clearFilters = useCallback(() => {
    setSearchText("");
    setStatusFilter("open");
  }, []);

  return {
    visibleOrders,
    searchText,
    statusFilter,
    sortState,
    availableStatuses,
    setSearchText,
    setStatusFilter,
    updateSort,
    clearFilters,
  };
}
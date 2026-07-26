import type { OrderDto } from "../../api/ordersApi";
import { formatDate, getOrderLineCount } from "./orderHelpers";

export type OrderSortKey =
  | "orderDate"
  | "vendor"
  | "store"
  | "status"
  | "lineCount";

export type OrderSortDirection = "asc" | "desc";

export type OrderSortState = {
  key: OrderSortKey;
  direction: OrderSortDirection;
};

export type OrderStatusFilter =
  | "open"
  | "all"
  | "pending"
  | "created"
  | "cancelled"
  | "canceled"
  | "fulfilled";

const OPEN_ORDER_STATUSES = new Set(["pending", "created"]);

export function normalizeOrderValue(value: unknown): string {
  return String(value ?? "").trim().toLowerCase();
}

function normalizeSearchValue(value: unknown): string {
  return normalizeOrderValue(value)
    .replace(/[^a-z0-9%]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function getSearchTokens(value: unknown): string[] {
  return Array.from(
    new Set(
      normalizeSearchValue(value)
        .split(" ")
        .map((token) => token.trim())
        .filter(Boolean),
    ),
  );
}

function getOrderSearchText(order: OrderDto): string {
  return [
    order.id,
    order.store_id,
    order.store_name,
    order.vendor_id,
    order.vendor_name,
    order.order_date,
    order.delivery_date,
    order.status,
    order.source,
    order.source_reference,
    getOrderLineCount(order),
  ]
    .map(normalizeSearchValue)
    .join(" ");
}

export function orderMatchesSearch(order: OrderDto, searchText: string): boolean {
  const searchTokens = getSearchTokens(searchText);

  if (searchTokens.length === 0) {
    return true;
  }

  const orderSearchText = getOrderSearchText(order);

  return searchTokens.every((token) => orderSearchText.includes(token));
}

export function orderMatchesStatusFilter(
  order: OrderDto,
  statusFilter: OrderStatusFilter,
): boolean {
  const status = normalizeOrderValue(order.status);

  if (statusFilter === "all") {
    return true;
  }

  if (statusFilter === "open") {
    return OPEN_ORDER_STATUSES.has(status);
  }

  return status === statusFilter;
}

export function getUniqueOrderStatuses(orders: OrderDto[]): string[] {
  return Array.from(
    new Set(
      orders
        .map((order) => normalizeOrderValue(order.status))
        .filter(Boolean),
    ),
  ).sort((left, right) => left.localeCompare(right));
}

export function getOrderStatusFilterLabel(statusFilter: string): string {
  switch (statusFilter) {
    case "open":
      return "Open";
    case "all":
      return "All";
    default:
      return formatStatusLabel(statusFilter);
  }
}

export function formatStatusLabel(status: string): string {
  return status
    .split("_")
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

export function getOrderSortLabel(
  key: OrderSortKey,
  sortState: OrderSortState,
): string {
  if (sortState.key !== key) {
    return "";
  }

  return sortState.direction === "asc" ? " ↑" : " ↓";
}

export function sortOrders(
  orders: OrderDto[],
  sortState: OrderSortState,
): OrderDto[] {
  return [...orders].sort((left, right) => {
    let result = 0;

    switch (sortState.key) {
      case "orderDate":
        result = compareDate(left.order_date, right.order_date);
        break;

      case "vendor":
        result = compareText(left.vendor_name ?? left.vendor_id, right.vendor_name ?? right.vendor_id);
        break;

      case "store":
        result = compareText(left.store_name ?? left.store_id, right.store_name ?? right.store_id);
        break;

      case "status":
        result = compareText(left.status, right.status);
        break;

      case "lineCount":
        result = getOrderLineCount(left) - getOrderLineCount(right);
        break;
    }

    return sortState.direction === "asc" ? result : -result;
  });
}

function compareText(
  left: string | null | undefined,
  right: string | null | undefined,
): number {
  return normalizeOrderValue(left).localeCompare(normalizeOrderValue(right));
}

function compareDate(
  left: string | null | undefined,
  right: string | null | undefined,
): number {
  const leftTime = left ? new Date(left).getTime() : 0;
  const rightTime = right ? new Date(right).getTime() : 0;

  return leftTime - rightTime;
}

export function getOrdersResultSummary({
  visibleCount,
  totalCount,
  statusFilter,
}: {
  visibleCount: number;
  totalCount: number;
  statusFilter: OrderStatusFilter;
}): string {
  const statusLabel = getOrderStatusFilterLabel(statusFilter);

  return `${statusLabel}: ${visibleCount} of ${totalCount}`;
}

export function formatOrderDateForTable(order: OrderDto): string {
  return formatDate(order.order_date);
}
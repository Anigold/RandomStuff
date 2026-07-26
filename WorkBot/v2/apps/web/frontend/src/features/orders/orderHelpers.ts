import type { OrderDto, OrderLineDto } from "../../api/ordersApi";

export function formatOrderTitle(order: OrderDto): string {
  const vendorName = order.vendor_name || "Unknown vendor";
  const date = formatDate(order.order_date);

  return `${vendorName} · ${date}`;
}

export function formatDate(value?: string | null): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString();
}

export function formatDateTime(value?: string | null): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export function formatOrderStatus(status: string): string {
  return status
    .split("_")
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join(" ");
}

export function getOrderStatusBadgeClass(status: string): string {
  const normalizedStatus = status.trim().toLowerCase();

  if (
    normalizedStatus === "cancelled" ||
    normalizedStatus === "canceled" ||
    normalizedStatus === "inactive"
  ) {
    return "status-badge status-badge-inactive";
  }

  return "status-badge status-badge-active";
}

export function getOrderLineCount(order: OrderDto): number {
  if ("lines" in order) {
    return order.lines.length;
  }

  return order.line_count;
}

export function getOrderLines(order: OrderDto): OrderLineDto[] {
  if ("lines" in order) {
    return order.lines;
  }

  return [];
}

export function formatOrderLineQuantity(line: OrderLineDto): string {
  const quantity = line.quantity == null ? "" : String(line.quantity);
  const unit = line.unit ?? "";

  return [quantity, unit].filter(Boolean).join(" ") || "—";
}

export function getOrderLineName(line: OrderLineDto): string {
  return (
    line.item_name_snapshot ||
    line.source_item_name ||
    line.item_id ||
    "Unknown item"
  );
}

export function canCancelOrder(order: OrderDto): boolean {
  const status = order.status.trim().toLowerCase();

  return status !== "cancelled" && status !== "canceled" && status !== "fulfilled";
}
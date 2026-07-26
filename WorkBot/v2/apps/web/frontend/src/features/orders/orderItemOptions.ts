import type { OrderItemOptionDto } from "../../api/itemsApi";

export type OrderItemOption = OrderItemOptionDto;

export function getOrderItemOptionKey(option: OrderItemOption): string {
  return `${option.item_id}:${option.item_vendor_info_id}`;
}

export function sortOrderItemOptions(
  options: OrderItemOption[],
): OrderItemOption[] {
  return [...options].sort((left, right) =>
    left.item_name.localeCompare(right.item_name),
  );
}

export function formatOrderItemOptionLabel(option: OrderItemOption): string {
  const details = [
    option.vendor_sku ? `SKU ${option.vendor_sku}` : null,
    option.purchase_unit ? `Unit ${option.purchase_unit}` : null,
    option.price != null ? `$${String(option.price)}` : null,
  ].filter(Boolean);

  return details.length
    ? `${option.item_name} — ${details.join(" · ")}`
    : option.item_name;
}

export function getOrderItemOptionUnit(option: OrderItemOption): string {
  return (
    option.purchase_unit ??
    option.store_count_unit ??
    option.count_unit_measure ??
    ""
  );
}

export function getOrderItemOptionUnitPrice(
  option: OrderItemOption,
): string | null {
  return option.price == null ? null : String(option.price);
}

export function getOrderItemOptionVendorSku(option: OrderItemOption): string {
  return option.vendor_sku ?? "";
}
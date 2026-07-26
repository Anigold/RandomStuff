import { apiRequest } from "./client";

export type OrderStatus = string;

export type OrderLineDto = {
  id: string;
  order_id: string;

  status: string;
  status_reason?: string | null;

  source_item_name?: string | null;
  source_vendor_sku?: string | null;

  quantity: string | number;
  unit?: string | null;
  unit_price_snapshot?: string | number | null;

  item_id?: string | null;
  item_vendor_info_id?: string | null;
  item_name_snapshot?: string | null;
  vendor_sku_snapshot?: string | null;

  moved_to_order_id?: string | null;
  notes: string;

  created_at?: string | null;
  updated_at?: string | null;
};

export type OrderListDto = {
  id: string;

  store_id: string;
  store_name?: string | null;

  vendor_id: string;
  vendor_name?: string | null;

  order_date: string;
  delivery_date?: string | null;

  status: OrderStatus;
  source?: string | null;
  source_reference?: string | null;

  line_count: number;

  created_at?: string | null;
  updated_at?: string | null;
};

export type OrderDetailDto = OrderListDto & {
  notes: string;
  lines: OrderLineDto[];
};

export type OrderDto = OrderListDto | OrderDetailDto;

export type OrderLineWriteDto = {
  source_item_name?: string | null;
  source_vendor_sku?: string | null;

  item_id?: string | null;
  item_vendor_info_id?: string | null;

  item_name_snapshot?: string | null;
  vendor_sku_snapshot?: string | null;
  unit_price_snapshot?: string | null;

  quantity: string;
  unit?: string | null;

  notes: string;
};

export type OrderWriteDto = {
  store_id: string;
  vendor_id: string;

  order_date: string;
  delivery_date?: string | null;

  notes: string;

  lines: OrderLineWriteDto[];
};

type ScopedRequestArgs = {
  accessToken: string;
  scopeId: string;
};

type ListOrdersArgs = ScopedRequestArgs & {
  storeId?: string;
  vendor?: string;
  startDate?: string;
  endDate?: string;
};

type OrderIdArgs = ScopedRequestArgs & {
  orderId: string;
};

type CreateOrderArgs = ScopedRequestArgs & {
  order: OrderWriteDto;
};

type CancelOrderArgs = OrderIdArgs & {
  reason?: string | null;
};

function buildOrderParams({
  scopeId,
  storeId,
  vendor,
  startDate,
  endDate,
}: {
  scopeId: string;
  storeId?: string;
  vendor?: string;
  startDate?: string;
  endDate?: string;
}): string {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  if (storeId?.trim()) {
    params.set("store_id", storeId.trim());
  }

  if (vendor?.trim()) {
    params.set("vendor", vendor.trim());
  }

  if (startDate?.trim()) {
    params.set("start_date", startDate.trim());
  }

  if (endDate?.trim()) {
    params.set("end_date", endDate.trim());
  }

  return params.toString();
}

export function listOrders({
  accessToken,
  scopeId,
  storeId,
  vendor,
  startDate,
  endDate,
}: ListOrdersArgs): Promise<OrderListDto[]> {
  const params = buildOrderParams({
    scopeId,
    storeId,
    vendor,
    startDate,
    endDate,
  });

  return apiRequest<OrderListDto[]>(`/api/orders?${params}`, {
    accessToken,
  });
}

export function getOrder({
  accessToken,
  scopeId,
  orderId,
}: OrderIdArgs): Promise<OrderDetailDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<OrderDetailDto>(
    `/api/orders/${encodeURIComponent(orderId)}?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export function createOrder({
  accessToken,
  scopeId,
  order,
}: CreateOrderArgs): Promise<OrderDetailDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<OrderDetailDto>(`/api/orders?${params.toString()}`, {
    method: "POST",
    accessToken,
    body: order,
  });
}

export function cancelOrder({
  accessToken,
  scopeId,
  orderId,
  reason = null,
}: CancelOrderArgs): Promise<OrderDetailDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<OrderDetailDto>(
    `/api/orders/${encodeURIComponent(orderId)}/cancel?${params.toString()}`,
    {
      method: "POST",
      accessToken,
      body: {
        reason,
      },
    },
  );
}
import { apiRequest } from "./client";

export type InventoryItemDto = {
  id: string;
  name: string;
  category?: string | null;
  subcategory?: string | null;
  count_unit_quantity?: string | null;
  count_unit_measure?: string | null;
  is_active: boolean;
};

export type InventoryCountLineDto = {
  id: string;
  inventory_count_id: string;
  item_id: string;
  item_name?: string | null;
  quantity: string;
  unit: string;
  notes?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type InventoryCountDto = {
  id: string;
  store_id: string;
  count_date: string;
  status: "draft" | "submitted";
  notes?: string | null;
  lines: InventoryCountLineDto[];
  created_at?: string | null;
  updated_at?: string | null;
};

export type InventoryCountLineWriteDto = {
  item_id: string;
  quantity: string;
  unit: string;
  notes?: string | null;
};

export type InventoryCountWriteDto = {
  count_date: string;
  notes?: string | null;
  lines: InventoryCountLineWriteDto[];
};

export async function listInventoryItems({
  accessToken,
  scopeId,
}: {
  accessToken: string;
  scopeId: string;
}): Promise<InventoryItemDto[]> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  return apiRequest<InventoryItemDto[]>(
    `/api/inventory/items?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export async function createInventoryCount({
  accessToken,
  scopeId,
  count,
}: {
  accessToken: string;
  scopeId: string;
  count: InventoryCountWriteDto;
}): Promise<InventoryCountDto> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  return apiRequest<InventoryCountDto>(
    `/api/inventory/counts?${params.toString()}`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(count),
    },
  );
}

export async function listInventoryCounts({
  accessToken,
  scopeId,
}: {
  accessToken: string;
  scopeId: string;
}): Promise<InventoryCountDto[]> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  return apiRequest<InventoryCountDto[]>(
    `/api/inventory/counts?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export async function getInventoryCount({
  accessToken,
  scopeId,
  countId,
}: {
  accessToken: string;
  scopeId: string;
  countId: string;
}): Promise<InventoryCountDto> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  return apiRequest<InventoryCountDto>(
    `/api/inventory/counts/${encodeURIComponent(countId)}?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export async function updateInventoryCount({
  accessToken,
  scopeId,
  countId,
  count,
}: {
  accessToken: string;
  scopeId: string;
  countId: string;
  count: InventoryCountWriteDto;
}): Promise<InventoryCountDto> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  return apiRequest<InventoryCountDto>(
    `/api/inventory/counts/${encodeURIComponent(countId)}?${params.toString()}`,
    {
      method: "PUT",
      accessToken,
      body: JSON.stringify(count),
    },
  );
}

export async function submitInventoryCount({
  accessToken,
  scopeId,
  countId,
}: {
  accessToken: string;
  scopeId: string;
  countId: string;
}): Promise<InventoryCountDto> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);

  return apiRequest<InventoryCountDto>(
    `/api/inventory/counts/${encodeURIComponent(countId)}/submit?${params.toString()}`,
    {
      method: "POST",
      accessToken,
    },
  );
}
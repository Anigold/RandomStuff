import { apiRequest } from "./client";

export type ItemDto = {
  id: string;
  name: string;

  category?: string | null;
  subcategory?: string | null;

  count_unit_quantity?: string | number | null;
  count_unit_measure?: string | null;

  custom_each_name?: string | null;

  each_quantity?: string | number | null;
  each_measure?: string | null;

  weight_quantity?: string | number | null;
  weight_measure?: string | null;

  volume_quantity?: string | number | null;
  volume_measure?: string | null;

  is_active: boolean;

  created_at?: string | null;
  updated_at?: string | null;
};

export type ItemVendorInfoDto = {
  id: string;

  item_id: string;
  vendor_id: string;

  vendor_sku?: string | null;
  purchase_unit?: string | null;
  pack_size?: string | number | null;
  price?: string | number | null;

  last_purchase_date?: string | null;
  is_active: boolean;

  created_at?: string | null;
  updated_at?: string | null;
};

export type StoreItemInfoDto = {
  id: string;

  item_id: string;
  store_id: string;

  count_unit?: string | null;
  par?: string | number | null;

  is_active: boolean;

  created_at?: string | null;
  updated_at?: string | null;
};

export type ItemDetailDto = ItemDto & {
  vendor_info: ItemVendorInfoDto[];
  store_info: StoreItemInfoDto[];
};

export type OrderItemOptionDto = {
  item_id: string;
  item_vendor_info_id: string;

  item_name: string;
  vendor_id: string;

  vendor_sku?: string | null;
  purchase_unit?: string | null;
  pack_size?: string | number | null;
  price?: string | number | null;

  store_id: string;
  store_count_unit?: string | null;
  store_par?: string | number | null;

  count_unit_quantity?: string | number | null;
  count_unit_measure?: string | null;
};

export type ItemWriteDto = {
  name: string;
  category?: string | null;
  subcategory?: string | null;

  count_unit_quantity?: string | null;
  count_unit_measure?: string | null;

  custom_each_name?: string | null;

  each_quantity?: string | null;
  each_measure?: string | null;

  weight_quantity?: string | null;
  weight_measure?: string | null;

  volume_quantity?: string | null;
  volume_measure?: string | null;

  is_active: boolean;
};

export type AddItemStoreInfoDto = {
  store_id: string;
  count_unit?: string | null;
  par?: string | null;
  is_active: boolean;
};

export type UpdateItemStoreInfoDto = {
  count_unit?: string | null;
  par?: string | null;
  is_active: boolean;
};

type ListItemsOptions = {
  accessToken: string;
  scopeId: string;
  search?: string;
  includeInactive?: boolean;
};

type ListOrderItemOptionsArgs = {
  accessToken: string;
  scopeId: string;
  storeId: string;
  vendorId: string;
  includeInactive?: boolean;
};

type ItemMutationOptions = {
  accessToken: string;
  scopeId: string;
};

export function listItems({
  accessToken,
  scopeId,
  search,
  includeInactive = true,
}: ListItemsOptions): Promise<ItemDto[]> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);
  params.set("include_inactive", String(includeInactive));

  if (search?.trim()) {
    params.set("search", search.trim());
  }

  return apiRequest<ItemDto[]>(`/api/items?${params.toString()}`, {
    accessToken,
  });
}

export function listOrderItemOptions({
  accessToken,
  scopeId,
  storeId,
  vendorId,
  includeInactive = false,
}: ListOrderItemOptionsArgs): Promise<OrderItemOptionDto[]> {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);
  params.set("store_id", storeId);
  params.set("vendor_id", vendorId);
  params.set("include_inactive", String(includeInactive));

  return apiRequest<OrderItemOptionDto[]>(
    `/api/items/order-options?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export function getItem({
  accessToken,
  scopeId,
  itemId,
}: ItemMutationOptions & {
  itemId: string;
}): Promise<ItemDetailDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<ItemDetailDto>(
    `/api/items/${encodeURIComponent(itemId)}?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export function createItem({
  accessToken,
  scopeId,
  item,
}: ItemMutationOptions & {
  item: ItemWriteDto;
}): Promise<ItemDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<ItemDto>(`/api/items?${params.toString()}`, {
    method: "POST",
    accessToken,
    body: item,
  });
}

export function updateItem({
  accessToken,
  scopeId,
  itemId,
  item,
}: ItemMutationOptions & {
  itemId: string;
  item: ItemWriteDto;
}): Promise<ItemDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<ItemDto>(
    `/api/items/${encodeURIComponent(itemId)}?${params.toString()}`,
    {
      method: "PUT",
      accessToken,
      body: item,
    },
  );
}

export function deactivateItem({
  accessToken,
  scopeId,
  itemId,
}: ItemMutationOptions & {
  itemId: string;
}): Promise<ItemDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<ItemDto>(
    `/api/items/${encodeURIComponent(itemId)}?${params.toString()}`,
    {
      method: "DELETE",
      accessToken,
    },
  );
}

export function addItemStoreInfo({
  accessToken,
  scopeId,
  itemId,
  storeInfo,
}: ItemMutationOptions & {
  itemId: string;
  storeInfo: AddItemStoreInfoDto;
}): Promise<StoreItemInfoDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreItemInfoDto>(
    `/api/items/${encodeURIComponent(itemId)}/store-info?${params.toString()}`,
    {
      method: "POST",
      accessToken,
      body: storeInfo,
    },
  );
}

export function updateItemStoreInfo({
  accessToken,
  scopeId,
  itemId,
  infoId,
  storeInfo,
}: ItemMutationOptions & {
  itemId: string;
  infoId: string;
  storeInfo: UpdateItemStoreInfoDto;
}): Promise<StoreItemInfoDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreItemInfoDto>(
    `/api/items/${encodeURIComponent(itemId)}/store-info/${encodeURIComponent(
      infoId,
    )}?${params.toString()}`,
    {
      method: "PUT",
      accessToken,
      body: storeInfo,
    },
  );
}

export function deactivateItemStoreInfo({
  accessToken,
  scopeId,
  itemId,
  infoId,
}: ItemMutationOptions & {
  itemId: string;
  infoId: string;
}): Promise<StoreItemInfoDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreItemInfoDto>(
    `/api/items/${encodeURIComponent(itemId)}/store-info/${encodeURIComponent(
      infoId,
    )}?${params.toString()}`,
    {
      method: "DELETE",
      accessToken,
    },
  );
}
import { apiRequest } from "./client";

export type StoreDto = {
  id: string;
  name: string;
  is_active: boolean;
  general_manager?: string | null;
  inventory_clerk?: string | null;
  address?: string | null;
  phone_number?: string | null;
  special_notes?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type StoreWriteDto = {
  name: string;
  is_active: boolean;
  general_manager?: string | null;
  inventory_clerk?: string | null;
  address?: string | null;
  phone_number?: string | null;
  special_notes: string;
};

type ListStoresArgs = {
  accessToken: string;
  scopeId: string;
  search?: string;
  includeInactive?: boolean;
};

type StoreWriteArgs = {
  accessToken: string;
  scopeId: string;
  store: StoreWriteDto;
};

type StoreUpdateArgs = StoreWriteArgs & {
  storeId: string;
};

type StoreIdArgs = {
  accessToken: string;
  scopeId: string;
  storeId: string;
};

function buildStoreParams({
  scopeId,
  search,
  includeInactive = false,
}: {
  scopeId: string;
  search?: string;
  includeInactive?: boolean;
}): string {
  const params = new URLSearchParams();

  params.set("scope_id", scopeId);
  params.set("include_inactive", String(includeInactive));

  if (search?.trim()) {
    params.set("search", search.trim());
  }

  return params.toString();
}

export function listStores({
  accessToken,
  scopeId,
  search,
  includeInactive = false,
}: ListStoresArgs): Promise<StoreDto[]> {
  const params = buildStoreParams({
    scopeId,
    search,
    includeInactive,
  });

  return apiRequest<StoreDto[]>(`/api/stores?${params}`, {
    accessToken,
  });
}

export function getStore({
  accessToken,
  scopeId,
  storeId,
}: StoreIdArgs): Promise<StoreDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreDto>(
    `/api/stores/${encodeURIComponent(storeId)}?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export function createStore({
  accessToken,
  scopeId,
  store,
}: StoreWriteArgs): Promise<StoreDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreDto>(`/api/stores?${params.toString()}`, {
    method: "POST",
    accessToken,
    body: JSON.stringify(store),
  });
}

export function updateStore({
  accessToken,
  scopeId,
  storeId,
  store,
}: StoreUpdateArgs): Promise<StoreDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreDto>(
    `/api/stores/${encodeURIComponent(storeId)}?${params.toString()}`,
    {
      method: "PUT",
      accessToken,
      body: JSON.stringify(store),
    },
  );
}

export function deleteStore({
  accessToken,
  scopeId,
  storeId,
}: StoreIdArgs): Promise<StoreDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<StoreDto>(
    `/api/stores/${encodeURIComponent(storeId)}?${params.toString()}`,
    {
      method: "DELETE",
      accessToken,
    },
  );
}
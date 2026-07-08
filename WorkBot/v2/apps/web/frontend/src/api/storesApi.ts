import { apiRequest } from "./client";

export type StoreDto = {
  id: string;
  name: string;
  is_active: boolean;
};

export function listStores({
  accessToken,
  scopeId,
}: {
  accessToken: string;
  scopeId: string;
}): Promise<StoreDto[]> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);
  params.set("include_inactive", "false");

  return apiRequest<StoreDto[]>(`/api/stores?${params.toString()}`, {
    accessToken,
  });
}
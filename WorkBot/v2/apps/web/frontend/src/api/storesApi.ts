import { apiRequest } from "./client";

export type StoreDto = {
  id: string;
  name: string;
  is_active?: boolean;
};

export function listStores(accessToken: string): Promise<StoreDto[]> {
  return apiRequest<StoreDto[]>("/api/stores", {
    accessToken,
  });
}
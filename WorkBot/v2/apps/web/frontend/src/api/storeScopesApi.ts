import { apiRequest } from "./client";

export type StoreScopeDto = {
  id: string;
  name: string;
  type: "store" | "supervisor";
};

export function listStoreScopes(
  accessToken: string,
): Promise<StoreScopeDto[]> {
  return apiRequest<StoreScopeDto[]>("/api/store-scopes", {
    accessToken,
  });
}
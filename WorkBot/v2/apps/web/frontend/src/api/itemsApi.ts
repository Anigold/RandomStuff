import { apiRequest } from "./client";

export type ItemDto = {
  id: string;
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
  created_at?: string | null;
  updated_at?: string | null;
};

type ListItemsOptions = {
  accessToken: string;
  storeId: string;
  search?: string;
  includeInactive?: boolean;
};

export function listItems({
  accessToken,
  storeId,
  search,
  includeInactive = true,
}: ListItemsOptions): Promise<ItemDto[]> {
  const params = new URLSearchParams();

  params.set("store_id", storeId);
  params.set("include_inactive", String(includeInactive));

  if (search) {
    params.set("search", search);
  }

  return apiRequest<ItemDto[]>(`/api/items?${params.toString()}`, {
    accessToken,
  });
}
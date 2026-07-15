import { apiRequest } from "./client";

export type VendorStoreReferenceDto = {
  store_id: string;
  vendor_store_reference: string;
};

export type ContactInfoDto = {
  name: string;
  title: string;
  email: string;
  phone: string;
};

export type ScheduleEntryDto = {
  order_day: string;
  delivery_days: string[];
  cutoff_time: string;
};

export type OrderingInfoDto = {
  method: string[];
  email: string;
  portal_url: string;
  phone_number: string;
  schedule: ScheduleEntryDto[];
};

export type VendorDto = {
  id: string;
  name: string;
  is_active: boolean;
  order_format: string;
  special_notes: string;
  min_order_value: string | number;
  min_order_cases: number;
  internal_contacts: ContactInfoDto[];
  ordering: OrderingInfoDto;
  store_references: VendorStoreReferenceDto[];
  created_at?: string | null;
  updated_at?: string | null;
};

export type VendorWriteDto = {
  name: string;
  is_active: boolean;
  order_format: string;
  special_notes: string;
  min_order_value: string;
  min_order_cases: number;
  internal_contacts: ContactInfoDto[];
  ordering: OrderingInfoDto;
  store_references: VendorStoreReferenceDto[];
};

type ListVendorsArgs = {
  accessToken: string;
  scopeId: string;
  search?: string;
  includeInactive?: boolean;
};

type VendorWriteArgs = {
  accessToken: string;
  scopeId: string;
  vendor: VendorWriteDto;
};

type VendorUpdateArgs = VendorWriteArgs & {
  vendorId: string;
};

type VendorIdArgs = {
  accessToken: string;
  scopeId: string;
  vendorId: string;
};

function buildVendorParams({
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

export function listVendors({
  accessToken,
  scopeId,
  search,
  includeInactive = false,
}: ListVendorsArgs): Promise<VendorDto[]> {
  const params = buildVendorParams({
    scopeId,
    search,
    includeInactive,
  });

  return apiRequest<VendorDto[]>(`/api/vendors?${params}`, {
    accessToken,
  });
}

export function getVendor({
  accessToken,
  scopeId,
  vendorId,
}: VendorIdArgs): Promise<VendorDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<VendorDto>(
    `/api/vendors/${encodeURIComponent(vendorId)}?${params.toString()}`,
    {
      accessToken,
    },
  );
}

export function createVendor({
  accessToken,
  scopeId,
  vendor,
}: VendorWriteArgs): Promise<VendorDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<VendorDto>(`/api/vendors?${params.toString()}`, {
    method: "POST",
    accessToken,
    body: vendor,
  });
}

export function updateVendor({
  accessToken,
  scopeId,
  vendorId,
  vendor,
}: VendorUpdateArgs): Promise<VendorDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<VendorDto>(
    `/api/vendors/${encodeURIComponent(vendorId)}?${params.toString()}`,
    {
      method: "PUT",
      accessToken,
      body: vendor,
    },
  );
}

export function deleteVendor({
  accessToken,
  scopeId,
  vendorId,
}: VendorIdArgs): Promise<VendorDto> {
  const params = new URLSearchParams();
  params.set("scope_id", scopeId);

  return apiRequest<VendorDto>(
    `/api/vendors/${encodeURIComponent(vendorId)}?${params.toString()}`,
    {
      method: "DELETE",
      accessToken,
    },
  );
}
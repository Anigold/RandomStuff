import { useCallback, useEffect, useState } from "react";

import { listStores, type StoreDto } from "../../../api/storesApi";
import { listVendors, type VendorDto } from "../../../api/vendorsApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";

type UseVendorsManagementResult = {
  vendors: VendorDto[];
  stores: StoreDto[];
  isLoadingVendors: boolean;
  vendorErrorMessage: string | null;
  canManageVendors: boolean;
  reloadVendors: () => Promise<void>;
};

export function useVendorsManagement(): UseVendorsManagementResult {
  const accessToken = useAccessToken();
  const { activeScope, activeScopeId, isLoadingScopes } = useStoreScope();

  const [vendors, setVendors] = useState<VendorDto[]>([]);
  const [stores, setStores] = useState<StoreDto[]>([]);
  const [isLoadingVendors, setIsLoadingVendors] = useState(true);
  const [vendorErrorMessage, setVendorErrorMessage] = useState<string | null>(
    null,
  );

  const canManageVendors = activeScope?.type === "supervisor";

  const reloadVendors = useCallback(async () => {
    if (isLoadingScopes) {
      return;
    }

    if (!activeScopeId) {
      setVendors([]);
      setStores([]);
      setIsLoadingVendors(false);
      setVendorErrorMessage("Select an operating scope before loading vendors.");
      return;
    }

    if (!canManageVendors) {
      setVendors([]);
      setStores([]);
      setIsLoadingVendors(false);
      setVendorErrorMessage(null);
      return;
    }

    setIsLoadingVendors(true);
    setVendorErrorMessage(null);

    try {
      const [loadedVendors, loadedStores] = await Promise.all([
        listVendors({
          accessToken,
          scopeId: activeScopeId,
          includeInactive: true,
        }),
        listStores({
          accessToken,
          scopeId: activeScopeId,
          includeInactive: false,
        }),
      ]);

      setVendors(loadedVendors);
      setStores(loadedStores);
    } catch (error) {
      setVendorErrorMessage(
        error instanceof Error ? error.message : "Unable to load vendors.",
      );
    } finally {
      setIsLoadingVendors(false);
    }
  }, [accessToken, activeScopeId, canManageVendors, isLoadingScopes]);

  useEffect(() => {
    void reloadVendors();
  }, [reloadVendors]);

  return {
    vendors,
    stores,
    isLoadingVendors,
    vendorErrorMessage,
    canManageVendors,
    reloadVendors,
  };
}
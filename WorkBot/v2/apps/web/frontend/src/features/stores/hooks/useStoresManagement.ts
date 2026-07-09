import { useCallback, useEffect, useState } from "react";

import { listStores, type StoreDto } from "../../../api/storesApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../hooks/useStoreScope";

type UseStoresManagementResult = {
  stores: StoreDto[];
  isLoadingStores: boolean;
  storeErrorMessage: string | null;
  canManageStores: boolean;
  reloadStores: () => Promise<void>;
};

export function useStoresManagement(): UseStoresManagementResult {
  const accessToken = useAccessToken();
  const { activeScope, activeScopeId, isLoadingScopes } = useStoreScope();

  const [stores, setStores] = useState<StoreDto[]>([]);
  const [isLoadingStores, setIsLoadingStores] = useState(true);
  const [storeErrorMessage, setStoreErrorMessage] = useState<string | null>(
    null,
  );

  const canManageStores = activeScope?.type === "supervisor";

  const reloadStores = useCallback(async () => {
    if (isLoadingScopes) {
      return;
    }

    if (!activeScopeId) {
      setStores([]);
      setIsLoadingStores(false);
      setStoreErrorMessage("Select an operating scope before loading stores.");
      return;
    }

    if (!canManageStores) {
      setStores([]);
      setIsLoadingStores(false);
      setStoreErrorMessage(null);
      return;
    }

    setIsLoadingStores(true);
    setStoreErrorMessage(null);

    try {
      const loadedStores = await listStores({
        accessToken,
        scopeId: activeScopeId,
        includeInactive: true,
      });

      setStores(loadedStores);
    } catch (error) {
      setStoreErrorMessage(
        error instanceof Error ? error.message : "Unable to load stores.",
      );
    } finally {
      setIsLoadingStores(false);
    }
  }, [accessToken, activeScopeId, canManageStores, isLoadingScopes]);

  useEffect(() => {
    void reloadStores();
  }, [reloadStores]);

  return {
    stores,
    isLoadingStores,
    storeErrorMessage,
    canManageStores,
    reloadStores,
  };
}
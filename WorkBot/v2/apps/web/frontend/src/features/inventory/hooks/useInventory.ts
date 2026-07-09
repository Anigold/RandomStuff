import { useEffect, useState } from "react";

import {
  listInventoryCounts,
  listInventoryItems,
  type InventoryCountDto,
  type InventoryItemDto,
} from "../../../api/inventoryApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";

type UseInventoryResult = {
  inventoryItems: InventoryItemDto[];
  inventoryCounts: InventoryCountDto[];
  isLoading: boolean;
  errorMessage: string | null;
  reloadInventory: () => Promise<void>;
};

export function useInventory(): UseInventoryResult {
  const accessToken = useAccessToken();
  const { activeScope, activeScopeId, isLoadingScopes } = useStoreScope();

  const [inventoryItems, setInventoryItems] = useState<InventoryItemDto[]>([]);
  const [inventoryCounts, setInventoryCounts] = useState<InventoryCountDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function reloadInventory() {
    if (isLoadingScopes) {
      return;
    }

    if (!activeScopeId) {
      setInventoryItems([]);
      setInventoryCounts([]);
      setIsLoading(false);
      setErrorMessage("Select an operating scope before loading inventory.");
      return;
    }

    if (activeScope?.type !== "store") {
      setInventoryItems([]);
      setInventoryCounts([]);
      setIsLoading(false);
      setErrorMessage(null);
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [loadedItems, loadedCounts] = await Promise.all([
        listInventoryItems({
          accessToken,
          scopeId: activeScopeId,
        }),
        listInventoryCounts({
          accessToken,
          scopeId: activeScopeId,
        }),
      ]);

      setInventoryItems(loadedItems);
      setInventoryCounts(loadedCounts);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to load inventory.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void reloadInventory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, activeScopeId, activeScope?.type, isLoadingScopes]);

  return {
    inventoryItems,
    inventoryCounts,
    isLoading,
    errorMessage,
    reloadInventory,
  };
}
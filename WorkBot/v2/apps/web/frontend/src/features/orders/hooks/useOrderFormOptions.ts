import { useCallback, useEffect, useState } from "react";

import { listItems, type ItemDto } from "../../../api/itemsApi";
import { listStores, type StoreDto } from "../../../api/storesApi";
import { listVendors, type VendorDto } from "../../../api/vendorsApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";

type UseOrderFormOptionsResult = {
  stores: StoreDto[];
  vendors: VendorDto[];
  items: ItemDto[];
  isLoadingOptions: boolean;
  optionsErrorMessage: string | null;
  defaultStoreId: string | null;
  requireStoreSelection: boolean;
  reloadOptions: () => Promise<void>;
};

export function useOrderFormOptions(): UseOrderFormOptionsResult {
  const accessToken = useAccessToken();
  const { activeScope, activeScopeId, isLoadingScopes } = useStoreScope();

  const [stores, setStores] = useState<StoreDto[]>([]);
  const [vendors, setVendors] = useState<VendorDto[]>([]);
  const [items, setItems] = useState<ItemDto[]>([]);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
  const [optionsErrorMessage, setOptionsErrorMessage] = useState<string | null>(
    null,
  );

  const isSupervisorScope = activeScope?.type === "supervisor";
  const requireStoreSelection = isSupervisorScope;
  const defaultStoreId = isSupervisorScope ? null : activeScopeId;

  const reloadOptions = useCallback(async () => {
    if (isLoadingScopes) {
      return;
    }

    if (!activeScopeId) {
      setStores([]);
      setVendors([]);
      setItems([]);
      setIsLoadingOptions(false);
      setOptionsErrorMessage(
        "Select an operating scope before loading order options.",
      );
      return;
    }

    setIsLoadingOptions(true);
    setOptionsErrorMessage(null);

    try {
      const [loadedVendors, loadedItems, loadedStores] = await Promise.all([
        listVendors({
          accessToken,
          scopeId: activeScopeId,
          includeInactive: false,
        }),
        listItems({
          accessToken,
          scopeId: activeScopeId,
        }),
        isSupervisorScope
          ? listStores({
              accessToken,
              scopeId: activeScopeId,
              includeInactive: false,
            })
          : Promise.resolve([]),
      ]);

      setVendors(loadedVendors);
      setItems(loadedItems);
      setStores(loadedStores);
    } catch (error) {
      setStores([]);
      setVendors([]);
      setItems([]);
      setOptionsErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to load order options.",
      );
    } finally {
      setIsLoadingOptions(false);
    }
  }, [accessToken, activeScopeId, isSupervisorScope, isLoadingScopes]);

  useEffect(() => {
    void reloadOptions();
  }, [reloadOptions]);

  return {
    stores,
    vendors,
    items,
    isLoadingOptions,
    optionsErrorMessage,
    defaultStoreId,
    requireStoreSelection,
    reloadOptions,
  };
}
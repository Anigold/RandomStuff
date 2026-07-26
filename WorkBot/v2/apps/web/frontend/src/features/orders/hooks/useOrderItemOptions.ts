import { useCallback, useEffect, useState } from "react";

import {
  listOrderItemOptions,
  type OrderItemOptionDto,
} from "../../../api/itemsApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";

type UseOrderItemOptionsArgs = {
  storeId: string;
  vendorId: string;
};

type UseOrderItemOptionsResult = {
  itemOptions: OrderItemOptionDto[];
  isLoadingItemOptions: boolean;
  itemOptionsErrorMessage: string | null;
  reloadItemOptions: () => Promise<void>;
};

export function useOrderItemOptions({
  storeId,
  vendorId,
}: UseOrderItemOptionsArgs): UseOrderItemOptionsResult {
  const accessToken = useAccessToken();
  const { activeScopeId } = useStoreScope();

  const [itemOptions, setItemOptions] = useState<OrderItemOptionDto[]>([]);
  const [isLoadingItemOptions, setIsLoadingItemOptions] = useState(false);
  const [itemOptionsErrorMessage, setItemOptionsErrorMessage] = useState<
    string | null
  >(null);

  const reloadItemOptions = useCallback(async () => {
    if (!activeScopeId || !storeId || !vendorId) {
      setItemOptions([]);
      setIsLoadingItemOptions(false);
      setItemOptionsErrorMessage(null);
      return;
    }

    setIsLoadingItemOptions(true);
    setItemOptionsErrorMessage(null);

    try {
      const loadedOptions = await listOrderItemOptions({
        accessToken,
        scopeId: activeScopeId,
        storeId,
        vendorId,
      });

      setItemOptions(loadedOptions);
    } catch (error) {
      setItemOptions([]);
      setItemOptionsErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to load order item options.",
      );
    } finally {
      setIsLoadingItemOptions(false);
    }
  }, [accessToken, activeScopeId, storeId, vendorId]);

  useEffect(() => {
    void reloadItemOptions();
  }, [reloadItemOptions]);

  return {
    itemOptions,
    isLoadingItemOptions,
    itemOptionsErrorMessage,
    reloadItemOptions,
  };
}
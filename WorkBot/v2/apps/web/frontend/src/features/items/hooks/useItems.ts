import { useEffect, useState } from "react";

import { listItems, type ItemDto } from "../../../api/itemsApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";

type UseItemsResult = {
  items: ItemDto[];
  isLoading: boolean;
  errorMessage: string | null;
  reloadItems: () => Promise<void>;
};

export function useItems(): UseItemsResult {
  const accessToken = useAccessToken();
  const { activeScopeId, isLoadingScopes } = useStoreScope();

  const [items, setItems] = useState<ItemDto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function reloadItems() {
    if (isLoadingScopes) {
      return;
    }

    if (!activeScopeId) {
      setItems([]);
      setIsLoading(false);
      setErrorMessage("Select an operating scope before loading items.");
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const loadedItems = await listItems({
        accessToken,
        scopeId: activeScopeId,
      });

      setItems(loadedItems);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to load items.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void reloadItems();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, activeScopeId, isLoadingScopes]);

  return {
    items,
    isLoading,
    errorMessage,
    reloadItems,
  };
}
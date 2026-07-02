import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { listStores, type StoreDto } from "../../api/storesApi";
import { useAccessToken } from "../auth/hooks/useAccessTokens";

type StoreScopeContextValue = {
  stores: StoreDto[];
  activeStoreId: string | null;
  activeStore: StoreDto | null;
  isLoadingStores: boolean;
  storeErrorMessage: string | null;
  setActiveStoreId: (storeId: string) => void;
  reloadStores: () => Promise<void>;
};

export const StoreScopeContext = createContext<StoreScopeContextValue | null>(
  null,
);

type StoreScopeProviderProps = {
  children: ReactNode;
};

export function StoreScopeProvider({ children }: StoreScopeProviderProps) {
  const accessToken = useAccessToken();

  const [stores, setStores] = useState<StoreDto[]>([]);
  const [activeStoreId, setActiveStoreIdState] = useState<string | null>(null);
  const [isLoadingStores, setIsLoadingStores] = useState(true);
  const [storeErrorMessage, setStoreErrorMessage] = useState<string | null>(
    null,
  );

  const reloadStores = useCallback(async () => {
    setIsLoadingStores(true);
    setStoreErrorMessage(null);

    try {
      const loadedStores = await listStores(accessToken);
      const activeStores = loadedStores.filter(
        (store) => store.is_active !== false,
      );

      setStores(activeStores);

      setActiveStoreIdState((currentStoreId) => {
        if (
          currentStoreId &&
          activeStores.some((store) => store.id === currentStoreId)
        ) {
          return currentStoreId;
        }

        return activeStores[0]?.id ?? null;
      });
    } catch (error) {
      setStoreErrorMessage(
        error instanceof Error ? error.message : "Unable to load stores.",
      );
    } finally {
      setIsLoadingStores(false);
    }
  }, [accessToken]);

  useEffect(() => {
    void reloadStores();
  }, [reloadStores]);

  const setActiveStoreId = useCallback((storeId: string) => {
    setActiveStoreIdState(storeId);
  }, []);

  const activeStore = useMemo(
    () => stores.find((store) => store.id === activeStoreId) ?? null,
    [stores, activeStoreId],
  );

  const value = useMemo<StoreScopeContextValue>(
    () => ({
      stores,
      activeStoreId,
      activeStore,
      isLoadingStores,
      storeErrorMessage,
      setActiveStoreId,
      reloadStores,
    }),
    [
      stores,
      activeStoreId,
      activeStore,
      isLoadingStores,
      storeErrorMessage,
      setActiveStoreId,
      reloadStores,
    ],
  );

  return (
    <StoreScopeContext.Provider value={value}>
      {children}
    </StoreScopeContext.Provider>
  );
}
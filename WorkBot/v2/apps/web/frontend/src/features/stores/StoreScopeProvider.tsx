import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  listStoreScopes,
  type StoreScopeDto,
} from "../../api/storeScopesApi";
import { useAccessToken } from "../auth/hooks/useAccessTokens";

type StoreScopeContextValue = {
  scopes: StoreScopeDto[];
  activeScopeId: string | null;
  activeScope: StoreScopeDto | null;
  isLoadingScopes: boolean;
  scopeErrorMessage: string | null;
  setActiveScopeId: (scopeId: string) => void;
  reloadScopes: () => Promise<void>;
};

export const StoreScopeContext =
  createContext<StoreScopeContextValue | null>(null);

type StoreScopeProviderProps = {
  children: ReactNode;
};

export function StoreScopeProvider({ children }: StoreScopeProviderProps) {
  const accessToken = useAccessToken();

  const [scopes, setScopes] = useState<StoreScopeDto[]>([]);
  const [activeScopeId, setActiveScopeIdState] = useState<string | null>(null);
  const [isLoadingScopes, setIsLoadingScopes] = useState(true);
  const [scopeErrorMessage, setScopeErrorMessage] = useState<string | null>(
    null,
  );

  const reloadScopes = useCallback(async () => {
    setIsLoadingScopes(true);
    setScopeErrorMessage(null);

    try {
      const loadedScopes = await listStoreScopes(accessToken);

      setScopes(loadedScopes);

      setActiveScopeIdState((currentScopeId) => {
        if (
          currentScopeId &&
          loadedScopes.some((scope) => scope.id === currentScopeId)
        ) {
          return currentScopeId;
        }

        return loadedScopes[0]?.id ?? null;
      });
    } catch (error) {
      setScopeErrorMessage(
        error instanceof Error
          ? error.message
          : "Unable to load store scopes.",
      );
    } finally {
      setIsLoadingScopes(false);
    }
  }, [accessToken]);

  useEffect(() => {
    void reloadScopes();
  }, [reloadScopes]);

  const setActiveScopeId = useCallback((scopeId: string) => {
    setActiveScopeIdState(scopeId);
  }, []);

  const activeScope = useMemo(
    () => scopes.find((scope) => scope.id === activeScopeId) ?? null,
    [scopes, activeScopeId],
  );

  const value = useMemo<StoreScopeContextValue>(
    () => ({
      scopes,
      activeScopeId,
      activeScope,
      isLoadingScopes,
      scopeErrorMessage,
      setActiveScopeId,
      reloadScopes,
    }),
    [
      scopes,
      activeScopeId,
      activeScope,
      isLoadingScopes,
      scopeErrorMessage,
      setActiveScopeId,
      reloadScopes,
    ],
  );

  return (
    <StoreScopeContext.Provider value={value}>
      {children}
    </StoreScopeContext.Provider>
  );
}
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

const ACTIVE_SCOPE_STORAGE_KEY = "workbot.activeScopeId";

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

function readStoredScopeId(): string | null {
  try {
    return window.localStorage.getItem(ACTIVE_SCOPE_STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredScopeId(scopeId: string | null): void {
  try {
    if (scopeId) {
      window.localStorage.setItem(ACTIVE_SCOPE_STORAGE_KEY, scopeId);
    } else {
      window.localStorage.removeItem(ACTIVE_SCOPE_STORAGE_KEY);
    }
  } catch {
    // Ignore localStorage failures. React state will still work for this session.
  }
}

function scopeExists(scopes: StoreScopeDto[], scopeId: string | null): boolean {
  return Boolean(scopeId && scopes.some((scope) => scope.id === scopeId));
}

export function StoreScopeProvider({ children }: StoreScopeProviderProps) {
  const accessToken = useAccessToken();

  const [scopes, setScopes] = useState<StoreScopeDto[]>([]);
  const [activeScopeId, setActiveScopeIdState] = useState<string | null>(() =>
    readStoredScopeId(),
  );
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
        const storedScopeId = readStoredScopeId();

        if (scopeExists(loadedScopes, currentScopeId)) {
          writeStoredScopeId(currentScopeId);
          return currentScopeId;
        }

        if (scopeExists(loadedScopes, storedScopeId)) {
          writeStoredScopeId(storedScopeId);
          return storedScopeId;
        }

        const fallbackScopeId = loadedScopes[0]?.id ?? null;
        writeStoredScopeId(fallbackScopeId);

        return fallbackScopeId;
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
    writeStoredScopeId(scopeId);
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
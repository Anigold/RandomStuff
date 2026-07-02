import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  login as loginRequest,
  logout as logoutRequest,
  refreshAuth,
  type CurrentUserDto,
} from "../../api/authApi";
import { ApiError } from "../../api/client";
import { getCurrentUser } from "../../api/meApi";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

export type AuthContextValue = {
  status: AuthStatus;
  accessToken: string | null;
  currentUser: CurrentUserDto | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  reloadCurrentUser: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<CurrentUserDto | null>(null);

  const clearAuthState = useCallback(() => {
    setAccessToken(null);
    setCurrentUser(null);
    setStatus("unauthenticated");
  }, []);

  const refreshSession = useCallback(async () => {
    try {
      const response = await refreshAuth();

      setAccessToken(response.access_token);
      setCurrentUser(response.user);
      setStatus("authenticated");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        clearAuthState();
        return;
      }

      clearAuthState();
      throw error;
    }
  }, [clearAuthState]);

  const reloadCurrentUser = useCallback(async () => {
    if (!accessToken) {
      clearAuthState();
      return;
    }

    try {
      const user = await getCurrentUser(accessToken);
      setCurrentUser(user);
      setStatus("authenticated");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        await refreshSession();
        return;
      }

      throw error;
    }
  }, [accessToken, clearAuthState, refreshSession]);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  const login = useCallback(async (username: string, password: string) => {
    const response = await loginRequest({
      username,
      password,
    });

    setAccessToken(response.access_token);
    setCurrentUser(response.user);
    setStatus("authenticated");
  }, []);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      clearAuthState();
    }
  }, [clearAuthState]);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      accessToken,
      currentUser,
      login,
      logout,
      refreshSession,
      reloadCurrentUser,
    }),
    [
      status,
      accessToken,
      currentUser,
      login,
      logout,
      refreshSession,
      reloadCurrentUser,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
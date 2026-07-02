import { useAuth } from "./useAuth";

export function useAccessToken(): string {
  const { accessToken, status } = useAuth();

  if (status !== "authenticated" || !accessToken) {
    throw new Error("Access token is not available");
  }

  return accessToken;
}
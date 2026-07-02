import { apiRequest } from "./client";
import type { CurrentUserDto } from "./authApi"

export function getCurrentUser(
  accessToken: string,
): Promise<CurrentUserDto> {
  return apiRequest<CurrentUserDto>("/api/me", {
    accessToken,
  });
}
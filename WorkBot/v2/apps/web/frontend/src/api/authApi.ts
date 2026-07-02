import { apiRequest } from "./client";

export type CurrentUserDto = {
  id: string;
  username: string;
  email?: string | null;
  display_name?: string | null;
};

export type LoginRequestDto = {
  username: string;
  password: string;
};

export type AuthTokenResponseDto = {
  access_token: string;
  token_type: "bearer";
  user: CurrentUserDto;
};

export type LogoutResponseDto = {
  ok: true;
};

export function login(
  request: LoginRequestDto,
): Promise<AuthTokenResponseDto> {
  return apiRequest<AuthTokenResponseDto>("/api/auth/login", {
    method: "POST",
    body: request,
  });
}

export function refreshAuth(): Promise<AuthTokenResponseDto> {
  return apiRequest<AuthTokenResponseDto>("/api/auth/refresh", {
    method: "POST",
  });
}

export function logout(): Promise<LogoutResponseDto> {
  return apiRequest<LogoutResponseDto>("/api/auth/logout", {
    method: "POST",
  });
}
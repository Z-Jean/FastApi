/**
 * 认证 API
 */
import api from "./api";
import type { ApiResponse, LoginForm, LoginResponse } from "./types";

export const authApi = {
  login: (data: LoginForm) =>
    api.post<ApiResponse<LoginResponse>>("/api/auth/login", data),
};

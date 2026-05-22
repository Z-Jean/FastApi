/**
 * 用户管理 API
 */
import api from "./api";
import type { ApiResponse, User } from "./types";

// 用户列表
export const getUsers = () => api.get<ApiResponse<User[]>>("/api/users");

// 获取单个用户
export const getUser = (id: number) =>
  api.get<ApiResponse<User>>(`/api/users/${id}`);

// 创建用户
export const createUser = (data: {
  name: string;
  age: number;
  email: string;
}) => api.post<ApiResponse<User>>("/api/users", data);

// 更新用户
export const updateUser = (
  id: number,
  data: { name?: string; age?: number; email?: string }
) => api.put<ApiResponse<User>>(`/api/users/${id}`, data);

// 删除用户
export const deleteUser = (id: number) =>
  api.delete<ApiResponse<null>>(`/api/users/${id}`);

/**
 * 分类管理 API
 */
import api from "./api";
import type { ApiResponse, Category } from "./types";

// 获取分类列表
export const getCategories = () =>
  api.get<ApiResponse<Category[]>>("/api/categories");

// 获取单个分类
export const getCategory = (id: number) =>
  api.get<ApiResponse<Category>>(`/api/categories/${id}`);

// 创建分类
export const createCategory = (data: { name: string }) =>
  api.post<ApiResponse<Category>>("/api/categories", data);

// 更新分类
export const updateCategory = (id: number, data: { name: string }) =>
  api.put<ApiResponse<Category>>(`/api/categories/${id}`, data);

// 删除分类
export const deleteCategory = (id: number) =>
  api.delete<ApiResponse<null>>(`/api/categories/${id}`);

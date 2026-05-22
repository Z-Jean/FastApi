/**
 * 商品管理 API
 */
import api from "./api";
import type { ApiResponse, Product } from "./types";

// 获取商品列表
export const getProducts = () =>
  api.get<ApiResponse<Product[]>>("/api/products");

// 获取单个商品
export const getProduct = (id: number) =>
  api.get<ApiResponse<Product>>(`/api/products/${id}`);

// 根据分类ID获取商品
export const getProductsByCategory = (categoryId: number) =>
  api.get<ApiResponse<Product[]>>(`/api/products/category/${categoryId}`);

// 创建商品
export const createProduct = (data: {
  name: string;
  price: number;
  category_id: number;
}) => api.post<ApiResponse<Product>>("/api/products", data);

// 更新商品
export const updateProduct = (
  id: number,
  data: { name?: string; price?: number; category_id?: number }
) => api.put<ApiResponse<Product>>(`/api/products/${id}`, data);

// 删除商品
export const deleteProduct = (id: number) =>
  api.delete<ApiResponse<null>>(`/api/products/${id}`);

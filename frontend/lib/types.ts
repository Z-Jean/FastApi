/**
 * API 响应类型定义
 */
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

/**
 * 用户类型
 */
export interface User {
  id: number;
  name: string;
  age: number;
  email: string;
  created_at?: string;
}

/**
 * 登录请求
 */
export interface LoginForm {
  username: string;
  password: string;
}

/**
 * 登录响应
 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * 分类类型
 */
export interface Category {
  id: number;
  name: string;
  product_count?: number;
  created_at?: string;
}

/**
 * 商品类型
 */
export interface Product {
  id: number;
  name: string;
  price: number;
  category_id: number;
  category_name?: string;
  created_at?: string;
}

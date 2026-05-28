"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">欢迎使用全栈管理系统</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {/* 用户管理 */}
          <Link href="/users" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">👥</div>
            <h3 className="text-lg font-semibold text-gray-900">用户管理</h3>
            <p className="text-gray-500 text-sm mt-1">用户信息增删改查</p>
          </Link>

          {/* 分类管理 */}
          <Link href="/categories" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">📂</div>
            <h3 className="text-lg font-semibold text-gray-900">分类管理</h3>
            <p className="text-gray-500 text-sm mt-1">商品分类增删改查</p>
          </Link>

          {/* 商品管理 */}
          <Link href="/products" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">📦</div>
            <h3 className="text-lg font-semibold text-gray-900">商品管理</h3>
            <p className="text-gray-500 text-sm mt-1">商品信息增删改查</p>
          </Link>

          {/* API 文档 */}
          <a href="/docs" target="_blank" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">📖</div>
            <h3 className="text-lg font-semibold text-gray-900">API 文档</h3>
            <p className="text-gray-500 text-sm mt-1">查看接口文档</p>
          </a>

          {/* 米兔聊天 */}
          <Link href="/chat" className="card hover:shadow-lg transition-shadow">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold text-gray-900">米兔聊天</h3>
            <p className="text-gray-500 text-sm mt-1">AI 智能助手</p>
          </Link>
        </div>
      </main>
    </div>
  );
}

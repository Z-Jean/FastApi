"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Header() {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* 左侧 Logo */}
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold text-gray-900">
              <Link href="/dashboard">📦 全栈管理系统</Link>
            </h1>
            <nav className="flex gap-6">
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-blue-600 font-medium"
              >
                首页
              </Link>
              <Link
                href="/users"
                className="text-gray-600 hover:text-blue-600 font-medium"
              >
                用户管理
              </Link>
              <Link
                href="/categories"
                className="text-gray-600 hover:text-blue-600 font-medium"
              >
                分类管理
              </Link>
              <Link
                href="/products"
                className="text-gray-600 hover:text-blue-600 font-medium"
              >
                商品管理
              </Link>
              <Link
                href="/chat"
                className="text-gray-600 hover:text-blue-600 font-medium"
              >
                米兔聊天
              </Link>
            </nav>
          </div>

          {/* 右侧用户操作 */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">👤 admin</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
            >
              退出登录
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

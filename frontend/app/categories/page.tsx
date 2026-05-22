"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from "@/lib/category";
import type { Category } from "@/lib/types";

export default function CategoriesPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [deleteId, setDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
    } else {
      fetchCategories();
    }
  }, [router]);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const res = await getCategories();
      if (res.data.code === 200) {
        setCategories(res.data.data);
      }
    } catch (err) {
      console.error("获取分类列表失败", err);
    } finally {
      setLoading(false);
    }
  };

  const openAdd = () => {
    setEditId(null);
    setName("");
    setError("");
    setShowModal(true);
  };

  const openEdit = (cat: Category) => {
    setEditId(cat.id);
    setName(cat.name);
    setError("");
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (editId) {
        const res = await updateCategory(editId, { name });
        if (res.data.code === 200) {
          setShowModal(false);
          fetchCategories();
        } else {
          setError(res.data.message);
        }
      } else {
        const res = await createCategory({ name });
        if (res.data.code === 200) {
          setShowModal(false);
          fetchCategories();
        } else {
          setError(res.data.message);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "操作失败");
    }
  };

  const confirmDelete = async () => {
    if (!deleteId) return;
    try {
      const res = await deleteCategory(deleteId);
      if (res.data.code === 200) {
        setDeleteId(null);
        fetchCategories();
      }
    } catch (err: any) {
      alert(err.response?.data?.message || "删除失败");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">📂 分类管理</h2>
          <button onClick={openAdd} className="btn btn-primary">
            + 新增分类
          </button>
        </div>

        <div className="card">
          {loading ? (
            <div className="text-center py-12 text-gray-500">加载中...</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>分类名称</th>
                  <th>商品数量</th>
                  <th>创建时间</th>
                  <th className="text-right">操作</th>
                </tr>
              </thead>
              <tbody>
                {categories.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-8 text-gray-500">
                      暂无分类
                    </td>
                  </tr>
                ) : (
                  categories.map((cat) => (
                    <tr key={cat.id}>
                      <td className="font-mono text-gray-500">{cat.id}</td>
                      <td className="font-semibold">{cat.name}</td>
                      <td>
                        <span
                          className={`px-2 py-1 rounded text-sm ${
                            cat.product_count && cat.product_count > 0
                              ? "bg-blue-100 text-blue-700"
                              : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {cat.product_count || 0} 个商品
                        </span>
                      </td>
                      <td className="text-gray-500 text-sm">
                        {cat.created_at
                          ? new Date(cat.created_at).toLocaleString("zh-CN")
                          : "-"}
                      </td>
                      <td className="text-right space-x-2">
                        <button
                          onClick={() => openEdit(cat)}
                          className="btn btn-secondary text-sm px-3 py-1"
                        >
                          编辑
                        </button>
                        <button
                          onClick={() => setDeleteId(cat.id)}
                          className="btn btn-danger text-sm px-3 py-1"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </main>

      {/* 弹窗 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {editId ? "✏️ 编辑分类" : "➕ 新增分类"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  分类名称（1-10字符）
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="form-input"
                  placeholder="请输入分类名称"
                  minLength={1}
                  maxLength={10}
                  required
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded-lg text-sm">
                  ⚠️ {error}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn btn-secondary"
                >
                  取消
                </button>
                <button type="submit" className="btn btn-primary">
                  保存
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 删除确认 */}
      {deleteId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-2">⚠️ 确认删除</h3>
            <p className="text-gray-600 mb-6">确定要删除该分类吗？</p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteId(null)}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button onClick={confirmDelete} className="btn btn-danger">
                确认删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

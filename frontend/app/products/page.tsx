"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
} from "@/lib/product";
import { getCategories } from "@/lib/category";
import type { Product, Category } from "@/lib/types";

export default function ProductsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState({
    name: "",
    price: 0,
    category_id: 0,
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
    } else {
      fetchData();
    }
  }, [router]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [prodRes, catRes] = await Promise.all([
        getProducts(),
        getCategories(),
      ]);
      if (prodRes.data.code === 200) {
        setProducts(prodRes.data.data);
      }
      if (catRes.data.code === 200) {
        setCategories(catRes.data.data);
      }
    } catch (err) {
      console.error("获取数据失败", err);
    } finally {
      setLoading(false);
    }
  };

  const openAdd = () => {
    setEditId(null);
    setForm({ name: "", price: 0, category_id: 0 });
    setError("");
    setShowModal(true);
  };

  const openEdit = (prod: Product) => {
    setEditId(prod.id);
    setForm({
      name: prod.name,
      price: prod.price,
      category_id: prod.category_id,
    });
    setError("");
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setError("");

    if (!form.name.trim()) {
      setError("请输入商品名称");
      return;
    }
    if (form.price <= 0) {
      setError("价格必须大于 0");
      return;
    }
    if (form.category_id <= 0) {
      setError("请选择所属分类");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        name: form.name.trim(),
        price: form.price,
        category_id: form.category_id,
      };
      if (editId) {
        const res = await updateProduct(editId, payload);
        if (res.data.code === 200) {
          setShowModal(false);
          fetchData();
        } else {
          setError(res.data.message);
        }
      } else {
        const res = await createProduct(payload);
        if (res.data.code === 200) {
          setShowModal(false);
          fetchData();
        } else {
          setError(res.data.message);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "操作失败");
    } finally {
      setSubmitting(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteId || deleting) return;
    setDeleting(true);
    try {
      const res = await deleteProduct(deleteId);
      if (res.data.code === 200) {
        setDeleteId(null);
        fetchData();
      } else {
        alert(res.data.message || "删除失败");
      }
    } catch (err: any) {
      alert(err.response?.data?.message || "删除失败");
    } finally {
      setDeleting(false);
    }
  };

  const deleteTarget = products.find((p) => p.id === deleteId);

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">📦 商品管理</h2>
          <button onClick={openAdd} className="btn btn-primary">
            + 新增商品
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
                  <th>商品名称</th>
                  <th>价格</th>
                  <th>所属分类</th>
                  <th>创建时间</th>
                  <th className="text-right">操作</th>
                </tr>
              </thead>
              <tbody>
                {products.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-gray-500">
                      暂无商品，请先添加分类
                    </td>
                  </tr>
                ) : (
                  products.map((prod) => (
                    <tr key={prod.id}>
                      <td className="font-mono text-gray-500">{prod.id}</td>
                      <td className="font-semibold">{prod.name}</td>
                      <td className="text-red-600 font-semibold">
                        ¥{prod.price.toFixed(2)}
                      </td>
                      <td>
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                          {prod.category_name || `分类${prod.category_id}`}
                        </span>
                      </td>
                      <td className="text-gray-500 text-sm">
                        {prod.created_at
                          ? new Date(prod.created_at).toLocaleString("zh-CN")
                          : "-"}
                      </td>
                      <td className="text-right space-x-2">
                        <button
                          onClick={() => openEdit(prod)}
                          className="btn btn-secondary text-sm px-3 py-1"
                        >
                          编辑
                        </button>
                        <button
                          onClick={() => setDeleteId(prod.id)}
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
              {editId ? "✏️ 编辑商品" : "➕ 新增商品"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  商品名称
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) =>
                    setForm({ ...form, name: e.target.value })
                  }
                  className="form-input"
                  placeholder="请输入商品名称"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  价格（元）
                </label>
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={form.price}
                  onChange={(e) =>
                    setForm({ ...form, price: parseFloat(e.target.value) })
                  }
                  className="form-input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  所属分类
                </label>
                <select
                  value={form.category_id}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      category_id: parseInt(e.target.value),
                    })
                  }
                  className="form-input"
                  required
                >
                  <option value={0}>请选择分类</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
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
                  disabled={submitting}
                  className="btn btn-secondary"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn-primary"
                >
                  {submitting ? "保存中..." : "保存"}
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
            <p className="text-gray-600 mb-6">
              确定要删除商品
              <span className="font-semibold text-gray-900">
                「{deleteTarget?.name || `#${deleteId}`}」
              </span>
              吗？此操作不可撤销。
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteId(null)}
                disabled={deleting}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={confirmDelete}
                disabled={deleting}
                className="btn btn-danger"
              >
                {deleting ? "删除中..." : "确认删除"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

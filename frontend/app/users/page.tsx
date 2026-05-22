"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import { getUsers, createUser, updateUser, deleteUser } from "@/lib/user";
import type { User } from "@/lib/types";

export default function UsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState({ name: "", age: 25, email: "" });
  const [error, setError] = useState("");
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // 检查登录
  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
    } else {
      fetchUsers();
    }
  }, [router]);

  // 获取用户列表
  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await getUsers();
      if (res.data.code === 200) {
        setUsers(res.data.data);
      }
    } catch (err) {
      console.error("获取用户列表失败", err);
    } finally {
      setLoading(false);
    }
  };

  // 打开新增弹窗
  const openAdd = () => {
    setEditId(null);
    setForm({ name: "", age: 25, email: "" });
    setError("");
    setShowModal(true);
  };

  // 打开编辑弹窗
  const openEdit = (user: User) => {
    setEditId(user.id);
    setForm({ name: user.name, age: user.age, email: user.email });
    setError("");
    setShowModal(true);
  };

  // 提交表单
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      if (editId) {
        const res = await updateUser(editId, form);
        if (res.data.code === 200) {
          setShowModal(false);
          fetchUsers();
        } else {
          setError(res.data.message);
        }
      } else {
        const res = await createUser(form);
        if (res.data.code === 200) {
          setShowModal(false);
          fetchUsers();
        } else {
          setError(res.data.message);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.message || "操作失败");
    }
  };

  // 确认删除
  const confirmDelete = async () => {
    if (!deleteId) return;
    try {
      const res = await deleteUser(deleteId);
      if (res.data.code === 200) {
        setDeleteId(null);
        fetchUsers();
      }
    } catch (err: any) {
      alert(err.response?.data?.message || "删除失败");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* 页面标题 */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">👥 用户管理</h2>
          <button onClick={openAdd} className="btn btn-primary">
            + 新增用户
          </button>
        </div>

        {/* 用户表格 */}
        <div className="card">
          {loading ? (
            <div className="text-center py-12 text-gray-500">加载中...</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>姓名</th>
                  <th>年龄</th>
                  <th>邮箱</th>
                  <th>创建时间</th>
                  <th className="text-right">操作</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-gray-500">
                      暂无数据
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td className="font-mono text-gray-500">{user.id}</td>
                      <td className="font-semibold">{user.name}</td>
                      <td>{user.age} 岁</td>
                      <td className="text-blue-600">{user.email}</td>
                      <td className="text-gray-500 text-sm">
                        {user.created_at
                          ? new Date(user.created_at).toLocaleString("zh-CN")
                          : "-"}
                      </td>
                      <td className="text-right space-x-2">
                        <button
                          onClick={() => openEdit(user)}
                          className="btn btn-secondary text-sm px-3 py-1"
                        >
                          编辑
                        </button>
                        <button
                          onClick={() => setDeleteId(user.id)}
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

      {/* 新增/编辑弹窗 */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              {editId ? "✏️ 编辑用户" : "➕ 新增用户"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  姓名
                </label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="form-input"
                  placeholder="请输入姓名"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  年龄（18-60岁）
                </label>
                <input
                  type="number"
                  min="18"
                  max="60"
                  value={form.age}
                  onChange={(e) =>
                    setForm({ ...form, age: parseInt(e.target.value) })
                  }
                  className="form-input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  邮箱
                </label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) =>
                    setForm({ ...form, email: e.target.value })
                  }
                  className="form-input"
                  placeholder="请输入邮箱"
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

      {/* 删除确认弹窗 */}
      {deleteId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-2xl">
            <h3 className="text-lg font-bold text-gray-900 mb-2">⚠️ 确认删除</h3>
            <p className="text-gray-600 mb-6">确定要删除该用户吗？此操作不可撤销。</p>
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

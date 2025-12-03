import { useEffect, useState } from "react";
import usersService from "../services/usersService";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [editing, setEditing] = useState(null); // usuário sendo editado
  const [form, setForm] = useState({
    username: "",
    email: "",
    role: "",
    password: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Carregar lista de usuários ao abrir a página
  const loadUsers = async () => {
    try {
      const response = await usersService.getAll();
      setUsers(response.data);
    } catch (err) {
      console.error("Erro ao carregar usuários:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // Abrir modal de edição
  const startEdit = (user) => {
    setEditing(user.id);
    setForm({
      username: user.username,
      email: user.email,
      role: user.role,
      password: "",
    });
  };

  // Salvar alterações
  const save = async () => {
    setSaving(true);
    try {
      const payload = {
        username: form.username,
        email: form.email,
        role: form.role,
      };

      if (form.password.trim() !== "") {
        payload.password = form.password;
      }

      await usersService.update(editing, payload);
      await loadUsers();
      setEditing(null);
    } catch (err) {
      alert("Erro ao salvar alterações");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  // Apagar usuário
  const removeUser = async (id) => {
    if (!confirm("Tem certeza que deseja remover este usuário?")) return;

    try {
      await usersService.remove(id);
      loadUsers();
    } catch (err) {
      alert("Erro ao remover usuário");
      console.error(err);
    }
  };

  if (loading) return <p>Carregando usuários...</p>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Gerenciar Usuários</h1>

      <div className="overflow-x-auto">
        <table className="w-full border text-left">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-2 border">ID</th>
              <th className="p-2 border">Username</th>
              <th className="p-2 border">Email</th>
              <th className="p-2 border">Role</th>
              <th className="p-2 border w-40">Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border">
                <td className="p-2 border">{u.id}</td>
                <td className="p-2 border">{u.username}</td>
                <td className="p-2 border">{u.email}</td>
                <td className="p-2 border">{u.role}</td>
                <td className="p-2 border flex gap-2">
                  <button
                    onClick={() => startEdit(u)}
                    className="px-2 py-1 bg-blue-500 text-white rounded"
                  >
                    Editar
                  </button>

                  <button
                    onClick={() => removeUser(u.id)}
                    className="px-2 py-1 bg-red-500 text-white rounded"
                  >
                    Remover
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal de edição */}
      {editing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded shadow-xl w-96">
            <h2 className="text-xl font-bold mb-4">Editar Usuário</h2>

            <label className="block mb-2">Username</label>
            <input
              className="border p-2 w-full mb-3"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />

            <label className="block mb-2">Email</label>
            <input
              className="border p-2 w-full mb-3"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />

            <label className="block mb-2">Role</label>
            <select
              className="border p-2 w-full mb-3"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            >
              <option value="user">user</option>
              <option value="admin">admin</option>
              <option value="editor">editor</option>
            </select>

            <label className="block mb-2">Nova senha (opcional)</label>
            <input
              type="password"
              className="border p-2 w-full mb-4"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />

            <div className="flex justify-end gap-2">
              <button
                className="px-3 py-1 bg-gray-400 text-white rounded"
                onClick={() => setEditing(null)}
                disabled={saving}
              >
                Cancelar
              </button>

              <button
                className="px-3 py-1 bg-green-600 text-white rounded"
                onClick={save}
                disabled={saving}
              >
                {saving ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

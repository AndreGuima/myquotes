import { useEffect, useState } from "react";
import usersService from "../services/usersService";
import DataTable from "../components/DataTable";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({
    username: "",
    email: "",
    role: "",
    password: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

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

  const startEdit = (user) => {
    setEditing(user.id);
    setForm({
      username: user.username,
      email: user.email,
      role: user.role,
      password: "",
    });
  };

  const save = async () => {
    setSaving(true);
    try {
      const payload = {
        username: form.username,
        email: form.email,
        role: form.role,
      };

      if (form.password.trim() !== "") payload.password = form.password;

      await usersService.update(editing, payload);
      await loadUsers();
      setEditing(null);
    } catch (err) {
      alert("Erro ao salvar");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const removeUser = async (id) => {
    if (!confirm("Tem certeza?")) return;
    await usersService.remove(id);
    loadUsers();
  };

  if (loading) return <p>Carregando usuários...</p>;

  return (
    <>
      <DataTable
        title="Gerenciar Usuários"
        createLabel={null}
        createLink={null}
        enableSearch={true}
        searchPlaceholder="Buscar por username, email ou role..."
        searchKeys={["username", "email", "role"]}
        columns={[
          { key: "id", label: "ID", width: "60px" },
          { key: "username", label: "Username" },
          { key: "email", label: "Email" },
          { key: "role", label: "Role" },
          { key: "is_active", label: "Status", width: "120px" },
          { key: "actions", label: "Ações", width: "120px" },
        ]}
        data={users}
        renderRow={(u) => (
          <tr key={u.id} className="border">
            <td className="p-2 border">{u.id}</td>
            <td className="p-2 border">{u.username}</td>
            <td className="p-2 border">{u.email}</td>
            <td className="p-2 border">{u.role}</td>

            <td className="p-2 border">
              {u.is_active ? (
                <span className="px-2 py-1 bg-green-200 text-green-800 rounded text-sm">
                  Ativo
                </span>
              ) : (
                <span className="px-2 py-1 bg-red-200 text-red-800 rounded text-sm">
                  Inativo
                </span>
              )}
            </td>


            <td className="p-2 border flex gap-2">
              <button
                onClick={() => startEdit(u)}
                className="px-2 py-1 bg-blue-500 text-white rounded"
              >
                Editar
              </button>

              {u.is_active ? (
                <button
                  onClick={() => removeUser(u.id)}
                  className="px-2 py-1 bg-red-500 text-white rounded"
                >
                  Desativar
                </button>
              ) : (
                <button
                  onClick={async () => {
                    await usersService.restore(u.id);
                    loadUsers();
                  }}
                  className="px-2 py-1 bg-green-500 text-white rounded"
                >
                  Restaurar
                </button>
              )}
            </td>

          </tr>
        )}
      />

      {/* Modal permanece igual */}
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
    </>
  );
}

import { useEffect, useState } from "react";
import usersService from "../services/usersService";
import DataTable from "../components/DataTable";
import { notify, confirm } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

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
  const [processing, setProcessing] = useState(null); // desativar/restaurar

  const loadUsers = async () => {
    try {
      const users = await usersService.getAll();
      setUsers(users);
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao carregar usuários"));
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

      if (form.password.trim() !== "") {
        payload.password = form.password;
      }

      await usersService.update(editing, payload);

      notify.success("Usuário atualizado com sucesso");
      setEditing(null);
      await loadUsers();
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar usuário"));
    } finally {
      setSaving(false);
    }
  };

  const removeUser = (id) => {
    confirm({
      message: "Tem certeza que deseja desativar este usuário?",
      confirmText: "Desativar",
      cancelText: "Cancelar",
      variant: "danger",

      onConfirm: async () => {
        setProcessing(id);

        try {
          await usersService.remove(id);
          notify.success("Usuário desativado");
          loadUsers();
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao desativar usuário"));
        } finally {
          setProcessing(null);
        }
      },
    });
  };

  const restoreUser = (id) => {
    confirm({
      message: "Deseja restaurar este usuário?",
      confirmText: "Restaurar",
      cancelText: "Cancelar",
      variant: "primary",

      onConfirm: async () => {
        setProcessing(id);

        try {
          await usersService.restore(id);
          notify.success("Usuário restaurado");
          loadUsers();
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao restaurar usuário"));
        } finally {
          setProcessing(null);
        }
      },
    });
  };

  if (loading) {
    return <p className="p-4 text-gray-600">Carregando usuários...</p>;
  }

  return (
    <>
      <DataTable
        title="Gerenciar Usuários"
        enableSearch
        searchPlaceholder="Buscar por username, email ou role..."
        searchKeys={["username", "email", "role"]}
        columns={[
          { key: "id", label: "ID", width: "60px" },
          { key: "username", label: "Username" },
          { key: "email", label: "Email" },
          { key: "role", label: "Role" },
          { key: "is_active", label: "Status", width: "120px" },
          { key: "actions", label: "Ações", width: "140px" },
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
                  disabled={processing === u.id}
                  className="px-2 py-1 bg-red-500 text-white rounded disabled:opacity-50"
                >
                  {processing === u.id ? "Aguarde..." : "Desativar"}
                </button>
              ) : (
                <button
                  onClick={() => restoreUser(u.id)}
                  disabled={processing === u.id}
                  className="px-2 py-1 bg-green-500 text-white rounded disabled:opacity-50"
                >
                  {processing === u.id ? "Aguarde..." : "Restaurar"}
                </button>
              )}
            </td>
          </tr>
        )}
      />

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
    </>
  );
}

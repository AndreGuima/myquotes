import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { confirm, notify } from "../core/toast";
import { useAuth } from "../contexts/useAuth";

export default function MainLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  function handleLogout() {
    confirm({
      message: "Tem certeza que deseja sair da sua conta?",
      confirmText: "Sair",
      cancelText: "Cancelar",
      variant: "danger",

      onConfirm: () => {
        logout();
        notify.success("Logout realizado com sucesso");
        navigate("/login", { replace: true });
      },
    });
  }

  const navClass = ({ isActive }) =>
    isActive ? "text-blue-400 font-semibold" : "hover:text-blue-400";

  return (
    <div className="flex h-screen bg-[var(--app-bg)] text-[var(--app-text)]">
      {/* Sidebar */}
      <aside className="w-64 bg-[var(--panel-bg)] text-[var(--panel-text)] flex flex-col p-4">
        <NavLink to="/home" className="text-xl font-bold mb-6">
          MyLife
        </NavLink>

        <nav className="flex flex-col gap-3 flex-1">
          <NavLink to="/home" className={navClass}>
            Home
          </NavLink>

          <NavLink to="/quotes" className={navClass}>
            Quotes
          </NavLink>

          <NavLink to="/habits" className={navClass}>
            Hábitos
          </NavLink>

          <NavLink to="/daily-routine" className={navClass}>
            Rotina do Dia
          </NavLink>

          <NavLink to="/dreams" className={navClass}>
            Sonhos
          </NavLink>

          <NavLink to="/reading-list" className={navClass}>
            Leituras
          </NavLink>

          <NavLink to="/preferences" className={navClass}>
            Preferências
          </NavLink>

          {user?.role === "admin" && (
            <NavLink to="/users" className={navClass}>
              Users
            </NavLink>
          )}
        </nav>

        {/* User info */}
        <div className="bg-[var(--panel-subtle-bg)] p-3 rounded mb-4 text-sm">
          Logado como: <span className="font-semibold">{user?.username}</span>
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 mt-2 py-2 rounded transition"
        >
          Sair
        </button>
      </aside>

      {/* Conteúdo */}
      <div className="flex-1 bg-[var(--content-bg)] p-6 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}

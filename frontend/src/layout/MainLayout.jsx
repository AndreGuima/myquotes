import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { confirm, notify } from "../core/toast";
import { useAuth } from "../contexts/useAuth";

export default function MainLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
    isActive
      ? "rounded-lg bg-white/10 px-3 py-2 text-blue-300 font-semibold"
      : "rounded-lg px-3 py-2 hover:bg-white/5 hover:text-blue-300";

  function handleMobileNavClick() {
    setMobileMenuOpen(false);
  }

  return (
    <div className="flex min-h-screen bg-[var(--app-bg)] text-[var(--app-text)]">
      <button
        type="button"
        onClick={() => setMobileMenuOpen(true)}
        className="fixed left-4 top-4 z-40 rounded-lg bg-[var(--panel-bg)] px-3 py-2 text-sm font-semibold text-[var(--panel-text)] shadow-lg md:hidden"
      >
        Menu
      </button>

      {mobileMenuOpen && (
        <button
          type="button"
          aria-label="Fechar menu"
          onClick={() => setMobileMenuOpen(false)}
          className="fixed inset-0 z-30 bg-slate-950/50 md:hidden"
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-[17rem] max-w-[84vw]
          bg-[var(--panel-bg)] text-[var(--panel-text)] p-4 shadow-2xl
          transition-transform duration-200 md:static md:z-auto md:w-64 md:max-w-none md:translate-x-0 md:shadow-none
          ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="mb-6 flex items-center justify-between md:block">
          <NavLink
            to="/home"
            className="text-xl font-bold"
            onClick={handleMobileNavClick}
          >
            MyLife
          </NavLink>

          <button
            type="button"
            onClick={() => setMobileMenuOpen(false)}
            className="rounded-md px-2 py-1 text-sm text-[var(--panel-text)]/80 hover:bg-white/10 md:hidden"
          >
            Fechar
          </button>
        </div>

        <nav className="flex flex-col gap-2">
          <NavLink
            to="/home"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Home
          </NavLink>

          <NavLink
            to="/quotes"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Quotes
          </NavLink>

          <NavLink
            to="/day-management"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Gestão do Dia
          </NavLink>

          <NavLink
            to="/finances"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Finanças
          </NavLink>

          <NavLink
            to="/reading-list"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Leituras
          </NavLink>

          <NavLink
            to="/dreams"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Metas e Conquistas
          </NavLink>

          <NavLink
            to="/preferences"
            className={navClass}
            onClick={handleMobileNavClick}
          >
            Preferências
          </NavLink>

          {user?.role === "admin" && (
            <NavLink
              to="/users"
              className={navClass}
              onClick={handleMobileNavClick}
            >
              Users
            </NavLink>
          )}
        </nav>

        <div className="mt-6 border-t border-white/10 pt-4">
          <div className="mb-4 rounded bg-[var(--panel-subtle-bg)] p-3 text-sm">
            Logado como: <span className="font-semibold">{user?.username}</span>
          </div>

          <button
            onClick={handleLogout}
            className="w-full rounded bg-red-600 py-2 transition hover:bg-red-700"
          >
            Sair
          </button>
        </div>
      </aside>

      <div className="flex-1 bg-[var(--content-bg)] overflow-auto">
        <div className="min-h-screen px-4 pb-6 pt-20 md:p-6">
          <Outlet />
        </div>
      </div>
    </div>
  );
}

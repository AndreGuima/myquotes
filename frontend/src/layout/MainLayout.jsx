import { NavLink, Outlet, useNavigate } from "react-router-dom";

export default function MainLayout() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login", { replace: true });
  }

  const navClass = ({ isActive }) =>
    isActive ? "text-blue-400 font-semibold" : "hover:text-blue-400";

  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-900 text-white flex flex-col p-4">
        <h2 className="text-xl font-bold mb-6">MyLife</h2>

        <nav className="flex flex-col gap-3 flex-1">
          <NavLink to="/home" className={navClass}>
            Dashboard
          </NavLink>

          <NavLink to="/quotes" className={navClass}>
            Quotes
          </NavLink>

          <NavLink to="/habits" className={navClass}>
            Hábitos
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

        <div className="bg-gray-800 p-3 rounded mb-4 text-sm">
          Logado como: <span className="font-semibold">{user?.username}</span>
        </div>

        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 mt-6 py-2 rounded"
        >
          Sair
        </button>
      </aside>

      <div className="flex-1 bg-gray-100 p-6 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}

import { Link, Outlet, useNavigate } from "react-router-dom";

export default function MainLayout() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login", { replace: true }); // 👈 MELHOR logout
  }

  return (
    <div className="flex h-screen">

      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col p-4">
        <h2 className="text-xl font-bold mb-6">MyQuotes</h2>

        <nav className="flex flex-col gap-3 flex-1">
          <Link to="/home" className="hover:text-blue-400">Dashboard</Link>
          <Link to="/quotes" className="hover:text-blue-400">Quotes</Link>
          <Link to="/users" className="hover:text-blue-400">Users</Link>
        </nav>

        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 mt-6 py-2 rounded"
        >
          Sair
        </button>
      </aside>

      {/* Conteúdo */}
      <div className="flex-1 bg-gray-100 p-6 overflow-auto">
        <Outlet />
      </div>
    </div>
  );
}

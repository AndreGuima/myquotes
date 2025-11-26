import { Navigate } from "react-router-dom";

export default function AdminRoute({ children }) {
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  // 1) Não está logado
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // 2) Está logado, mas não é admin
  if (user.role !== "admin") {
    return <Navigate to="/home" replace />;
  }

  // 3) OK → é admin
  return children;
}

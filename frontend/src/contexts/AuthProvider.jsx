import { useState } from "react";
import authService from "../services/authService";
import { clearSession } from "../services/session";
import { AuthContext } from "./AuthContext";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const [loading, setLoading] = useState(false);

  async function login({ email, password }) {
    try {
      setLoading(true);

      const data = await authService.login({ email, password });

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      setUser(data.user);
      return data;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearSession();
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

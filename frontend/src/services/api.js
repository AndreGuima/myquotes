import axios from "axios";
import { clearSession } from "./session";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// ==========================
// Interceptor de REQUEST
// ==========================
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ==========================
// Interceptor de RESPONSE
// ==========================
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url || "";

    if (status === 401) {
      // Rotas públicas (não devem forçar logout)
      const publicRoutes = [
        "/auth/login",
        "/auth/register",
        "/auth/forgot-password",
        "/auth/reset-password",
        "/auth/reset-password/validate",
        "/auth/verify-email",
      ];

      const isPublicRoute = publicRoutes.some((route) =>
        requestUrl.includes(route),
      );

      if (!isPublicRoute) {
        clearSession();
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);

export default api;

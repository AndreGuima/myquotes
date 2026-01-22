import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import authService from "../services/authService";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const token = params.get("token");

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  // 🔎 1) Valida token ao carregar a página
  useEffect(() => {
    async function validateToken() {
      try {
        await authService.validateResetToken(token);

        setChecking(false);
      } catch {
        setError("Token inválido ou expirado.");
        setChecking(false);
      }
    }

    if (token) {
      validateToken();
    } else {
      setError("Token inválido.");
      setChecking(false);
    }
  }, [token]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("A senha deve ter no mínimo 8 caracteres.");
      return;
    }

    if (password !== confirm) {
      setError("As senhas não conferem.");
      return;
    }

    setLoading(true);

    try {
      await authService.resetPassword({
        token,
        new_password: password,
      });

      setDone(true);
      setTimeout(() => navigate("/login"), 2000);
    } catch {
      setError("Token inválido ou expirado. Solicite um novo link.");
    } finally {
      setLoading(false);
    }
  }

  // ⏳ Enquanto valida o token
  if (checking) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
        <div className="bg-white p-6 rounded-xl shadow-lg w-full max-w-sm text-center">
          <p className="text-gray-600">Validando token…</p>
        </div>
      </div>
    );
  }

  // ❌ Token inválido
  if (error && !done) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
        <div className="bg-white p-6 rounded-xl shadow-lg w-full max-w-sm text-center">
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      </div>
    );
  }

  // ✅ Sucesso
  if (done) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
        <div className="bg-white p-6 rounded-xl shadow-lg w-full max-w-sm text-center">
          <h2 className="text-xl font-semibold mb-2">
            Senha redefinida com sucesso
          </h2>
          <p className="text-gray-600">Redirecionando para o login…</p>
        </div>
      </div>
    );
  }

  // 📝 Formulário
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-4 text-center">Nova senha</h1>

        {error && (
          <div className="bg-red-100 text-red-700 px-3 py-2 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="password"
            placeholder="Nova senha"
            className="w-full border p-2 rounded"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Confirmar senha"
            className="w-full border p-2 rounded"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Salvando..." : "Redefinir senha"}
          </button>
        </form>
      </div>
    </div>
  );
}

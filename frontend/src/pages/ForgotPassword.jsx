import { useState } from "react";
import { Link } from "react-router-dom";
import authService from "../services/authService";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      await authService.forgotPassword(email);

      setMessage(
        "Se este email estiver cadastrado, você receberá instruções para redefinir sua senha.",
      );
    } catch {
      setError("Erro ao enviar solicitação. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--app-bg)] p-4 text-[var(--app-text)]">
      <div className="w-full max-w-sm rounded-2xl border themed-border themed-card p-8 shadow-lg">
        <h1 className="mb-4 text-center text-2xl font-bold">
          Esqueci minha senha
        </h1>

        <p className="themed-muted mb-6 text-center">
          Informe seu email para receber o link de redefinição de senha.
        </p>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-red-700">
            {error}
          </div>
        )}

        {message && (
          <div className="mb-4 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-green-700">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-medium mb-1">Email</label>
            <input
              type="email"
              className="themed-input w-full rounded-lg p-2.5"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 py-2.5 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Enviando..." : "Enviar link"}
          </button>
        </form>

        <div className="mt-5 text-center text-sm">
          <Link to="/login" className="themed-link hover:underline">
            Voltar para o login
          </Link>
        </div>
      </div>
    </div>
  );
}

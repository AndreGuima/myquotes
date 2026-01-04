import { useState } from "react";
import api from "../services/api";

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
      await api.post("/auth/forgot-password", { email });

      // resposta SEMPRE genérica (boa prática de segurança)
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
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-sm">
        <h1 className="text-2xl font-bold text-center mb-4">
          Esqueci minha senha
        </h1>

        <p className="text-center text-gray-600 mb-6">
          Informe seu email para receber o link de redefinição de senha.
        </p>

        {error && (
          <div className="bg-red-100 text-red-700 px-3 py-2 rounded mb-4">
            {error}
          </div>
        )}

        {message && (
          <div className="bg-green-100 text-green-700 px-3 py-2 rounded mb-4">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-medium mb-1">Email</label>
            <input
              type="email"
              className="w-full border p-2 rounded"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Enviando..." : "Enviar link"}
          </button>
        </form>
      </div>
    </div>
  );
}

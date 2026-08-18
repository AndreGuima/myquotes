import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/useAuth";
import PasswordInput from "../components/PasswordInput";
import authService from "../services/authService";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setSuccessMessage("");

    try {
      await login({ email, password });
      navigate("/home");
    } catch (err) {
      const backendMessage =
        err.response?.data?.detail || "Erro ao fazer login. Tente novamente.";

      setError(backendMessage);
    }
  }

  async function handleResendVerification() {
    if (!email.trim()) {
      setError("Informe seu e-mail antes de reenviar a verificação.");
      return;
    }

    try {
      const response = await authService.resendVerificationEmail(email);
      setError("");
      setSuccessMessage(
        response.data?.message || "E-mail de verificação reenviado.",
      );
    } catch (err) {
      const backendMessage =
        err.response?.data?.detail || "Não foi possível reenviar o e-mail.";
      setError(backendMessage);
    }
  }

  const canResendVerification = error
    .toLowerCase()
    .includes("verificar seu email");

  return (
    <div className="flex items-center justify-center min-h-screen bg-[var(--app-bg)] p-4 text-[var(--app-text)]">
      <div className="themed-card themed-border border p-8 rounded-xl shadow-lg w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center mb-4">MyLife</h1>

        <p className="text-center themed-muted mb-6">
          Controle sobre seus hábitos e alcance seus objetivos!
        </p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded mb-4">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-3 py-2 rounded mb-4">
            {successMessage}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          {/* Email */}
          <div>
            <label className="block font-medium mb-1">Email</label>
            <input
              type="email"
              className="themed-input w-full p-2 rounded"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {/* Senha */}
          <PasswordInput
            label="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            Entrar
          </button>

          {canResendVerification && (
            <button
              type="button"
              onClick={handleResendVerification}
              className="w-full bg-amber-500 text-white py-2 rounded hover:bg-amber-600"
            >
              Reenviar validação do e-mail
            </button>
          )}
        </form>

        <div className="text-center mt-4 space-y-2">
          <button
            type="button"
            className="text-sm themed-link hover:underline block w-full"
            onClick={() => navigate("/forgot-password")}
          >
            Esqueceu sua senha?
          </button>

          <button
            type="button"
            className="themed-link hover:underline"
            onClick={() => navigate("/register")}
          >
            Criar conta
          </button>
        </div>
      </div>
    </div>
  );
}

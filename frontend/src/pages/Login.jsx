import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/useAuth";
import PasswordInput from "../components/PasswordInput";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleLogin(e) {
    e.preventDefault();
    setError("");

    try {
      await login({ email, password });
      navigate("/home");
    } catch (err) {
      const backendMessage =
        err.response?.data?.detail || "Erro ao fazer login. Tente novamente.";

      setError(backendMessage);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center mb-4">MyQuotes</h1>

        <p className="text-center text-gray-600 mb-6">
          Entre para acessar suas frases favoritas!
        </p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          {/* Email */}
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
        </form>

        <div className="text-center mt-4 space-y-2">
          <button
            type="button"
            className="text-sm text-blue-600 hover:underline block w-full"
            onClick={() => navigate("/forgot-password")}
          >
            Esqueceu sua senha?
          </button>

          <button
            type="button"
            className="text-blue-600 hover:underline"
            onClick={() => navigate("/register")}
          >
            Criar conta
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  async function handleRegister(e) {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("A senha deve ter pelo menos 8 caracteres.");
      return;
    }

    if (password !== confirmPassword) {
      setError("As senhas não coincidem.");
      return;
    }

    try {
      await api.post("/auth/register", {
        username,
        email,
        password,
        confirm_password: confirmPassword,
      });

      navigate("/verify-instructions");
    } catch {
      setError("Não foi possível criar a conta.");
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-sm">
        <h1 className="text-3xl font-bold text-center mb-4">Criar Conta</h1>
        <p className="text-center text-gray-600 mb-6">
          Preencha os dados abaixo para se registrar.
        </p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          {/* Campos iguais aos que você já tinha */}
        </form>

        <div className="text-center mt-4">
          <button
            className="text-blue-600 hover:underline"
            onClick={() => navigate("/login")}
          >
            Já tenho conta
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import authService from "../services/authService";
import PasswordInput from "../components/PasswordInput";
import {
  validatePassword,
  isPasswordValid as isPasswordValidFn,
} from "../utils/passwordPolicy";

/**
 * Componente estático para exibir regras de senha
 * (deve ficar fora do Register para não ser recriado a cada render)
 */
function Rule({ ok, children }) {
  return (
    <li className={`text-sm ${ok ? "text-green-600" : "text-red-500"}`}>
      {ok ? "✓" : "✗"} {children}
    </li>
  );
}

export default function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  // 🟢 Controle de foco da senha
  const [passwordFocused, setPasswordFocused] = useState(false);

  const passwordChecks = useMemo(() => validatePassword(password), [password]);

  const isPasswordValid = isPasswordValidFn(passwordChecks);
  const passwordsMatch = password && password === confirmPassword;

  async function handleRegister(e) {
    e.preventDefault();
    setError("");

    if (!isPasswordValid) {
      setError("A senha não atende aos requisitos de segurança.");
      return;
    }

    if (!passwordsMatch) {
      setError("As senhas não coincidem.");
      return;
    }

    try {
      await authService.register({
        username,
        email,
        password,
        confirm_password: confirmPassword,
      });

      navigate("/verify-instructions");
    } catch (err) {
      const backendError =
        err?.response?.data?.detail || "Não foi possível criar a conta.";
      setError(backendError);
    }
  }

  const isDisabled =
    !username ||
    !email ||
    !password ||
    !confirmPassword ||
    !isPasswordValid ||
    !passwordsMatch;

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
          {/* Nome */}
          <div>
            <label className="block font-medium mb-1">Nome</label>
            <input
              type="text"
              className="w-full border p-2 rounded"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

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
            onFocus={() => setPasswordFocused(true)}
            onBlur={() => setPasswordFocused(false)}
            placeholder="Crie uma senha segura"
          />

          {/* Regras de senha (FOCO ou TEXTO) */}
          {(passwordFocused || password) && (
            <ul className="bg-gray-50 border rounded p-3 space-y-1">
              <Rule ok={passwordChecks.minLength}>Mínimo de 8 caracteres</Rule>
              <Rule ok={passwordChecks.upper}>Uma letra maiúscula</Rule>
              <Rule ok={passwordChecks.lower}>Uma letra minúscula</Rule>
              <Rule ok={passwordChecks.digit}>Um número</Rule>
              <Rule ok={passwordChecks.special}>Um caractere especial</Rule>
            </ul>
          )}

          {/* Confirmar Senha */}
          <PasswordInput
            label="Confirmar senha"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Repita a senha"
            name="confirm_password"
          />

          {confirmPassword && !passwordsMatch && (
            <p className="text-sm text-red-500">As senhas não coincidem.</p>
          )}

          <button
            type="submit"
            disabled={isDisabled}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Criar Conta
          </button>
        </form>

        <div className="text-center mt-4">
          <button
            type="button"
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

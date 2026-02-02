import { useEffect, useState, useMemo } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import authService from "../services/authService";
import PasswordInput from "../components/PasswordInput";
import {
  validatePassword,
  isPasswordValid as isPasswordValidFn,
} from "../utils/passwordPolicy";

// 🔁 Mesmo componente usado no Register
function Rule({ ok, children }) {
  return (
    <li className={`text-sm ${ok ? "text-green-600" : "text-red-500"}`}>
      {ok ? "✓" : "✗"} {children}
    </li>
  );
}

export default function ResetPassword() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [passwordFocused, setPasswordFocused] = useState(false);

  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  // 🔐 Password policy
  const passwordChecks = useMemo(() => validatePassword(password), [password]);

  const isPasswordValid = isPasswordValidFn(passwordChecks);
  const passwordsMatch = password && password === confirmPassword;

  // 🔎 1) Validar token ao carregar
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

  // 💾 2) Enviar nova senha
  async function handleSubmit(e) {
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

  // ⏳ Validando token
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
  if (error && !done && !password) {
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

  const isDisabled =
    loading ||
    !password ||
    !confirmPassword ||
    !isPasswordValid ||
    !passwordsMatch;

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

        <form onSubmit={handleSubmit} className="space-y-4">
          <PasswordInput
            label="Nova senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onFocus={() => setPasswordFocused(true)}
            onBlur={() => setPasswordFocused(false)}
            placeholder="Crie uma senha segura"
          />

          {(passwordFocused || password) && (
            <ul className="bg-gray-50 border rounded p-3 space-y-1">
              <Rule ok={passwordChecks.minLength}>Mínimo de 8 caracteres</Rule>
              <Rule ok={passwordChecks.upper}>Uma letra maiúscula</Rule>
              <Rule ok={passwordChecks.lower}>Uma letra minúscula</Rule>
              <Rule ok={passwordChecks.digit}>Um número</Rule>
              <Rule ok={passwordChecks.special}>Um caractere especial</Rule>
            </ul>
          )}

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
            {loading ? "Salvando..." : "Redefinir senha"}
          </button>
        </form>
      </div>
    </div>
  );
}

import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../services/api";

export default function VerifyEmail() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const token = params.get("token");

  useEffect(() => {
    async function verify() {
      if (!token) {
        navigate("/verify-error");
        return;
      }

      try {
        await api.get(`/auth/verify-email?token=${token}`);
        navigate("/verify-success");
      } catch (err) {
        navigate("/verify-error");
      }
    }

    verify();
  }, [token, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md text-center">
        <h1 className="text-xl font-semibold mb-4">Validando email...</h1>
        <p className="text-gray-600">Aguarde alguns instantes.</p>
      </div>
    </div>
  );
}

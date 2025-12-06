import { useNavigate } from "react-router-dom";

export default function VerifySuccess() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-screen bg-green-50 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md text-center">
        <h1 className="text-3xl font-bold text-green-700 mb-4">
          Email verificado!
        </h1>

        <p className="text-gray-700 mb-6">
          Sua conta foi ativada com sucesso. Agora você já pode fazer login no
          sistema.
        </p>

        <button
          onClick={() => navigate("/login")}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Ir para Login
        </button>
      </div>
    </div>
  );
}

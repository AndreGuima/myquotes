import { useNavigate } from "react-router-dom";

export default function VerifyError() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-screen bg-red-50 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md text-center">
        <h1 className="text-3xl font-bold text-red-700 mb-4">
          Link inválido ou expirado
        </h1>

        <p className="text-gray-700 mb-6">
          Não foi possível validar seu email.  
          Talvez o link tenha sido usado antes ou já expirou.
        </p>

        <button
          onClick={() => navigate("/login")}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Voltar ao Login
        </button>
      </div>
    </div>
  );
}

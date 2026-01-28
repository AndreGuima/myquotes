import { useNavigate } from "react-router-dom";

export default function VerifyInstructions() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md text-center">
        <h1 className="text-3xl font-bold mb-4">Verifique seu email</h1>

        <p className="text-gray-700 mb-6">
          Enviamos um link de confirmação para o seu email. Clique no link para
          ativar sua conta antes de fazer login.
        </p>

        <p className="text-sm text-gray-500 mb-8">
          Caso não encontre, verifique sua caixa de spam ou lixeira.
        </p>

        {/* CTA */}
        <button
          type="button"
          onClick={() => navigate("/")}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Voltar para a página inicial
        </button>
      </div>
    </div>
  );
}

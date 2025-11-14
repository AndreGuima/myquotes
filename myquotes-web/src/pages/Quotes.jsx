import { useEffect, useState } from "react";
import { getQuotes, deleteQuote } from "../services/quotesService";
import { useNavigate } from "react-router-dom";

export default function Quotes() {
  const navigate = useNavigate();

  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadData() {
    try {
      setLoading(true);
      const data = await getQuotes();
      setQuotes(data);
    } catch (err) {
      setError("Erro ao carregar quotes");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleDelete(id) {
    if (!confirm("Tem certeza que deseja deletar esta frase?")) return;

    try {
      await deleteQuote(id);
      loadData();
    } catch (err) {
      alert("Erro ao deletar");
    }
  }

  if (loading) {
    return (
      <div className="p-4 text-gray-600 text-lg animate-pulse">
        Carregando quotes...
      </div>
    );
  }

  if (error) {
    return <div className="p-4 text-red-600 font-bold">{error}</div>;
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Quotes</h1>

        <button
          onClick={() => navigate("/quotes/new")}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Criar Quote
        </button>
      </div>

      {/* Tabela */}
      {quotes.length === 0 ? (
        <p className="text-gray-600">Nenhuma frase cadastrada.</p>
      ) : (
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="border-b bg-gray-100">
              <th className="p-3">Autor</th>
              <th className="p-3">Texto</th>
              <th className="p-3 w-32">Ações</th>
            </tr>
          </thead>
          <tbody>
            {quotes.map((q) => (
              <tr key={q.id} className="border-b">
                <td className="p-3">{q.author}</td>
                <td className="p-3">{q.text}</td>
                <td className="p-3 flex gap-2">
                  <button className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600">
                    Editar
                  </button>

                  <button
                    onClick={() => handleDelete(q.id)}
                    className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    Deletar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

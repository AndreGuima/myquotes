import { useEffect, useState, useCallback } from "react";
import { getQuotes, deleteQuote } from "../services/quotesService";
import { Link } from "react-router-dom";
import DataTable from "../components/DataTable";

export default function Quotes() {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const data = await getQuotes();
      setQuotes(data);
    } catch {
      setError("Erro ao carregar quotes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleDelete = async (id) => {
    if (!confirm("Tem certeza que deseja deletar esta frase?")) return;

    await deleteQuote(id);
    loadData();
  };

  if (loading) return <p>Carregando frases...</p>;
  if (error) return <p className="text-red-600">{error}</p>;

  return (
    <DataTable
      title="Gerenciar Quotes"
      createLabel="+ Criar Quote"
      createLink="/quotes/new"
      enableSearch={true}
      searchPlaceholder="Buscar por texto, autor ou criador..."
      searchKeys={["text", "author", "user_name"]}
      columns={[
        { key: "text", label: "Texto" },
        { key: "author", label: "Autor" },
        { key: "user_name", label: "Criado por" },
        { key: "actions", label: "Ações", width: 120 },
      ]}
      data={quotes}
      renderRow={(q) => (
        <tr key={q.id} className="border">
          <td className="p-2 border">{q.text}</td>
          <td className="p-2 border">{q.author}</td>
          <td className="p-2 border text-blue-700 font-medium">
            {q.user_name ?? "—"}
          </td>

          <td className="p-2 border flex gap-2">
            <Link
              to={`/quotes/${q.id}/edit`}
              className="px-2 py-1 bg-blue-500 text-white rounded"
            >
              Editar
            </Link>

            <button
              onClick={() => handleDelete(q.id)}
              className="px-2 py-1 bg-red-500 text-white rounded"
            >
              Remover
            </button>
          </td>
        </tr>
      )}
    />
  );
}

import { useEffect, useState, useCallback } from "react";
import quotesService from "../services/quotesService";
import { Link } from "react-router-dom";
import DataTable from "../components/DataTable";
import { notify, confirm } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

export default function Quotes() {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const data = await quotesService.list();
      setQuotes(data);
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao carregar quotes"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleDelete = (id) => {
    confirm({
      message: "Tem certeza que deseja remover esta quote?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",

      onConfirm: async () => {
        setProcessing(id);

        try {
          await quotesService.remove(id);
          notify.success("Quote removida com sucesso");
          loadData();
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover quote"));
        } finally {
          setProcessing(null);
        }
      },
    });
  };

  if (loading) {
    return <p className="p-4 themed-muted">Carregando frases...</p>;
  }

  return (
    <DataTable
      title="Gerenciar Quotes"
      createLabel="+ Criar Quote"
      createLink="/quotes/new"
      enableSearch
      searchPlaceholder="Buscar por texto, autor ou criador..."
      searchKeys={["text", "author", "user_name"]}
      columns={[
        { key: "text", label: "Texto" },
        { key: "author", label: "Autor" },
        { key: "user_name", label: "Criado por" },
        { key: "actions", label: "Ações", width: 140 },
      ]}
      data={quotes}
      renderRow={(q) => (
        <tr key={q.id} className="border themed-border">
          <td className="p-2 border themed-border">{q.text}</td>
          <td className="p-2 border themed-border">{q.author || "—"}</td>
          <td className="p-2 border themed-border themed-link font-medium">
            {q.user_name ?? "—"}
          </td>

          <td className="p-2 border themed-border flex gap-2">
            <Link
              to={`/quotes/${q.id}/edit`}
              className="px-2 py-1 bg-blue-500 text-white rounded"
            >
              Editar
            </Link>

            <button
              onClick={() => handleDelete(q.id)}
              disabled={processing === q.id}
              className="px-2 py-1 bg-red-500 text-white rounded disabled:opacity-50"
            >
              {processing === q.id ? "Removendo..." : "Remover"}
            </button>
          </td>
        </tr>
      )}
    />
  );
}

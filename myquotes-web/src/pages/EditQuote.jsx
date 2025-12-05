import { useEffect, useState, useCallback } from "react";
import { getQuoteById, updateQuote } from "../services/quotesService";
import { useNavigate, useParams } from "react-router-dom";

export default function EditQuote() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [author, setAuthor] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);

  const TEXT_LIMIT = 200;

  const loadData = useCallback(async () => {
    try {
      const q = await getQuoteById(id);
      setAuthor(q.author);
      setText(q.text);
    } catch {
      alert("Erro ao carregar quote");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await updateQuote(id, { author, text });
      navigate("/quotes");
    } catch {
      alert("Erro ao atualizar");
    }
  }

  if (loading) {
    return <div className="p-4 animate-pulse text-gray-600">Carregando...</div>;
  }

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Editar Quote</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">Texto</label>
          <textarea
            className="w-full border p-2 rounded"
            value={text}
            maxLength={TEXT_LIMIT}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            required
          ></textarea>
          <div className="text-right text-sm text-gray-500 mt-1">
            {text.length}/{TEXT_LIMIT}
          </div>
        </div>

        <div>
          <label className="block mb-1 font-medium">Autor</label>
          <input
            className="w-full border p-2 rounded"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
          />
        </div>

        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          Salvar Alterações
        </button>
      </form>
    </div>
  );
}

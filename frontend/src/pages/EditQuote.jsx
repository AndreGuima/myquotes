import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import quotesService from "../services/quotesService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const TEXT_LIMIT = 200;

export default function EditQuote() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [author, setAuthor] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);

  // ============================
  // 📥 Carregar quote
  // ============================
  useEffect(() => {
    async function loadData() {
      try {
        const q = await quotesService.get(id);
        setAuthor(q.author ?? "");
        setText(q.text ?? "");
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar quote"));
        navigate("/quotes");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id, navigate]);

  // ============================
  // 💾 Salvar alterações
  // ============================
  async function handleSubmit(e) {
    e.preventDefault();

    try {
      await quotesService.update(id, { author, text });
      navigate("/quotes");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar alterações"));
    }
  }

  // ============================
  // ⏳ Loading
  // ============================
  if (loading) {
    return <div className="p-4 animate-pulse text-gray-600">Carregando...</div>;
  }

  // ============================
  // 📝 Formulário
  // ============================
  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Editar Quote</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Texto */}
        <div>
          <label className="block mb-1 font-medium">Texto</label>
          <textarea
            className="w-full border p-2 rounded"
            value={text}
            maxLength={TEXT_LIMIT}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            required
          />
          <div className="text-right text-sm text-gray-500 mt-1">
            {text.length}/{TEXT_LIMIT}
          </div>
        </div>

        {/* Autor */}
        <div>
          <label className="block mb-1 font-medium">Autor</label>
          <input
            className="w-full border p-2 rounded"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            placeholder="Autor (opcional)"
          />
        </div>

        {/* Ações */}
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={() => navigate("/quotes")}
            className="px-4 py-2 rounded border text-gray-600 hover:bg-gray-100"
          >
            Cancelar
          </button>

          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Salvar Alterações
          </button>
        </div>
      </form>
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
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
  const [saving, setSaving] = useState(false);
  const isTextValid = text.trim().length > 0;

  // ============================
  // 📥 Carregar quote
  // ============================
  useEffect(() => {
    async function loadData() {
      try {
        const q = await quotesService.getById(id);
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
    setSaving(true);

    try {
      await quotesService.update(id, { author, text });
      navigate("/quotes");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar alterações"));
    } finally {
      setSaving(false);
    }
  }

  // ============================
  // ⏳ Loading
  // ============================
  if (loading) {
    return (
      <div className="p-6 max-w-xl mx-auto themed-muted">
        Carregando quote...
      </div>
    );
  }

  // ============================
  // 📝 Formulário
  // ============================
  return (
    <div className="p-6 max-w-xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Editar Quote</h1>
        <Link
          to="/quotes"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Frases
        </Link>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 themed-card themed-border border rounded-xl p-5"
      >
        {/* Texto */}
        <div>
          <label className="block mb-1 font-medium">Texto</label>
          <textarea
            className="w-full themed-input p-2 rounded"
            value={text}
            maxLength={TEXT_LIMIT}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            required
          />
          <div className="text-right text-sm themed-muted mt-1">
            {text.length}/{TEXT_LIMIT}
          </div>
        </div>

        {/* Autor */}
        <div>
          <label className="block mb-1 font-medium">Autor</label>
          <input
            className="w-full themed-input p-2 rounded"
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
            className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90 transition"
          >
            Cancelar
          </button>

          <button
            type="submit"
            disabled={saving || !isTextValid}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Salvando..." : "Salvar Alterações"}
          </button>
        </div>
      </form>
    </div>
  );
}

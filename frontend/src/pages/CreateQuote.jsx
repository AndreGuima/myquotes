import { useState } from "react";
import quotesService from "../services/quotesService";
import { notify } from "../core/toast";
import { useNavigate } from "react-router-dom";

export default function CreateQuote() {
  const navigate = useNavigate();
  const [author, setAuthor] = useState("");
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const TEXT_LIMIT = 200;
  const isTextValid = text.trim().length > 0;

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = { text };
      if (author.trim() !== "") {
        payload.author = author;
      }
      await quotesService.create(payload);
      navigate("/quotes/");
    } catch {
      notify.error("Erro ao criar quote. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Criar Quote</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">Texto</label>
          <textarea
            className="w-full border p-2 rounded"
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={TEXT_LIMIT}
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
            placeholder="Autor (opcional)"
          />
        </div>

        <button
          disabled={loading || !isTextValid}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Salvando..." : "Salvar"}
        </button>
      </form>
    </div>
  );
}

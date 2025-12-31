import { useEffect, useState } from "react";
import {
  getPreferences,
  updatePreferences,
} from "../services/preferencesService";

export default function Preferences() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [receiveDailyQuote, setReceiveDailyQuote] = useState(true);
  const [dailyQuoteTime, setDailyQuoteTime] = useState("08:00");

  useEffect(() => {
    async function load() {
      try {
        const data = await getPreferences("quotes");

        setReceiveDailyQuote(data.preferences.receive_daily_quote ?? true);

        setDailyQuoteTime(data.preferences.daily_quote_time ?? "08:00");
      } catch (err) {
        console.error("Erro ao carregar preferências", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);

    try {
      await updatePreferences("quotes", {
        receive_daily_quote: receiveDailyQuote,
        daily_quote_time: dailyQuoteTime,
      });

      alert("Preferências salvas com sucesso!");
    } catch {
      alert("Erro ao salvar preferências");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p>Carregando preferências...</p>;

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Preferências</h1>

      <form onSubmit={handleSave} className="space-y-6">
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={receiveDailyQuote}
            onChange={(e) => setReceiveDailyQuote(e.target.checked)}
          />
          <span>Receber quote diária por email</span>
        </label>

        <div>
          <label className="block mb-1 font-medium">Horário de envio</label>
          <input
            type="time"
            className="border p-2 rounded"
            value={dailyQuoteTime}
            onChange={(e) => setDailyQuoteTime(e.target.value)}
            disabled={!receiveDailyQuote}
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Salvando..." : "Salvar"}
        </button>
      </form>
    </div>
  );
}

import { useEffect, useState } from "react";
import preferencesService from "../services/preferencesService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";
import { useTheme } from "../contexts/useTheme";

export default function Preferences() {
  const { theme, setTheme } = useTheme();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [receiveDailyQuote, setReceiveDailyQuote] = useState(true);
  const [dailyQuoteTime, setDailyQuoteTime] = useState("08:00");
  const [selectedTheme, setSelectedTheme] = useState(theme);

  useEffect(() => {
    async function load() {
      try {
        const [quotesData, themeData] = await Promise.all([
          preferencesService.get("quotes"),
          preferencesService.get("theme"),
        ]);

        const prefs = quotesData?.preferences ?? {};
        const themePrefs = themeData?.preferences ?? {};

        setReceiveDailyQuote(prefs.receive_daily_quote ?? true);
        setDailyQuoteTime(prefs.daily_quote_time ?? "08:00");
        setSelectedTheme(themePrefs.theme ?? theme);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar preferências"));
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [theme]);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);

    try {
      const normalizedTheme = setTheme(selectedTheme);

      await Promise.all([
        preferencesService.update("quotes", {
          receive_daily_quote: receiveDailyQuote,
          daily_quote_time: dailyQuoteTime,
        }),
        preferencesService.update("theme", {
          theme: normalizedTheme,
        }),
      ]);

      notify.success("Preferências salvas com sucesso");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar preferências"));
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
            className="themed-input p-2 rounded"
            value={dailyQuoteTime}
            onChange={(e) => setDailyQuoteTime(e.target.value)}
            disabled={!receiveDailyQuote}
          />
        </div>

        <div>
          <label htmlFor="theme" className="block mb-1 font-medium">
            Tema da interface
          </label>
          <select
            id="theme"
            className="themed-input p-2 rounded w-full max-w-xs"
            value={selectedTheme}
            onChange={(e) => setSelectedTheme(e.target.value)}
          >
            <option value="light">Claro</option>
            <option value="dark">Escuro</option>
            <option value="ocean">Oceano</option>
          </select>
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

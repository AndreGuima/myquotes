import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import habitsService from "../services/habitsService";
import HabitHeatmap from "../components/HabitHeatmap";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

function formatDateLabel(dateStr) {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const isSameDay = (a, b) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  if (isSameDay(date, today)) return "Hoje";
  if (isSameDay(date, yesterday)) return "Ontem";

  return date.toLocaleDateString("pt-BR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
  });
}

function formatFullDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export default function EditHabit() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [frequencyType, setFrequencyType] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [showHistory, setShowHistory] = useState(false);

  // ============================
  // 📥 Carregar hábito
  // ============================
  useEffect(() => {
    async function load() {
      try {
        const habits = await habitsService.list();
        const habit = habits.find((h) => h.id === Number(id));

        if (!habit) {
          setError("Hábito não encontrado");
          return;
        }

        setTitle(habit.title);
        setFrequencyType(habit.frequency_type);
      } catch {
        setError("Erro ao carregar hábito");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  // ============================
  // 📅 Carregar histórico
  // ============================
  useEffect(() => {
    async function loadHistory() {
      try {
        const data = await habitsService.history(id);
        const sortedDays = [...(data.days || [])].sort(
          (a, b) => new Date(b.date) - new Date(a.date),
        );
        setHistory(sortedDays);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar histórico"));
      } finally {
        setLoadingHistory(false);
      }
    }

    loadHistory();
  }, [id]);

  // ============================
  // 💾 Salvar alteração
  // ============================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      await habitsService.update(id, { title });
      navigate("/habits");
    } catch {
      setError("Erro ao atualizar hábito");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-xl mx-auto text-gray-600">
        Carregando hábito...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Editar Hábito</h1>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-xl mx-auto space-y-10">
      {/* ===================== */}
      {/* ✏️ Formulário */}
      {/* ===================== */}
      <div>
        <h1 className="text-3xl font-bold mb-6">Editar Hábito</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Nome do hábito
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Frequência</label>
            <input
              type="text"
              value={
                frequencyType === "daily"
                  ? "Diário"
                  : frequencyType === "weekly"
                    ? "Semanal"
                    : ""
              }
              disabled
              className="w-full border rounded px-3 py-2 bg-gray-100 text-gray-600"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => navigate("/habits")}
              className="px-4 py-2 border rounded"
              disabled={saving}
            >
              Cancelar
            </button>

            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
            >
              {saving ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </form>
      </div>

      {/* ===================== */}
      {/* 🔥 Heatmap (visão rápida) */}
      {/* ===================== */}
      <div>
        <h2 className="text-xl font-semibold mb-3">Consistência</h2>

        <HabitHeatmap habitId={id} />
      </div>

      {/* ===================== */}
      {/* 📜 Histórico (colapsado) */}
      {/* ===================== */}
      <div>
        <button
          onClick={() => setShowHistory((v) => !v)}
          className="text-sm text-blue-600 hover:underline mb-3"
        >
          {showHistory
            ? "Ocultar histórico detalhado ▲"
            : "Ver histórico detalhado ▼"}
        </button>

        {showHistory && (
          <>
            {loadingHistory ? (
              <p className="text-gray-600">Carregando histórico…</p>
            ) : history.length === 0 ? (
              <p className="text-gray-500">Nenhum registro ainda.</p>
            ) : (
              <ul className="space-y-2">
                {history.map((day) => (
                  <li
                    key={day.date}
                    className="relative group flex items-center justify-between border rounded px-3 py-2 hover:bg-gray-50"
                  >
                    <span className="text-gray-700">
                      {formatDateLabel(day.date)}
                    </span>

                    <span
                      className={`font-medium ${
                        day.completed ? "text-green-600" : "text-gray-400"
                      }`}
                    >
                      {day.completed ? "✔ Feito" : "✖ Não feito"}
                    </span>

                    {/* Tooltip */}
                    <div
                      className="
                        pointer-events-none
                        absolute right-0 top-full mt-2
                        w-64 rounded-lg bg-gray-900 text-white text-sm
                        px-3 py-2 shadow-lg
                        opacity-0 scale-95
                        group-hover:opacity-100 group-hover:scale-100
                        transition-all duration-150
                        z-20
                      "
                    >
                      <div className="font-medium mb-1">
                        {formatFullDate(day.date)}
                      </div>
                      <div>
                        Status:{" "}
                        <span className="font-semibold">
                          {day.completed ? "Feito" : "Não feito"}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    </div>
  );
}

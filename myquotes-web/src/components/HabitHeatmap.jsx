import { useEffect, useState } from "react";
import habitsService from "../services/habitsService";

function getColor(completed) {
  if (!completed) return "bg-gray-200";
  return "bg-green-500";
}

export default function HabitHeatmap({
  habitId,
  days = 90, // últimos 3 meses
}) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await habitsService.history(habitId);
        const sliced = (data.days || []).slice(-days);
        setHistory(sliced);
      } catch (err) {
        console.error("Erro ao carregar heatmap", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [habitId, days]);

  if (loading) {
    return (
      <div className="grid grid-cols-14 gap-1">
        {Array.from({ length: days }).map((_, i) => (
          <div key={i} className="w-3 h-3 rounded bg-gray-200 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-14 gap-1">
      {history.map((day) => (
        <div key={day.date} className="relative group">
          {/* Célula */}
          <div className={`w-3 h-3 rounded ${getColor(day.completed)}`} />

          {/* Tooltip */}
          <div
            className="
              pointer-events-none
              absolute bottom-full left-1/2 -translate-x-1/2 mb-2
              w-44 rounded-md bg-gray-900 text-white text-xs
              px-2 py-1 shadow-lg
              opacity-0 scale-95
              group-hover:opacity-100 group-hover:scale-100
              transition-all duration-150
              z-20
            "
          >
            <div className="font-medium">
              {new Date(day.date).toLocaleDateString("pt-BR", {
                weekday: "long",
                day: "2-digit",
                month: "long",
                year: "numeric",
              })}
            </div>
            <div className="mt-1">
              {day.completed ? "✔ Feito" : "✖ Não feito"}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

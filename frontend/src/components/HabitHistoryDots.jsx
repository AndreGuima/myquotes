import { useEffect, useState } from "react";
import habitsService from "../services/habitsService";

function formatFullDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

export default function HabitHistoryDots({
  habitId,
  days = 14, // 7, 14 ou 30
}) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await habitsService.history(habitId);
        const sliced = (data.days || []).slice(-days); // últimos N dias
        setHistory(sliced);
      } catch (err) {
        console.error("Erro ao carregar histórico", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [habitId, days]);

  // Skeleton
  if (loading) {
    return (
      <div className="flex gap-1">
        {Array.from({ length: days }).map((_, i) => (
          <div key={i} className="w-3 h-3 rounded bg-gray-200 animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex gap-1 items-center">
      {history.map((day) => (
        <div key={day.date} className="relative group">
          {/* Quadradinho */}
          <div
            className={`
              w-3 h-3 rounded
              ${day.completed ? "bg-green-500" : "bg-gray-300"}
            `}
          />

          {/* Tooltip rico */}
          <div
            className="
              pointer-events-none
              absolute bottom-full left-1/2 -translate-x-1/2 mb-2
              w-48 rounded-lg bg-gray-900 text-white text-xs
              px-2 py-1 shadow-lg
              opacity-0 scale-95
              group-hover:opacity-100 group-hover:scale-100
              transition-all duration-150
              z-20
            "
          >
            <div className="font-medium">{formatFullDate(day.date)}</div>
            <div className="mt-1">
              Status:{" "}
              <span className="font-semibold">
                {day.completed ? "✔ Feito" : "✖ Não feito"}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

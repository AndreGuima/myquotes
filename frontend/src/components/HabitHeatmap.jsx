import { useEffect, useState } from "react";
import habitsService from "../services/habitsService";
import { notify } from "../core/toast";

/**
 * Heatmap binário:
 * 0 = não feito
 * 1 = feito
 */
function getColor(count) {
  return count === 1 ? "bg-green-500" : "bg-gray-200";
}

export default function HabitHeatmap({ habitId, days = 90 }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await habitsService.heatmap(habitId, days);
        setData(res);
      } catch (err) {
        notify.error("Erro ao carregar heatmap");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [habitId, days]);

  // ⏳ Skeleton
  if (loading) {
    return (
      <div className="grid grid-cols-7 gap-1">
        {Array.from({ length: days }).map((_, i) => (
          <div key={i} className="w-3 h-3 rounded bg-gray-200 animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="grid grid-cols-7 gap-1">
      {data.days.map((day) => (
        <div key={day.date} className="relative group">
          {/* Quadrado */}
          <div className={`w-3 h-3 rounded ${getColor(day.count)}`} />

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
              Status: <strong>{day.count === 1 ? "Feito" : "Não feito"}</strong>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

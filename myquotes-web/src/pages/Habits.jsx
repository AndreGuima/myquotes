import { useEffect, useState } from "react";
import habitsService from "../services/habitsService";

export default function Habits() {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null);

  async function loadHabits() {
    try {
      const data = await habitsService.list();

      // Para cada hábito, buscamos stats
      const withStats = await Promise.all(
        data.map(async (h) => {
          const stats = await habitsService.stats(h.id);
          return { ...h, stats };
        }),
      );

      setHabits(withStats);
    } catch (err) {
      console.error("Erro ao carregar hábitos", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHabits();
  }, []);

  async function handleToggle(habitId) {
    setToggling(habitId);

    try {
      const result = await habitsService.toggle(habitId);

      setHabits((prev) =>
        prev.map((h) =>
          h.id === habitId
            ? {
                ...h,
                stats: result.stats,
              }
            : h,
        ),
      );
    } catch (err) {
      alert("Erro ao marcar hábito");
      console.error(err);
    } finally {
      setToggling(null);
    }
  }

  if (loading) {
    return <p className="p-4 text-gray-600">Carregando hábitos…</p>;
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Meus Hábitos</h1>

      {habits.length === 0 ? (
        <p className="text-gray-600">
          Você ainda não possui hábitos cadastrados.
        </p>
      ) : (
        <div className="space-y-4">
          {habits.map((habit) => {
            const completed = habit.stats?.today_completed;

            return (
              <div
                key={habit.id}
                className="
                  flex items-center justify-between
                  border rounded-lg p-4
                  shadow-sm
                "
              >
                <div>
                  <h2 className="text-lg font-semibold">{habit.title}</h2>

                  <div className="text-sm text-gray-600 mt-1">
                    🔥 Streak atual:{" "}
                    <span className="font-medium">
                      {habit.stats?.current_streak ?? 0}
                    </span>
                    {" · "}⭐ Melhor streak:{" "}
                    <span className="font-medium">
                      {habit.stats?.best_streak ?? 0}
                    </span>
                  </div>

                  {habit.frequency_type === "weekly" && (
                    <div className="text-sm text-gray-600 mt-1">
                      📅 Semana: {habit.stats.weekly_completed}/
                      {habit.stats.weekly_target}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleToggle(habit.id)}
                  disabled={toggling === habit.id}
                  className={`
                    px-4 py-2 rounded-lg font-medium
                    transition
                    ${
                      completed
                        ? "bg-green-600 text-white hover:bg-green-700"
                        : "bg-gray-200 text-gray-800 hover:bg-gray-300"
                    }
                  `}
                >
                  {toggling === habit.id
                    ? "Salvando..."
                    : completed
                      ? "✔ Feito hoje"
                      : "Marcar hoje"}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

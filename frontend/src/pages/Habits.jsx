import { useEffect, useState } from "react";
import habitsService from "../services/habitsService";
import { Link } from "react-router-dom";
import { notify, confirm } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

export default function Habits() {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null);
  const [removing, setRemoving] = useState(null);

  async function loadHabits() {
    try {
      const data = await habitsService.list();

      const withStats = await Promise.all(
        data.map(async (h) => {
          const stats = await habitsService.stats(h.id);
          return { ...h, stats };
        }),
      );

      setHabits(withStats);
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao carregar hábitos"));
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
        prev.map((h) => (h.id === habitId ? { ...h, stats: result.stats } : h)),
      );
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao atualizar hábito"));
    } finally {
      setToggling(null);
    }
  }

  function handleRemove(habitId) {
    confirm({
      message: "Tem certeza que deseja remover este hábito?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",

      onConfirm: async () => {
        setRemoving(habitId);

        try {
          await habitsService.update(habitId, { is_active: false });

          setHabits((prev) => prev.filter((h) => h.id !== habitId));

          notify.success("Hábito removido com sucesso");
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover hábito"));
        } finally {
          setRemoving(null);
        }
      },
    });
  }

  if (loading) {
    return <p className="p-4 text-gray-600">Carregando hábitos…</p>;
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Meus Hábitos</h1>

        {habits.length > 0 && (
          <Link
            to="/habits/new"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + Novo Hábito
          </Link>
        )}
      </div>

      {/* Empty state */}
      {habits.length === 0 ? (
        <div className="text-gray-600 mt-10 text-center">
          <p className="mb-4">Você ainda não possui hábitos cadastrados.</p>
          <Link
            to="/habits/new"
            className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Criar meu primeiro hábito
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {habits.map((habit) => {
            const completed = habit.stats?.today_completed;

            return (
              <div
                key={habit.id}
                className="flex items-center justify-between border rounded-lg p-4 shadow-sm"
              >
                {/* Info */}
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
                      {habit.target_per_week}
                    </div>
                  )}

                  {/* Secondary actions */}
                  <div className="flex gap-4 mt-2 text-sm">
                    <Link
                      to={`/habits/${habit.id}/edit`}
                      className="text-blue-600 hover:underline"
                    >
                      Editar
                    </Link>

                    <button
                      onClick={() => handleRemove(habit.id)}
                      disabled={removing === habit.id}
                      className="text-red-600 hover:underline disabled:opacity-50"
                    >
                      {removing === habit.id ? "Removendo..." : "Remover"}
                    </button>
                  </div>
                </div>

                {/* Primary action */}
                <button
                  onClick={() => handleToggle(habit.id)}
                  disabled={toggling === habit.id}
                  className={`
                    px-4 py-2 rounded-lg font-medium transition
                    ${
                      completed
                        ? "bg-green-600 text-white hover:bg-green-700"
                        : "bg-gray-200 text-gray-800 hover:bg-gray-300"
                    }
                    ${toggling === habit.id ? "opacity-60 cursor-not-allowed" : ""}
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

import { useEffect, useState } from "react";
import habitsService from "../services/habitsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

export default function HabitHistorySummary({ habit }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const history = await habitsService.history(habit.id);

        const days = history.days;
        const total = days.length;
        const completed = days.filter((d) => d.completed).length;

        // streak atual (de trás pra frente)
        let streak = 0;
        for (let i = days.length - 1; i >= 0; i--) {
          if (days[i].completed) streak++;
          else break;
        }

        setSummary({
          total,
          completed,
          streak,
        });
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar histórico"));
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [habit.id]);

  if (loading) {
    return <div className="text-sm themed-muted">Carregando histórico…</div>;
  }

  if (!summary || summary.total === 0) {
    return <div className="text-sm themed-muted">Nenhum histórico ainda</div>;
  }

  return (
    <div className="text-sm themed-muted mt-2 space-y-1">
      <div>
        ✔️ {summary.completed} / {summary.total} dias
      </div>

      <div>
        🔥 Streak atual: <span className="font-medium">{summary.streak}</span>
      </div>
    </div>
  );
}

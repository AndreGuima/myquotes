import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import dreamsService from "../services/dreamsService";
import habitsService from "../services/habitsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

function toDateLabel(date) {
  if (!date) return "Sem data";
  return new Date(`${date}T00:00:00`).toLocaleDateString("pt-BR");
}

function toMoneyLabel(value) {
  if (value == null || value === "") return "Não informado";
  return Number(value).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function toTimestamp(value) {
  const ts = new Date(value || "").getTime();
  return Number.isFinite(ts) ? ts : 0;
}

function sortByDate(items) {
  return [...items].sort((a, b) => {
    if (!a.targetDate && !b.targetDate) return 0;
    if (!a.targetDate) return 1;
    if (!b.targetDate) return -1;
    return toTimestamp(a.targetDate) - toTimestamp(b.targetDate);
  });
}

function isMilestoneCompleted(milestone) {
  return (
    Boolean(milestone?.completedAt) ||
    Number(milestone?.progressPercent ?? 0) >= 100
  );
}

export default function DreamDetails() {
  const { id } = useParams();
  const [dream, setDream] = useState(null);
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [dreamData, habitsData] = await Promise.all([
          dreamsService.getById(id),
          habitsService.list({ include_stats: true }),
        ]);
        setDream(dreamData);
        setHabits(Array.isArray(habitsData) ? habitsData : []);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar sonho"));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id]);

  const habitNames = useMemo(() => {
    const byId = new Map(habits.map((habit) => [habit.id, habit.title]));
    return (dream?.linkedHabitIds || []).map((habitId) => ({
      id: habitId,
      title: byId.get(habitId) || `Hábito #${habitId}`,
    }));
  }, [habits, dream]);

  if (loading) {
    return <p className="p-4 themed-muted">Carregando sonho...</p>;
  }

  if (!dream) {
    return <p className="p-4 themed-muted">Sonho não encontrado.</p>;
  }

  return (
    <div className="dreams-page p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Detalhes do Sonho</h1>
        <Link
          to="/dreams"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Sonhos
        </Link>
      </div>

      <section className="themed-card themed-border border rounded-xl p-5 mb-5">
        <h2 className="text-2xl font-semibold">{dream.title}</h2>
        <p className="themed-muted mt-2">
          {dream.description || "Sem descrição"}
        </p>
      </section>

      <section className="themed-card themed-border border rounded-xl p-5 mb-5">
        <h3 className="text-xl font-semibold mb-3">SMART</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          <div>
            <strong>S:</strong> {dream.smart?.specific || "Não informado"}
          </div>
          <div>
            <strong>M:</strong> {dream.smart?.measurable || "Não informado"}
          </div>
          <div>
            <strong>A:</strong> {dream.smart?.achievable || "Não informado"}
          </div>
          <div>
            <strong>R:</strong> {dream.smart?.relevant || "Não informado"}
          </div>
          <div>
            <strong>T:</strong> {dream.smart?.timeBound || "Não informado"}
          </div>
          <div>
            <strong>Data alvo:</strong> {toDateLabel(dream.smart?.targetDate)}
          </div>
          <div>
            <strong>Meta financeira:</strong>{" "}
            {toMoneyLabel(dream.smart?.financialTargetValue)}
          </div>
        </div>
      </section>

      <section className="themed-card themed-border border rounded-xl p-5 mb-5">
        <h3 className="text-xl font-semibold mb-3">Hábitos vinculados</h3>
        {habitNames.length === 0 ? (
          <p className="themed-muted">Nenhum hábito vinculado.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {habitNames.map((habit) => (
              <span
                key={habit.id}
                className="text-xs px-2 py-1 rounded-full themed-subtle themed-border border"
              >
                {habit.title}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="themed-card themed-border border rounded-xl p-5">
        <h3 className="text-xl font-semibold mb-3">Timeline de marcos</h3>
        {dream.milestones?.length ? (
          <div className="space-y-3">
            {sortByDate(dream.milestones).map((milestone) => (
              <div
                key={milestone.id}
                className="themed-border border rounded-lg p-4 relative overflow-hidden"
              >
                <div
                  className="absolute inset-y-0 left-0 bg-blue-500/15 pointer-events-none"
                  style={{
                    width: `${Math.min(
                      100,
                      Math.max(0, Number(milestone.progressPercent ?? 0)),
                    )}%`,
                  }}
                />

                <div className="relative z-10">
                  <div className="font-medium">{milestone.title}</div>
                  <div className="text-sm themed-muted mt-1">
                    Previsto: {toDateLabel(milestone.targetDate)}
                  </div>
                  <div className="text-sm themed-muted mt-1">
                    Meta do marco:{" "}
                    {toMoneyLabel(milestone.financialTargetValue)}
                  </div>
                  <div className="text-sm themed-muted mt-1">
                    Realizado:{" "}
                    {Number(milestone.progressPercent ?? 0).toFixed(2)}%
                  </div>
                  <div className="mt-2 h-1.5 bg-[var(--line-color)] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{
                        width: `${Math.min(
                          100,
                          Math.max(0, Number(milestone.progressPercent ?? 0)),
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="text-sm themed-muted mt-2">
                    Status:{" "}
                    {isMilestoneCompleted(milestone) ? "Concluído" : "Pendente"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="themed-muted">Nenhum marco cadastrado.</p>
        )}
      </section>
    </div>
  );
}

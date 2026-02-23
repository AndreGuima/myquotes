import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import quotesService from "../services/quotesService";
import habitsService from "../services/habitsService";
import HabitHistorySummary from "../components/HabitHistorySummary";
import HabitHeatmap from "../components/HabitHeatmap";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";
import { useAuth } from "../contexts/useAuth";
import { isHabitScheduledForDate } from "../utils/habitSchedule";

// ============================
// 🧠 Ordenação por prioridade
// ============================
function sortHabitsByPriority(habits) {
  return [...habits].sort((a, b) => {
    const aDone = a.stats?.today_completed ?? false;
    const bDone = b.stats?.today_completed ?? false;

    // 1️⃣ Não feitos hoje primeiro
    if (aDone !== bDone) {
      return aDone ? 1 : -1;
    }

    // 2️⃣ Maior streak primeiro
    const aStreak = a.stats?.current_streak ?? 0;
    const bStreak = b.stats?.current_streak ?? 0;

    return bStreak - aStreak;
  });
}

function formatTimeRange(startTime, endTime) {
  if (!startTime) return "Sem horário";
  const start = startTime.slice(0, 5);
  const end = endTime ? endTime.slice(0, 5) : null;
  return end ? `${start}–${end}` : start;
}

function formatQuoteCreatedAt(value) {
  if (!value) return "Data não informada";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Data não informada";
  return date.toLocaleDateString("pt-BR");
}

function isHabitForToday(habit) {
  return isHabitScheduledForDate(habit, new Date());
}

export default function Home() {
  const [quote, setQuote] = useState(null);
  const [loadingQuote, setLoadingQuote] = useState(true);

  const [habits, setHabits] = useState([]);
  const [loadingHabits, setLoadingHabits] = useState(true);

  const { user } = useAuth();

  // ============================
  // ✨ Quote do Dia
  // ============================
  useEffect(() => {
    if (!user) {
      setLoadingQuote(false);
      return;
    }

    async function loadQuote() {
      try {
        const q = await quotesService.getQuoteOfTheDay();
        setQuote(q);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar quote do dia"));
      } finally {
        setLoadingQuote(false);
      }
    }

    loadQuote();
  }, [user]);

  // ============================
  // 📅 Hábitos + stats
  // ============================
  useEffect(() => {
    async function loadHabits() {
      try {
        const data = await habitsService.list({ include_stats: true });
        setHabits(data);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar hábitos"));
      } finally {
        setLoadingHabits(false);
      }
    }

    loadHabits();
  }, []);

  const todayHabits = sortHabitsByPriority(habits.filter(isHabitForToday));

  // ============================
  // ⏳ Loading inicial
  // ============================
  if (loadingQuote) {
    return (
      <div className="animate-pulse p-6 max-w-5xl mx-auto">
        <div className="h-6 bg-[var(--line-color)] rounded w-48 mb-6"></div>
        <div className="h-24 bg-[var(--line-color)] rounded"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Home</h1>

      {/* ============================
          ✨ Quote do Dia
      ============================ */}
      {quote ? (
        <div className="p-6 bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-xl rounded-xl mb-10">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold mb-3">✨ Quote do Dia</h2>
              <p className="text-2xl italic mb-3">"{quote.text}"</p>
              <div className="font-light">— {quote.author}</div>
              <p className="text-sm text-blue-100 mt-2">
                Cadastrada em: {formatQuoteCreatedAt(quote.created_at)}
              </p>
            </div>

            <Link
              to="/quotes"
              className="inline-flex items-center justify-center bg-white text-blue-700 px-4 py-2 rounded hover:bg-blue-50 font-medium whitespace-nowrap h-fit"
            >
              Ir para Frases
            </Link>
          </div>
        </div>
      ) : (
        <p className="themed-muted mb-10">
          Você ainda não possui quotes cadastradas.
          <Link to="/quotes/new" className="themed-link underline ml-1">
            Criar agora →
          </Link>
        </p>
      )}

      <div className="mb-8 border themed-border rounded-xl themed-card p-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">
            Módulo de Metas e Conquistas
          </h2>
          <p className="themed-muted text-sm mt-1">
            Planeje metas com método SMART, marcos em timeline e vínculo com
            hábitos para acompanhar suas conquistas.
          </p>
        </div>
        <Link
          to="/dreams"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 whitespace-nowrap"
        >
          Abrir Metas e Conquistas
        </Link>
      </div>

      <div className="mb-8 border themed-border rounded-xl themed-card p-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Módulo de Finanças</h2>
          <p className="themed-muted text-sm mt-1">
            Gerencie patrimônio, despesas e investimentos em um só lugar.
          </p>
        </div>
        <Link
          to="/finances"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 whitespace-nowrap"
        >
          Abrir Finanças
        </Link>
      </div>

      <div className="mb-8 border themed-border rounded-xl themed-card p-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Gerenciamento do Dia</h2>
          <p className="themed-muted text-sm mt-1">
            Organize sua rotina diária e acompanhe atividades do dia em um só
            lugar.
          </p>
        </div>
        <a
          href="http://localhost:5173/day-management"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 whitespace-nowrap"
        >
          Abrir Gerenciamento do Dia
        </a>
      </div>

      {/* ============================
          📅 Seus hábitos
      ============================ */}
      <div>
        <h2 className="text-2xl font-bold mb-4">📅 Seus hábitos</h2>

        {loadingHabits ? (
          <p className="themed-muted">Carregando hábitos…</p>
        ) : todayHabits.length === 0 ? (
          <p className="themed-muted">
            Você não possui hábitos programados para hoje.
          </p>
        ) : (
          <div
            className="
              grid
              grid-cols-1
              sm:grid-cols-2
              lg:grid-cols-3
              gap-4
            "
          >
            {todayHabits.map((habit) => (
              <div
                key={habit.id}
                className="
                  border
                  themed-border
                  rounded-lg
                  p-4
                  themed-card
                  hover:shadow-md
                  transition
                "
              >
                {/* Título */}
                <Link
                  to={`/habits/${habit.id}/edit`}
                  className="text-lg font-semibold themed-link hover:underline"
                >
                  {habit.title}
                </Link>

                <div className="text-xs themed-muted mt-1">
                  ⏰ {formatTimeRange(habit.start_time, habit.end_time)}
                </div>

                {/* Badge pendente */}
                {!habit.stats?.today_completed && (
                  <div className="text-xs text-red-500 font-medium mt-1">
                    • pendente hoje
                  </div>
                )}

                {/* Resumo */}
                <div className="mt-2">
                  <HabitHistorySummary habit={habit} />
                </div>

                {/* Heatmap binário */}
                <div className="mt-3">
                  <div className="text-xs themed-muted mb-1">
                    Últimos 30 dias
                  </div>
                  <HabitHeatmap habitId={habit.id} days={30} />
                </div>

                {/* CTA */}
                <div className="mt-3 text-sm">
                  <Link
                    to={`/habits/${habit.id}/edit`}
                    className="themed-muted hover:text-blue-600 hover:underline"
                  >
                    Ver histórico →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

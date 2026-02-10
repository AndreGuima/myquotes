import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import quotesService from "../services/quotesService";
import habitsService from "../services/habitsService";
import HabitHistorySummary from "../components/HabitHistorySummary";
import HabitHeatmap from "../components/HabitHeatmap";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";
import { useAuth } from "../contexts/useAuth";

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

  // ============================
  // ⏳ Loading inicial
  // ============================
  if (loadingQuote) {
    return (
      <div className="animate-pulse p-6 max-w-5xl mx-auto">
        <div className="h-6 bg-gray-300 rounded w-48 mb-6"></div>
        <div className="h-24 bg-gray-300 rounded"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      <div className="mb-8 border rounded-xl bg-white p-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Módulo de Sonhos SMART</h2>
          <p className="text-gray-600 text-sm mt-1">
            Planeje sonhos com metas SMART, marcos em timeline e vínculo com
            hábitos.
          </p>
        </div>
        <Link
          to="/dreams"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 whitespace-nowrap"
        >
          Abrir Sonhos
        </Link>
      </div>

      {/* ============================
          ✨ Quote do Dia
      ============================ */}
      {quote ? (
        <div className="p-6 bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-xl rounded-xl mb-10">
          <h2 className="text-lg font-semibold mb-3">✨ Quote do Dia</h2>
          <p className="text-2xl italic mb-3">"{quote.text}"</p>
          <span className="font-light">— {quote.author}</span>
        </div>
      ) : (
        <p className="text-gray-700 mb-10">
          Você ainda não possui quotes cadastradas.
          <Link to="/quotes/new" className="text-blue-600 underline ml-1">
            Criar agora →
          </Link>
        </p>
      )}

      {/* ============================
          📅 Seus hábitos
      ============================ */}
      <div>
        <h2 className="text-2xl font-bold mb-4">📅 Seus hábitos</h2>

        {loadingHabits ? (
          <p className="text-gray-500">Carregando hábitos…</p>
        ) : habits.length === 0 ? (
          <p className="text-gray-600">
            Você ainda não possui hábitos cadastrados.
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
            {sortHabitsByPriority(habits).map((habit) => (
              <div
                key={habit.id}
                className="
                  border
                  rounded-lg
                  p-4
                  bg-white
                  hover:shadow-md
                  transition
                "
              >
                {/* Título */}
                <Link
                  to={`/habits/${habit.id}/edit`}
                  className="text-lg font-semibold text-blue-700 hover:underline"
                >
                  {habit.title}
                </Link>

                <div className="text-xs text-gray-500 mt-1">
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
                  <div className="text-xs text-gray-400 mb-1">
                    Últimos 90 dias
                  </div>
                  <HabitHeatmap habitId={habit.id} />
                </div>

                {/* CTA */}
                <div className="mt-3 text-sm">
                  <Link
                    to={`/habits/${habit.id}/edit`}
                    className="text-gray-500 hover:text-blue-600 hover:underline"
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

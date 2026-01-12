import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import quotesService from "../services/quotesService";
import habitsService from "../services/habitsService";
import HabitHistorySummary from "../components/HabitHistorySummary";
import HabitHistoryDots from "../components/HabitHistoryDots";

export default function Home() {
  const [quote, setQuote] = useState(null);
  const [loadingQuote, setLoadingQuote] = useState(true);
  const [habits, setHabits] = useState([]);
  const [loadingHabits, setLoadingHabits] = useState(true);

  const user = JSON.parse(localStorage.getItem("user"));
  const cacheKey = `quote_of_day_${user?.id}`;

  // ============================
  // 📜 Quote do dia
  // ============================
  useEffect(() => {
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      setQuote(JSON.parse(cached));
    }

    async function loadQuote() {
      try {
        const q = await quotesService.getQuoteOfTheDay();
        setQuote(q);
        localStorage.setItem(cacheKey, JSON.stringify(q));
      } catch (err) {
        console.error("Erro ao carregar quote do dia:", err);
      } finally {
        setLoadingQuote(false);
      }
    }

    loadQuote();
  }, [cacheKey]);

  // ============================
  // 📅 Hábitos
  // ============================
  useEffect(() => {
    async function loadHabits() {
      try {
        const data = await habitsService.list();
        setHabits(data);
      } catch (err) {
        console.error("Erro ao carregar hábitos", err);
      } finally {
        setLoadingHabits(false);
      }
    }

    loadHabits();
  }, []);

  // ============================
  // ⏳ Loading
  // ============================
  if (loadingQuote) {
    return (
      <div className="animate-pulse p-6 max-w-4xl mx-auto">
        <div className="h-6 bg-gray-300 rounded w-48 mb-6"></div>
        <div className="h-24 bg-gray-300 rounded"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      {/* ============================
          ✨ Quote do Dia
      ============================ */}
      {quote ? (
        <div className="p-6 bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-xl rounded-xl animate-fadeSlide">
          <h2 className="text-lg font-semibold mb-3">✨ Quote do Dia</h2>
          <p className="text-2xl italic mb-3">"{quote.text}"</p>
          <span className="font-light">— {quote.author}</span>
        </div>
      ) : (
        <p className="text-gray-700">
          Você ainda não possui quotes cadastradas.
          <Link to="/quotes/new" className="text-blue-600 underline ml-1">
            Criar agora →
          </Link>
        </p>
      )}

      {/* ============================
          📅 Seus hábitos
      ============================ */}
      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4">📅 Seus hábitos</h2>

        {loadingHabits ? (
          <p className="text-gray-500">Carregando hábitos…</p>
        ) : habits.length === 0 ? (
          <p className="text-gray-600">
            Você ainda não possui hábitos cadastrados.
          </p>
        ) : (
          <div className="space-y-4">
            {habits.map((habit) => (
              <div
                key={habit.id}
                className="border rounded-lg p-4 hover:shadow-sm transition"
              >
                {/* Título */}
                <Link
                  to={`/habits/${habit.id}/edit`}
                  className="text-lg font-semibold text-blue-700 hover:underline"
                >
                  {habit.title}
                </Link>

                {/* Resumo */}
                <HabitHistorySummary habit={habit} />

                {/* 🔲 Quadradinhos com tooltip rico */}
                <div className="mt-3">
                  <div className="text-xs text-gray-400 mb-1">
                    Últimos 30 dias
                  </div>

                  <HabitHistoryDots habitId={habit.id} />
                </div>

                {/* CTA */}
                <div className="mt-2 text-sm">
                  <Link
                    to={`/habits/${habit.id}/edit`}
                    className="text-gray-500 hover:text-blue-600 hover:underline"
                  >
                    Ver histórico completo →
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

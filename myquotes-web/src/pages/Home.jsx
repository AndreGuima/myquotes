import { useEffect, useState } from "react";
import quotesService from "../services/quotesService";

export default function Home() {
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(true);

  // Recuperar usuário logado
  const user = JSON.parse(localStorage.getItem("user"));
  const cacheKey = `quote_of_day_${user?.id}`;

  useEffect(() => {
    // 1. Tenta carregar do cache
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      setQuote(JSON.parse(cached));
    }

    // 2. Tenta buscar a quote nova
    async function load() {
      try {
        const q = await quotesService.getQuoteOfTheDay();
        setQuote(q);
        localStorage.setItem(cacheKey, JSON.stringify(q));
      } catch (err) {
        console.log("Erro ao carregar quote do dia:", err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [cacheKey]);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-6 bg-gray-300 rounded w-48 mb-6"></div>
        <div className="h-24 bg-gray-300 rounded"></div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

      {quote ? (
        <div
          className="
            p-6 bg-gradient-to-r from-blue-500 to-blue-700 text-white
            shadow-xl rounded-xl
            animate-fadeSlide
          "
        >
          <h2 className="text-lg font-semibold mb-3">✨ Quote do Dia</h2>
          <p className="text-2xl italic mb-3">"{quote.text}"</p>
          <span className="font-light">— {quote.author}</span>
        </div>
      ) : (
        <p className="text-gray-700">
          Você ainda não possui quotes cadastradas.
          <a href="/quotes/new" className="text-blue-600 underline ml-1">
            Criar agora →
          </a>
        </p>
      )}
    </div>
  );
}

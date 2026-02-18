import { Link } from "react-router-dom";

export default function Expenses() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Lançamento de Despesas</h1>
        <Link
          to="/finances"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Finanças
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Registre despesas e acompanhe sua execução mensal.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Despesas do Mês</h2>
          <p className="text-2xl font-bold">R$ 0,00</p>
          <p className="themed-muted text-sm mt-1">Total lançado no período</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Maior Categoria</h2>
          <p className="text-2xl font-bold">-</p>
          <p className="themed-muted text-sm mt-1">
            Categoria com maior impacto
          </p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Lançamentos</h2>
          <p className="text-2xl font-bold">0</p>
          <p className="themed-muted text-sm mt-1">Quantidade de despesas</p>
        </div>
      </div>
    </div>
  );
}

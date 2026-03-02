import { Link } from "react-router-dom";

export default function InvestmentSummary({
  totalInvested,
  totalCurrent,
  profitability,
  formatCurrency,
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 mb-6">
      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="font-semibold mb-1">Valor Investido</h2>
        <p className="text-2xl font-bold">{formatCurrency(totalInvested)}</p>
        <p className="themed-muted text-sm mt-1">Baseado no preço médio</p>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="font-semibold mb-1">Valor Atual</h2>
        <p className="text-2xl font-bold">{formatCurrency(totalCurrent)}</p>
        <p className="themed-muted text-sm mt-1">Posição atual da carteira</p>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="font-semibold mb-1">Rentabilidade</h2>
        <p
          className={`text-2xl font-bold ${
            profitability >= 0 ? "text-green-600" : "text-red-600"
          }`}
        >
          {profitability.toFixed(2)}%
        </p>
        <p className="themed-muted text-sm mt-1">
          {formatCurrency(totalCurrent - totalInvested)} no total
        </p>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="font-semibold mb-1">Proventos e Dividendos</h2>
        <p className="themed-muted text-sm mt-1 mb-4">
          Cadastre os recebimentos da carteira.
        </p>
        <Link
          to="/finances/investments/incomes"
          className="inline-flex items-center justify-center bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded"
        >
          Abrir proventos
        </Link>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="font-semibold mb-1">Dashboards</h2>
        <p className="themed-muted text-sm mt-1 mb-4">
          Visualize a carteira por setor em ações e FIIs.
        </p>
        <Link
          to="/finances/investments/dashboards"
          className="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          Abrir dashboard
        </Link>
      </div>
    </div>
  );
}

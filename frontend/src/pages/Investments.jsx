import { Link } from "react-router-dom";

export default function Investments() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Investimentos</h1>
        <Link
          to="/finances"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Finanças
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Acompanhe sua carteira e a evolução dos seus investimentos.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Valor Investido</h2>
          <p className="text-2xl font-bold">R$ 0,00</p>
          <p className="themed-muted text-sm mt-1">Aportes acumulados</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Valor Atual</h2>
          <p className="text-2xl font-bold">R$ 0,00</p>
          <p className="themed-muted text-sm mt-1">Posição da carteira</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Rentabilidade</h2>
          <p className="text-2xl font-bold">0,00%</p>
          <p className="themed-muted text-sm mt-1">Desempenho consolidado</p>
        </div>
      </div>
    </div>
  );
}

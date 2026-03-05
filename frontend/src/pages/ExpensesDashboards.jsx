import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import expensesService from "../services/expensesService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const PIE_COLORS = [
  "#0ea5e9",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#14b8a6",
  "#3b82f6",
  "#f97316",
  "#84cc16",
];

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function polarToCartesian(cx, cy, radius, angleInDegrees) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(angleInRadians),
    y: cy + radius * Math.sin(angleInRadians),
  };
}

function describeArc(cx, cy, radius, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, radius, endAngle);
  const end = polarToCartesian(cx, cy, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${cx} ${cy} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArcFlag} 0 ${end.x} ${end.y} Z`;
}

export default function ExpensesDashboards() {
  const [summary, setSummary] = useState({
    total: 0,
    average: 0,
    count: 0,
    credit_total: 0,
    debit_total: 0,
    by_category: [],
  });
  const [periodFilters, setPeriodFilters] = useState({
    fromDate: "",
    toDate: "",
  });

  const invalidPeriod =
    periodFilters.fromDate &&
    periodFilters.toDate &&
    periodFilters.fromDate > periodFilters.toDate;

  useEffect(() => {
    if (invalidPeriod) return;

    async function loadSummary() {
      try {
        const data = await expensesService.summary({
          fromDate: periodFilters.fromDate,
          toDate: periodFilters.toDate,
        });
        setSummary({
          total: Number(data?.total || 0),
          average: Number(data?.average || 0),
          count: Number(data?.count || 0),
          credit_total: Number(data?.credit_total || 0),
          debit_total: Number(data?.debit_total || 0),
          by_category: Array.isArray(data?.by_category) ? data.by_category : [],
        });
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar dashboards"));
      }
    }

    loadSummary();
  }, [invalidPeriod, periodFilters.fromDate, periodFilters.toDate]);

  const categoriesSummary = useMemo(() => {
    const items = invalidPeriod ? [] : summary.by_category;
    return items
      .map((item) => ({
        id: item.category_id,
        name: item.category_name || "Sem categoria",
        total: Number(item.total || 0),
        count: Number(item.count || 0),
      }))
      .sort((a, b) => b.total - a.total);
  }, [invalidPeriod, summary.by_category]);

  const totalExpenses = invalidPeriod ? 0 : Number(summary.total || 0);
  const averageExpense = invalidPeriod ? 0 : Number(summary.average || 0);
  const launchCount = invalidPeriod ? 0 : Number(summary.count || 0);
  const paymentSplit = {
    debit: invalidPeriod ? 0 : Number(summary.debit_total || 0),
    credit: invalidPeriod ? 0 : Number(summary.credit_total || 0),
  };

  const pieSlices = useMemo(() => {
    if (totalExpenses <= 0 || categoriesSummary.length === 0) return [];

    let startAngle = 0;
    return categoriesSummary.map((item, index) => {
      const percentage = (item.total / totalExpenses) * 100;
      const angle = (item.total / totalExpenses) * 360;
      const endAngle = startAngle + angle;
      const slice = {
        ...item,
        percentage,
        color: PIE_COLORS[index % PIE_COLORS.length],
        path: describeArc(110, 110, 95, startAngle, endAngle),
      };
      startAngle = endAngle;
      return slice;
    });
  }, [categoriesSummary, totalExpenses]);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Dashboards de Despesas</h1>
        <Link
          to="/finances/expenses"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Despesas
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Indicadores consolidados dos lançamentos de despesas.
      </p>

      <div className="themed-card themed-border border rounded-xl p-5 mb-4">
        <h2 className="font-semibold mb-3">Filtro por período</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <label className="text-sm">
            <span className="block themed-muted mb-1">De</span>
            <input
              type="date"
              className="themed-input rounded px-3 py-2 w-full"
              value={periodFilters.fromDate}
              onChange={(e) =>
                setPeriodFilters((prev) => ({
                  ...prev,
                  fromDate: e.target.value,
                }))
              }
            />
          </label>

          <label className="text-sm">
            <span className="block themed-muted mb-1">Até</span>
            <input
              type="date"
              className="themed-input rounded px-3 py-2 w-full"
              value={periodFilters.toDate}
              onChange={(e) =>
                setPeriodFilters((prev) => ({
                  ...prev,
                  toDate: e.target.value,
                }))
              }
            />
          </label>

          <button
            type="button"
            className="themed-border border rounded px-3 py-2 self-end hover:opacity-90 transition"
            onClick={() => setPeriodFilters({ fromDate: "", toDate: "" })}
          >
            Limpar período
          </button>
        </div>

        {invalidPeriod ? (
          <p className="text-sm text-red-500 mt-3">
            O período é inválido: a data inicial deve ser menor ou igual a data
            final.
          </p>
        ) : null}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Total de Despesas</h2>
          <p className="text-2xl font-bold">{formatCurrency(totalExpenses)}</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Ticket Medio</h2>
          <p className="text-2xl font-bold">{formatCurrency(averageExpense)}</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Qtd. Lançamentos</h2>
          <p className="text-2xl font-bold">{launchCount}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Total em Debito</h2>
          <p className="text-2xl font-bold">
            {formatCurrency(paymentSplit.debit)}
          </p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Total em Credito</h2>
          <p className="text-2xl font-bold">
            {formatCurrency(paymentSplit.credit)}
          </p>
        </div>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5 mt-4">
        <h2 className="font-semibold mb-3">Distribuição por Categoria</h2>
        {categoriesSummary.length === 0 ? (
          <p className="themed-muted text-sm">Sem dados de categoria ainda.</p>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">
            <div className="w-full max-w-[260px] mx-auto">
              <svg
                viewBox="0 0 220 220"
                role="img"
                aria-label="Gráfico de pizza de despesas por categoria"
                className="w-full h-auto drop-shadow-sm"
              >
                <circle
                  cx="110"
                  cy="110"
                  r="98"
                  fill="rgba(255,255,255,0.04)"
                />
                {pieSlices.map((slice) => (
                  <path key={slice.id} d={slice.path} fill={slice.color} />
                ))}
                <circle cx="110" cy="110" r="48" fill="var(--card-bg)" />
                <text
                  x="110"
                  y="104"
                  textAnchor="middle"
                  className="fill-current text-[10px] font-medium themed-muted"
                >
                  Total
                </text>
                <text
                  x="110"
                  y="120"
                  textAnchor="middle"
                  className="fill-current text-[11px] font-semibold"
                >
                  {formatCurrency(totalExpenses)}
                </text>
              </svg>
            </div>

            <div className="space-y-2">
              {pieSlices.map((slice) => (
                <div
                  key={slice.id}
                  className="flex items-center justify-between text-sm themed-card themed-border border rounded-lg px-3 py-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className="inline-block w-3 h-3 rounded-full shrink-0"
                      style={{ backgroundColor: slice.color }}
                    />
                    <span className="truncate">{slice.name}</span>
                  </div>
                  <div className="text-right ml-3">
                    <div className="font-medium">
                      {formatCurrency(slice.total)}
                    </div>
                    <div className="themed-muted text-xs">
                      {slice.percentage.toFixed(1)}% • {slice.count} lanç.
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

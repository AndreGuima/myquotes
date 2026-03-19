import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { notify } from "../core/toast";
import investmentIncomesService from "../services/investmentIncomesService";
import investmentsService from "../services/investmentsService";
import PieDonutChart from "../components/charts/PieDonutChart";
import { describeArc } from "../utils/charts/pieMath";

const PIE_COLORS = ["#0ea5e9", "#22c55e", "#f59e0b"];

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function toTimestamp(value) {
  const ts = new Date(value || "").getTime();
  return Number.isFinite(ts) ? ts : 0;
}

function monthKey(value) {
  const date = new Date(value || "");
  if (Number.isNaN(date.getTime())) return null;
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  return `${y}-${m}`;
}

function monthLabel(key) {
  const [y, m] = String(key).split("-");
  return new Date(Number(y), Number(m) - 1, 1).toLocaleDateString("pt-BR", {
    month: "short",
    year: "numeric",
  });
}

function monthTimestamp(key) {
  const [y, m] = String(key).split("-");
  const ts = new Date(Number(y), Number(m) - 1, 1).getTime();
  return Number.isFinite(ts) ? ts : 0;
}

function buildPieSlices(summary) {
  const total = summary.reduce((acc, item) => acc + Number(item.total || 0), 0);
  if (total <= 0 || summary.length === 0) return { total, slices: [] };

  let startAngle = 0;
  const slices = summary.map((item, index) => {
    const percentage = (item.total / total) * 100;
    const angle = (item.total / total) * 360;
    const endAngle = startAngle + angle;
    const slice = {
      id: item.type,
      label: item.label,
      ...item,
      percentage,
      color: PIE_COLORS[index % PIE_COLORS.length],
      path: describeArc(110, 110, 95, startAngle, endAngle),
    };
    startAngle = endAngle;
    return slice;
  });

  return { total, slices };
}

function AssetTypePieCard({ summary }) {
  const { total, slices } = useMemo(() => buildPieSlices(summary), [summary]);
  const [hoveredType, setHoveredType] = useState(null);

  return (
    <div className="themed-card themed-border border rounded-xl p-5">
      <h2 className="font-semibold mb-3">Proventos por Tipo de Ativo</h2>
      <PieDonutChart
        slices={slices}
        total={total}
        hoveredId={hoveredType}
        setHoveredId={setHoveredType}
        ariaLabel="Gráfico de pizza de proventos por tipo de ativo"
        countSuffix="lançamentos"
      />
    </div>
  );
}

export default function InvestmentIncomesDashboards() {
  const [items, setItems] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
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

    async function loadData() {
      setLoading(true);
      try {
        const [incomesData, investmentsData] = await Promise.all([
          investmentIncomesService.list({
            fromDate: periodFilters.fromDate,
            toDate: periodFilters.toDate,
          }),
          investmentsService.list(),
        ]);
        setItems(Array.isArray(incomesData) ? incomesData : []);
        setInvestments(Array.isArray(investmentsData) ? investmentsData : []);
      } catch {
        notify.error("Erro ao carregar dashboard de proventos");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [invalidPeriod, periodFilters.fromDate, periodFilters.toDate]);

  const visibleItems = useMemo(
    () => (invalidPeriod ? [] : items),
    [invalidPeriod, items],
  );

  const totalAmount = useMemo(
    () => visibleItems.reduce((acc, item) => acc + Number(item.amount || 0), 0),
    [visibleItems],
  );

  const monthlySeries = useMemo(() => {
    const grouped = new Map();
    visibleItems.forEach((item) => {
      const key = monthKey(item.received_at);
      if (!key) return;
      grouped.set(key, (grouped.get(key) || 0) + Number(item.amount || 0));
    });

    return [...grouped.entries()]
      .sort((a, b) => monthTimestamp(a[0]) - monthTimestamp(b[0]))
      .map(([key, total]) => ({ key, label: monthLabel(key), total }));
  }, [visibleItems]);

  const typeSummary = useMemo(() => {
    const labels = {
      dividend: "Dividendo",
      provento: "Provento",
      jcp: "JCP",
      rendimento: "Rendimento",
    };

    const grouped = visibleItems.reduce((acc, item) => {
      const type = String(item.income_type || "provento");
      if (!acc[type]) {
        acc[type] = {
          type,
          label: labels[type] || "Provento",
          total: 0,
          count: 0,
        };
      }
      acc[type].total += Number(item.amount || 0);
      acc[type].count += 1;
      return acc;
    }, {});

    return Object.values(grouped).sort((a, b) => b.total - a.total);
  }, [visibleItems]);

  const assetTypeSummary = useMemo(() => {
    const investmentTypeByTicker = new Map();

    investments.forEach((item) => {
      const ticker = String(item.ticker || "")
        .trim()
        .toUpperCase();
      const assetType = String(item.asset_type || "")
        .trim()
        .toLowerCase();

      if (!ticker || !assetType || investmentTypeByTicker.has(ticker)) return;
      investmentTypeByTicker.set(ticker, assetType);
    });

    const grouped = visibleItems.reduce((acc, item) => {
      const ticker = String(item.ticker || "")
        .trim()
        .toUpperCase();
      const assetType = investmentTypeByTicker.get(ticker);

      const normalizedType =
        assetType === "stock" || assetType === "acao" || assetType === "acoes"
          ? "stock"
          : assetType === "fii" || assetType === "fiis"
            ? "fii"
            : "unknown";

      if (!acc[normalizedType]) {
        acc[normalizedType] = {
          type: normalizedType,
          label:
            normalizedType === "stock"
              ? "Ações"
              : normalizedType === "fii"
                ? "FIIs"
                : "Sem vínculo",
          total: 0,
          count: 0,
        };
      }

      acc[normalizedType].total += Number(item.amount || 0);
      acc[normalizedType].count += 1;
      return acc;
    }, {});

    return Object.values(grouped).sort((a, b) => b.total - a.total);
  }, [investments, visibleItems]);

  const lastIncomeAt = useMemo(() => {
    if (!visibleItems.length) return null;
    const latest = [...visibleItems].sort(
      (a, b) => toTimestamp(b.received_at) - toTimestamp(a.received_at),
    )[0];
    return latest?.received_at || null;
  }, [visibleItems]);

  const maxMonthly = Math.max(1, ...monthlySeries.map((item) => item.total));

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6 gap-3">
        <h1 className="text-3xl font-bold">Dashboard de Proventos</h1>
        <Link
          to="/finances/investments/incomes"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Proventos
        </Link>
      </div>

      {loading ? (
        <p className="themed-muted">Carregando dashboard...</p>
      ) : (
        <>
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
                O período é inválido: a data inicial deve ser menor ou igual a
                data final.
              </p>
            ) : null}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="themed-card themed-border border rounded-xl p-5">
              <h2 className="font-semibold mb-1">Total Recebido</h2>
              <p className="text-2xl font-bold">
                {formatCurrency(totalAmount)}
              </p>
            </div>
            <div className="themed-card themed-border border rounded-xl p-5">
              <h2 className="font-semibold mb-1">Lançamentos</h2>
              <p className="text-2xl font-bold">{visibleItems.length}</p>
            </div>
            <div className="themed-card themed-border border rounded-xl p-5">
              <h2 className="font-semibold mb-1">Último Recebimento</h2>
              <p className="text-2xl font-bold">
                {lastIncomeAt
                  ? new Date(`${lastIncomeAt}T00:00:00`).toLocaleDateString(
                      "pt-BR",
                    )
                  : "-"}
              </p>
            </div>
          </div>

          <div className="mb-4">
            <AssetTypePieCard summary={assetTypeSummary} />
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <div className="themed-card themed-border border rounded-xl p-5">
              <h2 className="font-semibold mb-3">Proventos por Tipo</h2>
              {typeSummary.length === 0 ? (
                <p className="themed-muted text-sm">Sem dados ainda.</p>
              ) : (
                <div className="space-y-2">
                  {typeSummary.map((item) => (
                    <div
                      key={item.type}
                      className="flex items-center justify-between themed-card themed-border border rounded-lg px-3 py-2 text-sm"
                    >
                      <span>{item.label}</span>
                      <span className="font-medium">
                        {formatCurrency(item.total)} ({item.count})
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="themed-card themed-border border rounded-xl p-5">
              <h2 className="font-semibold mb-3">Evolução Mensal</h2>
              {monthlySeries.length === 0 ? (
                <p className="themed-muted text-sm">Sem dados ainda.</p>
              ) : (
                <div className="space-y-2">
                  {monthlySeries.map((item) => (
                    <div key={item.key}>
                      <div className="flex items-center justify-between text-xs themed-muted mb-1">
                        <span>{item.label}</span>
                        <span>{formatCurrency(item.total)}</span>
                      </div>
                      <div className="h-2 rounded bg-[var(--line-color)] overflow-hidden">
                        <div
                          className="h-full bg-blue-600"
                          style={{
                            width: `${(item.total / maxMonthly) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

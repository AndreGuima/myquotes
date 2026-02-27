import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import investmentsService from "../services/investmentsService";
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

function buildSectorSummaryByType(investments, assetType) {
  const filtered = (investments || []).filter(
    (item) => item.asset_type === assetType,
  );

  const grouped = filtered.reduce((acc, item) => {
    const sectorName = String(item.sector || "").trim() || "Sem setor";
    const currentValue =
      Number(item.quantity || 0) * Number(item.current_price || 0);

    if (!acc[sectorName]) {
      acc[sectorName] = {
        sector: sectorName,
        total: 0,
        count: 0,
      };
    }

    acc[sectorName].total += currentValue;
    acc[sectorName].count += 1;
    return acc;
  }, {});

  return Object.values(grouped).sort((a, b) => b.total - a.total);
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

function PieBySectorCard({ title, summary }) {
  const { total, slices } = useMemo(() => buildPieSlices(summary), [summary]);

  return (
    <div className="themed-card themed-border border rounded-xl p-5">
      <h2 className="font-semibold mb-3">{title}</h2>
      {slices.length === 0 ? (
        <p className="themed-muted text-sm">
          Sem dados suficientes para montar o gráfico.
        </p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">
          <div className="w-full max-w-[260px] mx-auto">
            <svg
              viewBox="0 0 220 220"
              role="img"
              aria-label={`Gráfico de pizza de ${title} por setor`}
              className="w-full h-auto drop-shadow-sm"
            >
              <circle cx="110" cy="110" r="98" fill="rgba(255,255,255,0.04)" />
              {slices.map((slice) => (
                <path key={slice.sector} d={slice.path} fill={slice.color} />
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
                {formatCurrency(total)}
              </text>
            </svg>
          </div>

          <div className="space-y-2">
            {slices.map((slice) => (
              <div
                key={slice.sector}
                className="flex items-center justify-between text-sm themed-card themed-border border rounded-lg px-3 py-2"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="inline-block w-3 h-3 rounded-full shrink-0"
                    style={{ backgroundColor: slice.color }}
                  />
                  <span className="truncate">{slice.sector}</span>
                </div>
                <div className="text-right ml-3">
                  <div className="font-medium">
                    {formatCurrency(slice.total)}
                  </div>
                  <div className="themed-muted text-xs">
                    {slice.percentage.toFixed(1)}% • {slice.count} ativos
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function InvestmentsDashboards() {
  const [investments, setInvestments] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await investmentsService.list();
        setInvestments(Array.isArray(data) ? data : []);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar dashboards"));
      }
    }

    loadData();
  }, []);

  const stockSummary = useMemo(
    () => buildSectorSummaryByType(investments, "stock"),
    [investments],
  );
  const fiiSummary = useMemo(
    () => buildSectorSummaryByType(investments, "fii"),
    [investments],
  );

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6 gap-3">
        <h1 className="text-3xl font-bold">Dashboard de Investimentos</h1>
        <Link
          to="/finances/investments"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Investimentos
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Distribuição da carteira por setor com base no valor atual.
      </p>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <PieBySectorCard title="Ações por Setor" summary={stockSummary} />
        <PieBySectorCard title="FIIs por Setor" summary={fiiSummary} />
      </div>
    </div>
  );
}

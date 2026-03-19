import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import investmentsService from "../services/investmentsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";
import PieDonutChart from "../components/charts/PieDonutChart";
import { describeArc } from "../utils/charts/pieMath";

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
      id: item.sector,
      label: item.sector,
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
  const [hoveredSector, setHoveredSector] = useState(null);

  return (
    <div className="themed-card themed-border border rounded-xl p-5">
      <h2 className="font-semibold mb-3">{title}</h2>
      <PieDonutChart
        slices={slices}
        total={total}
        hoveredId={hoveredSector}
        setHoveredId={setHoveredSector}
        ariaLabel={`Gráfico de pizza de ${title} por setor`}
        countSuffix="ativos"
      />
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

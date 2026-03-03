import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import bankAccountsService from "../services/bankAccountsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

function toDateKey(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString().slice(0, 10);
}

function toMoney(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function toDateLabel(dateKey) {
  return new Date(`${dateKey}T00:00:00`).toLocaleDateString("pt-BR");
}

function toTimestamp(value) {
  const ts = new Date(value || "").getTime();
  return Number.isFinite(ts) ? ts : 0;
}

const PERIOD_OPTIONS = [
  { label: "1M", days: 30 },
  { label: "6M", days: 183 },
  { label: "1A", days: 365 },
  { label: "5A", days: 1825 },
  { label: "Máx", days: 3650 },
];

function computeAxisValues(minValue, maxValue, tickCount) {
  if (!Number.isFinite(minValue) || !Number.isFinite(maxValue)) {
    return {
      yMin: 0,
      yMax: 1,
      yValues: Array.from({ length: tickCount }, (_, idx) => idx),
    };
  }

  if (minValue === maxValue) {
    const delta = Math.max(Math.abs(minValue) * 0.02, 1);
    minValue -= delta;
    maxValue += delta;
  }

  const range = maxValue - minValue;
  const padding = Math.max(range * 0.2, Math.abs(maxValue) * 0.005, 1);
  const rawMin = minValue - padding;
  const rawMax = maxValue + padding;

  const rawStep = (rawMax - rawMin) / (tickCount - 1);
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const normalized = rawStep / magnitude;

  let niceNormalized = 1;
  if (normalized <= 1) niceNormalized = 1;
  else if (normalized <= 2) niceNormalized = 2;
  else if (normalized <= 5) niceNormalized = 5;
  else niceNormalized = 10;

  const step = niceNormalized * magnitude;
  const yMin = Math.floor(rawMin / step) * step;
  const yMax = Math.ceil(rawMax / step) * step;
  const yValues = Array.from({ length: tickCount }, (_, idx) => {
    const ratio = idx / (tickCount - 1);
    return yMax - (yMax - yMin) * ratio;
  });

  return { yMin, yMax, yValues };
}

function buildSeriesFromSnapshots(snapshots) {
  const latestByDate = new Map();

  (snapshots || []).forEach((snapshot) => {
    const dateKey = toDateKey(snapshot.snapshot_at);
    if (!dateKey) return;

    const existing = latestByDate.get(dateKey);
    if (
      !existing ||
      new Date(snapshot.snapshot_at) > new Date(existing.snapshot_at)
    ) {
      latestByDate.set(dateKey, snapshot);
    }
  });

  return [...latestByDate.entries()]
    .sort((a, b) => toTimestamp(a[0]) - toTimestamp(b[0]))
    .map(([dateKey, snapshot]) => ({
      dateKey,
      total: Number(snapshot.total_value || 0),
      snapshotAt: snapshot.snapshot_at,
    }));
}

function PatrimonyLineChart({ series }) {
  const width = 900;
  const height = 320;
  const margin = { top: 20, right: 18, bottom: 42, left: 86 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const yTicks = 5;
  const totals = series.map((point) => point.total);
  const minValue = Math.min(...totals);
  const maxValue = Math.max(...totals);
  const { yMin, yMax, yValues } = computeAxisValues(minValue, maxValue, yTicks);

  const xForIndex = (index) =>
    margin.left +
    (series.length === 1
      ? innerWidth / 2
      : (innerWidth * index) / (series.length - 1));
  const yForValue = (value) =>
    margin.top + innerHeight - ((value - yMin) / (yMax - yMin)) * innerHeight;

  const path = series
    .map(
      (point, index) =>
        `${index === 0 ? "M" : "L"} ${xForIndex(index)} ${yForValue(point.total)}`,
    )
    .join(" ");

  const first = series[0];
  const middle = series[Math.floor(series.length / 2)];
  const last = series[series.length - 1];
  const xLabelPoints = [first, middle, last].filter(
    (point, index, arr) =>
      point &&
      arr.findIndex((item) => item?.dateKey === point.dateKey) === index,
  );

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[720px]">
        {yValues.map((value, idx) => {
          const y = yForValue(value);
          return (
            <g key={`y-${idx}`}>
              <line
                x1={margin.left}
                y1={y}
                x2={width - margin.right}
                y2={y}
                className="stroke-[var(--line-color)]"
                strokeWidth="1"
              />
              <text
                x={margin.left - 10}
                y={y}
                textAnchor="end"
                dominantBaseline="middle"
                className="fill-[var(--muted-text)] text-[11px]"
              >
                {toMoney(value)}
              </text>
            </g>
          );
        })}

        <path
          d={path}
          fill="none"
          stroke="#2563eb"
          strokeWidth="3"
          strokeLinecap="round"
        />

        {series.map((point, index) => (
          <g key={point.dateKey}>
            <circle
              cx={xForIndex(index)}
              cy={yForValue(point.total)}
              r="4"
              fill="#2563eb"
            >
              <title>{`${toDateLabel(point.dateKey)} - ${toMoney(point.total)}`}</title>
            </circle>
          </g>
        ))}

        {xLabelPoints.map((point) => {
          const index = series.findIndex(
            (item) => item.dateKey === point.dateKey,
          );
          return (
            <text
              key={`x-${point.dateKey}`}
              x={xForIndex(index)}
              y={height - 14}
              textAnchor="middle"
              className="fill-[var(--muted-text)] text-[11px]"
            >
              {toDateLabel(point.dateKey)}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

export default function PatrimonyDashboards() {
  const [snapshots, setSnapshots] = useState([]);
  const [periodDays, setPeriodDays] = useState(365);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const snapshotsData = await bankAccountsService.snapshots(periodDays);
        setSnapshots(Array.isArray(snapshotsData) ? snapshotsData : []);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar dashboards"));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [periodDays]);

  const series = useMemo(
    () => buildSeriesFromSnapshots(snapshots),
    [snapshots],
  );
  const totalCurrent = series.length ? series[series.length - 1].total : 0;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6 gap-3">
        <h1 className="text-3xl font-bold">Dashboards de Patrimônio</h1>
        <Link
          to="/finances/patrimony"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Patrimônio
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Montante Atual</h2>
          <p className="text-2xl font-bold">{toMoney(totalCurrent)}</p>
          <p className="themed-muted text-sm mt-1">
            Soma das contas cadastradas
          </p>
        </div>
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Pontos no Gráfico</h2>
          <p className="text-2xl font-bold">{series.length}</p>
          <p className="themed-muted text-sm mt-1">
            Datas com evolução registrada
          </p>
        </div>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="text-xl font-semibold mb-2">
          Montante Geral ao Longo do Tempo
        </h2>
        <p className="themed-muted text-sm mb-4">
          Evolução do patrimônio com base nos snapshots salvos nas alterações.
        </p>
        <div className="flex flex-wrap gap-2 mb-4">
          {PERIOD_OPTIONS.map((option) => {
            const isActive = option.days === periodDays;
            return (
              <button
                key={option.label}
                type="button"
                onClick={() => setPeriodDays(option.days)}
                className={`px-3 py-1.5 rounded-lg border text-sm transition ${
                  isActive
                    ? "bg-blue-600 text-white border-blue-600"
                    : "themed-card themed-border border hover:opacity-90"
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>

        {loading ? (
          <p className="themed-muted">Carregando dados...</p>
        ) : series.length === 0 ? (
          <p className="themed-muted">
            Ainda não há contas cadastradas para gerar o gráfico.
          </p>
        ) : (
          <PatrimonyLineChart series={series} />
        )}
      </div>
    </div>
  );
}

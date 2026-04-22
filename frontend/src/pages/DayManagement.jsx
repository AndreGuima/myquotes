import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getApiErrorMessage } from "../core/apiError";
import { notify } from "../core/toast";
import habitsService from "../services/habitsService";

const CHART_DAYS = 14;

function formatDateKey(date) {
  return date.toISOString().slice(0, 10);
}

function buildDateRange(days) {
  const end = new Date();
  end.setHours(0, 0, 0, 0);
  const start = new Date(end);
  start.setDate(start.getDate() - (days - 1));

  const range = [];
  const current = new Date(start);
  while (current <= end) {
    range.push(formatDateKey(current));
    current.setDate(current.getDate() + 1);
  }
  return range;
}

function toShortDate(dateKey) {
  return new Date(`${dateKey}T00:00:00`).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
  });
}

function buildLinePath(points, xForIndex, yForValue) {
  return points
    .map((point, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command} ${xForIndex(index)} ${yForValue(point.completedCount)}`;
    })
    .join(" ");
}

function DailyHabitsPerformanceChart({ points, totalDailyHabits }) {
  const width = 960;
  const height = 320;
  const margin = { top: 24, right: 20, bottom: 56, left: 56 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const yMax = Math.max(totalDailyHabits, 1);
  const yTicks = Math.min(5, yMax + 1);
  const yValues =
    yTicks <= 1
      ? [0]
      : Array.from({ length: yTicks }, (_, index) => {
          const ratio = index / (yTicks - 1);
          return Math.round(yMax - yMax * ratio);
        });

  const xForIndex = (index) =>
    margin.left +
    (points.length <= 1
      ? innerWidth / 2
      : (innerWidth * index) / (points.length - 1));
  const yForValue = (value) =>
    margin.top + innerHeight - (Math.max(0, value) / yMax) * innerHeight;

  const path = buildLinePath(points, xForIndex, yForValue);

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[760px]">
        {points.map((point, index) => {
          const x = xForIndex(index);
          return (
            <line
              key={`x-grid-${point.dateKey}`}
              x1={x}
              y1={margin.top}
              x2={x}
              y2={height - margin.bottom}
              className="stroke-[var(--line-color)]"
              strokeWidth="1"
              opacity={index % 2 === 0 ? 0.45 : 0.2}
            />
          );
        })}

        {yValues.map((value) => {
          const y = yForValue(value);
          return (
            <g key={`y-${value}`}>
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
                {value}
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
          strokeLinejoin="round"
        />

        {points.map((point, index) => (
          <circle
            key={`dot-${point.dateKey}`}
            cx={xForIndex(index)}
            cy={yForValue(point.completedCount)}
            r="4"
            fill="#1d4ed8"
          >
            <title>{`${toShortDate(point.dateKey)}: ${point.completedCount}/${point.totalDailyHabits} (${point.percent.toFixed(0)}%)`}</title>
          </circle>
        ))}

        {points.map((point, index) => (
          <text
            key={`x-label-${point.dateKey}`}
            x={xForIndex(index)}
            y={height - 16}
            textAnchor="middle"
            className="fill-[var(--muted-text)] text-[10px]"
          >
            {toShortDate(point.dateKey)}
          </text>
        ))}
      </svg>
    </div>
  );
}

export default function DayManagement() {
  const [performancePoints, setPerformancePoints] = useState([]);
  const [loadingPerformance, setLoadingPerformance] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadPerformance() {
      setLoadingPerformance(true);

      try {
        const allHabits = await habitsService.list();
        const dailyHabits = allHabits.filter(
          (habit) => habit.frequency_type === "daily",
        );

        if (dailyHabits.length === 0) {
          if (isMounted) setPerformancePoints([]);
          return;
        }

        const dateKeys = buildDateRange(CHART_DAYS);
        const from_date = dateKeys[0];
        const to_date = dateKeys[dateKeys.length - 1];

        const histories = await Promise.all(
          dailyHabits.map((habit) =>
            habitsService.history(habit.id, { from_date, to_date }),
          ),
        );

        const completedByDate = new Map(
          dateKeys.map((dateKey) => [dateKey, 0]),
        );

        histories.forEach((history) => {
          history.days.forEach((day) => {
            if (day.completed && completedByDate.has(day.date)) {
              completedByDate.set(day.date, completedByDate.get(day.date) + 1);
            }
          });
        });

        const points = dateKeys.map((dateKey) => {
          const completedCount = completedByDate.get(dateKey) || 0;
          const totalDailyHabits = dailyHabits.length;
          const percent =
            totalDailyHabits > 0
              ? (completedCount / totalDailyHabits) * 100
              : 0;

          return {
            dateKey,
            completedCount,
            totalDailyHabits,
            percent,
          };
        });

        if (isMounted) setPerformancePoints(points);
      } catch (error) {
        notify.error(
          getApiErrorMessage(
            error,
            "Erro ao carregar performance dos hábitos diários",
          ),
        );
      } finally {
        if (isMounted) setLoadingPerformance(false);
      }
    }

    loadPerformance();

    return () => {
      isMounted = false;
    };
  }, []);

  const totalDailyHabits = useMemo(
    () => performancePoints[0]?.totalDailyHabits ?? 0,
    [performancePoints],
  );

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Gestão do Dia</h1>
      <p className="themed-muted mb-8">
        Acesse os módulos do seu planejamento diário.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          to="/habits"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition"
        >
          <div className="text-lg font-semibold mb-1">Hábitos</div>
          <div className="themed-muted text-sm">
            Gerencie seus hábitos, frequência e progresso.
          </div>
        </Link>

        <Link
          to="/daily-routine"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition"
        >
          <div className="text-lg font-semibold mb-1">Rotina do Dia</div>
          <div className="themed-muted text-sm">
            Visualize e acompanhe seus hábitos ao longo da rotina diária.
          </div>
        </Link>
      </div>

      <div className="mt-6 themed-card themed-border border rounded-xl p-5">
        <div className="mb-3">
          <h2 className="text-lg font-semibold">
            Performance dos hábitos diários (últimas 2 semanas)
          </h2>
          <p className="themed-muted text-sm">
            Cada ponto mostra quantos hábitos diários foram concluídos em cada
            dia.
          </p>
        </div>

        {loadingPerformance ? (
          <p className="themed-muted text-sm">Carregando performance...</p>
        ) : totalDailyHabits === 0 ? (
          <p className="themed-muted text-sm">
            Você ainda não possui hábitos diários para exibir no gráfico.
          </p>
        ) : (
          <>
            <DailyHabitsPerformanceChart
              points={performancePoints}
              totalDailyHabits={totalDailyHabits}
            />

            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
              {performancePoints.map((point) => (
                <div
                  key={`summary-${point.dateKey}`}
                  className="themed-border border rounded-lg px-2 py-1.5 text-xs"
                >
                  <div className="themed-muted">
                    {toShortDate(point.dateKey)}
                  </div>
                  <div className="font-medium">
                    {point.completedCount}/{point.totalDailyHabits}
                  </div>
                  <div className="text-blue-600 font-semibold">
                    {point.percent.toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import habitsService from "../services/habitsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const gradientPalette = [
  "from-[#A7F3D0] to-[#6EE7B7]",
  "from-[#FDE68A] to-[#FBBF24]",
  "from-[#93C5FD] to-[#60A5FA]",
  "from-[#E9D5FF] to-[#C4B5FD]",
  "from-[#FEF08A] to-[#FDE047]",
  "from-[#67E8F9] to-[#22D3EE]",
  "from-[#FDBA74] to-[#FB923C]",
  "from-[#86EFAC] to-[#4ADE80]",
  "from-[#FBCFE8] to-[#F472B6]",
  "from-[#BAE6FD] to-[#7DD3FC]",
  "from-[#DDD6FE] to-[#A5B4FC]",
  "from-[#FCA5A5] to-[#F87171]",
  "from-[#BFDBFE] to-[#93C5FD]",
  "from-[#FDE2E4] to-[#F9A8D4]",
];

const defaultStartOfDay = 6 * 60;
const defaultEndOfDay = 22 * 60;
const pxPerMinute = 1.1;
const minutesInDay = 24 * 60;

function timeToMinutes(value) {
  const [hours, minutes] = value.split(":").map(Number);
  return hours * 60 + minutes;
}

function formatHourLabel(hour) {
  const normalizedHour = ((hour % 24) + 24) % 24;
  const suffix = normalizedHour >= 12 ? "pm" : "am";
  const normalized = normalizedHour % 12 === 0 ? 12 : normalizedHour % 12;
  return `${normalized}:00 ${suffix}`;
}

function hashString(value) {
  let hash = 0;
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function getDurationMinutes(startTime, endTime) {
  if (!startTime || !endTime) return 30;
  const start = timeToMinutes(startTime);
  const end = timeToMinutes(endTime);
  if (end === start) return minutesInDay;
  return end > start ? end - start : minutesInDay - start + end;
}

function getVisualRanges(startTime, endTime) {
  const start = timeToMinutes(startTime);
  if (!endTime) {
    return [
      {
        visualStart: start,
        visualEnd: Math.min(start + 30, minutesInDay),
        period: "day",
      },
    ];
  }
  const end = timeToMinutes(endTime);
  if (end < start) {
    // Overnight: exibe continuação da madrugada + início no fim do dia.
    return [
      { visualStart: 0, visualEnd: end, period: "morning" },
      { visualStart: start, visualEnd: minutesInDay, period: "evening" },
    ];
  }
  return [{ visualStart: start, visualEnd: end, period: "day" }];
}

function formatDuration(startTime, endTime) {
  const diff = getDurationMinutes(startTime, endTime);
  const hours = Math.floor(diff / 60);
  const minutes = diff % 60;
  if (hours === 0) return `${minutes} min`;
  if (minutes === 0) return `${hours}h`;
  return `${hours}h ${minutes}min`;
}

function getHabitApplyFlags(
  habit,
  todayWeekday,
  yesterdayWeekday,
  todayDate,
  yesterdayDate,
) {
  const frequencyType = habit?.frequency_type;

  if (frequencyType === "weekly") {
    const weekdays = Array.isArray(habit?.weekdays) ? habit.weekdays : [];
    return {
      appliesToday: weekdays.includes(todayWeekday),
      appliesYesterday: weekdays.includes(yesterdayWeekday),
    };
  }

  if (frequencyType === "monthly") {
    const monthDay = Number(habit?.month_day);
    return {
      appliesToday: Number.isInteger(monthDay) && monthDay === todayDate,
      appliesYesterday:
        Number.isInteger(monthDay) && monthDay === yesterdayDate,
    };
  }

  return { appliesToday: true, appliesYesterday: false };
}

export default function DailyRoutine() {
  const navigate = useNavigate();
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null);
  const todayWeekday = useMemo(() => new Date().getDay(), []);
  const todayDate = useMemo(() => new Date().getDate(), []);
  const yesterdayDate = useMemo(() => {
    const date = new Date();
    date.setDate(date.getDate() - 1);
    return date.getDate();
  }, []);
  const yesterdayWeekday = useMemo(
    () => (todayWeekday + 6) % 7,
    [todayWeekday],
  );

  useEffect(() => {
    async function loadHabits() {
      try {
        const data = await habitsService.list({ include_stats: true });
        setHabits(Array.isArray(data) ? data : []);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar hábitos"));
      } finally {
        setLoading(false);
      }
    }

    loadHabits();
  }, []);

  async function handleToggle(habitId) {
    setToggling(habitId);

    try {
      const result = await habitsService.toggle(habitId);
      setHabits((prev) =>
        prev.map((habit) =>
          habit.id === habitId ? { ...habit, stats: result.stats } : habit,
        ),
      );
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (detail === "Habit is before scheduled time") {
        const habit = habits.find((h) => h.id === habitId);
        const startLabel = habit?.start_time
          ? habit.start_time.slice(0, 5)
          : "o horário definido";
        notify.error(
          `Esse hábito só pode ser marcado a partir de ${startLabel}.`,
        );
      } else {
        notify.error(getApiErrorMessage(err, "Erro ao atualizar hábito"));
      }
    } finally {
      setToggling(null);
    }
  }

  const { scheduledHabits, unscheduledHabits } = useMemo(() => {
    const scheduled = [];
    const unscheduled = [];

    habits.forEach((habit) => {
      const { appliesToday, appliesYesterday } = getHabitApplyFlags(
        habit,
        todayWeekday,
        yesterdayWeekday,
        todayDate,
        yesterdayDate,
      );
      const isOvernight =
        Boolean(habit?.start_time && habit?.end_time) &&
        timeToMinutes(habit.start_time) > timeToMinutes(habit.end_time);

      if (
        habit?.start_time &&
        (appliesToday || (isOvernight && appliesYesterday))
      ) {
        scheduled.push(habit);
      } else if (!habit?.start_time && appliesToday) {
        unscheduled.push(habit);
      }
    });

    return { scheduledHabits: scheduled, unscheduledHabits: unscheduled };
  }, [habits, todayWeekday, yesterdayWeekday, todayDate, yesterdayDate]);

  const schedule = useMemo(
    () =>
      scheduledHabits
        .flatMap((habit) => {
          const key = `${habit.id ?? habit.title ?? ""}`;
          const hash = hashString(key);
          const color = gradientPalette[hash % gradientPalette.length];
          const start = habit.start_time?.slice(0, 5);
          const end = habit.end_time?.slice(0, 5);
          const ranges = getVisualRanges(start, end);
          const { appliesToday, appliesYesterday } = getHabitApplyFlags(
            habit,
            todayWeekday,
            yesterdayWeekday,
            todayDate,
            yesterdayDate,
          );

          return ranges
            .filter((range) => {
              if (
                habit.frequency_type !== "weekly" &&
                habit.frequency_type !== "monthly"
              ) {
                return true;
              }
              if (range.period === "morning") return appliesYesterday;
              return appliesToday;
            })
            .map((range, index) => ({
              id: habit.id,
              segmentId: `${habit.id ?? key}-seg-${index}`,
              title: habit.title ?? "Hábito",
              start,
              end: end ?? "",
              duration: formatDuration(start, end),
              color,
              completed: Boolean(habit.stats?.today_completed),
              visualStart: range.visualStart,
              visualEnd: range.visualEnd,
            }));
        })
        .sort((a, b) => a.visualStart - b.visualStart),
    [scheduledHabits, todayWeekday, yesterdayWeekday, todayDate, yesterdayDate],
  );

  const timeBounds = useMemo(() => {
    if (schedule.length === 0) {
      return {
        startOfDay: defaultStartOfDay,
        endOfDay: defaultEndOfDay,
      };
    }

    const minutes = schedule.flatMap((item) => [
      item.visualStart,
      item.visualEnd,
    ]);

    const min = Math.min(...minutes);
    const max = Math.max(...minutes);

    return {
      startOfDay: Math.max(0, Math.min(defaultStartOfDay, min - 60)),
      endOfDay: Math.min(minutesInDay, Math.max(defaultEndOfDay, max + 60)),
    };
  }, [schedule]);

  const hours = useMemo(() => {
    const list = [];
    const startHour = Math.floor(timeBounds.startOfDay / 60);
    const endHour = Math.ceil(timeBounds.endOfDay / 60);
    for (let hour = startHour; hour <= endHour; hour += 1) {
      list.push(hour);
    }
    return list;
  }, [timeBounds]);

  const dayLabel = useMemo(() => {
    const now = new Date();
    return now.toLocaleDateString("pt-BR", {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
  }, []);

  const { layout, timelineHeight } = useMemo(() => {
    const totalMinutes = timeBounds.endOfDay - timeBounds.startOfDay;
    const baseHeight = Math.max(Math.round(totalMinutes * pxPerMinute), 420);
    const minHeight = 54;
    const gap = 8;

    let extraOffset = 0;
    let lastBottom = 0;

    const positioned = schedule.map((item) => {
      const startMinutes = item.visualStart - timeBounds.startOfDay;
      const endMinutes = item.visualEnd - timeBounds.startOfDay;
      const rawTop = startMinutes * pxPerMinute;
      const rawHeight = (endMinutes - startMinutes) * pxPerMinute;
      const height = Math.max(rawHeight, minHeight);
      let top = rawTop + extraOffset;

      if (top < lastBottom + gap) {
        top = lastBottom + gap;
        extraOffset = top - rawTop;
      }

      lastBottom = top + height;

      return {
        ...item,
        top,
        height,
      };
    });

    return {
      layout: positioned,
      timelineHeight: Math.max(baseHeight, Math.ceil(lastBottom + 24)),
    };
  }, [schedule, timeBounds]);

  return (
    <div
      className="relative overflow-hidden rounded-3xl border border-white/60 bg-[#f7f2e8] shadow-[0_20px_60px_rgba(18,28,38,0.18)]"
      style={{ fontFamily: '"Space Grotesk", "IBM Plex Sans", sans-serif' }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

        .float-slow {
          animation: floatSlow 12s ease-in-out infinite;
        }

        .float-slower {
          animation: floatSlow 18s ease-in-out infinite;
        }

        .shimmer {
          background-size: 200% 200%;
          animation: shimmerMove 8s ease infinite;
        }

        @keyframes floatSlow {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-18px); }
        }

        @keyframes shimmerMove {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>

      <div className="absolute -top-24 right-10 h-64 w-64 rounded-full bg-[radial-gradient(circle_at_top,#fff6d6,#f5d98f)] opacity-70 blur-3xl float-slow" />
      <div className="absolute -bottom-28 left-0 h-72 w-72 rounded-full bg-[radial-gradient(circle_at_top,#d7fff1,#9eecc9)] opacity-60 blur-3xl float-slower" />

      <header className="relative z-10 flex flex-wrap items-center justify-between gap-4 border-b border-black/10 px-8 py-6">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-gray-500">
            Rotina do Dia
          </p>
          <h1 className="text-2xl font-semibold text-gray-900 capitalize">
            {dayLabel}
          </h1>
          <p className="text-sm text-gray-600">
            {loading
              ? "Carregando hábitos do dia..."
              : `Resumo: ${scheduledHabits.length + unscheduledHabits.length} atividades, ${scheduledHabits.length} com horário.`}
          </p>
        </div>
        <Link
          to="/habits"
          className="rounded-full border border-gray-900/10 bg-white/80 px-5 py-2 text-sm font-semibold text-gray-900 transition hover:scale-[1.02] hover:bg-white"
        >
          Ir para hábitos
        </Link>
      </header>

      <div className="relative z-10 grid gap-6 px-6 pb-8 pt-4 lg:grid-cols-[120px_1fr]">
        <div className="relative hidden lg:block">
          <div className="relative" style={{ height: `${timelineHeight}px` }}>
            {hours.map((hour) => (
              <div
                key={hour}
                className="absolute left-0 flex items-center gap-3 text-xs text-gray-500"
                style={{
                  top: `${(hour * 60 - timeBounds.startOfDay) * pxPerMinute}px`,
                }}
              >
                <span className="h-2 w-2 rounded-full bg-gray-400" />
                <span>{formatHourLabel(hour)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative">
          <div
            className="relative rounded-[32px] border border-white/80 bg-white/60 p-6 shadow-inner backdrop-blur"
            style={{ height: `${timelineHeight}px` }}
          >
            {loading && (
              <div className="rounded-2xl border border-dashed border-gray-300 bg-white/70 p-6 text-sm text-gray-500">
                Carregando hábitos do dia...
              </div>
            )}

            {!loading && schedule.length === 0 && (
              <div className="rounded-2xl border border-dashed border-gray-300 bg-white/70 p-6 text-sm text-gray-500">
                Nenhum hábito com horário definido. Edite seus hábitos para
                adicionar horários e ver a rotina aqui.
              </div>
            )}

            {layout.map((item) => {
              const canEdit = Number.isInteger(item.id);

              return (
                <article
                  key={item.segmentId}
                  className={`group absolute left-4 right-4 overflow-hidden rounded-[28px] bg-gradient-to-r ${item.color} text-slate-900 shadow-[0_12px_30px_rgba(0,0,0,0.15)] transition hover:scale-[1.01] ${canEdit ? "cursor-pointer" : ""}`}
                  style={{ top: `${item.top}px`, height: `${item.height}px` }}
                  onClick={() => {
                    if (canEdit) navigate(`/habits/${item.id}/edit`);
                  }}
                  onKeyDown={(event) => {
                    if (!canEdit) return;
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      navigate(`/habits/${item.id}/edit`);
                    }
                  }}
                  role={canEdit ? "link" : undefined}
                  tabIndex={canEdit ? 0 : undefined}
                >
                  <div className="relative flex h-full flex-col justify-between px-6 py-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-xs uppercase tracking-[0.22em] text-black/50">
                          {item.start}
                          {item.end ? ` - ${item.end}` : ""}
                        </p>
                        {canEdit ? (
                          <Link
                            to={`/habits/${item.id}/edit`}
                            className="text-lg font-semibold hover:underline"
                          >
                            {item.title}
                          </Link>
                        ) : (
                          <h3 className="text-lg font-semibold">
                            {item.title}
                          </h3>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          type="button"
                          onClick={(event) => {
                            event.preventDefault();
                            event.stopPropagation();
                            handleToggle(item.id);
                          }}
                          disabled={toggling === item.id}
                          className={`h-8 min-w-[78px] rounded-md px-2 text-xs font-semibold transition ${
                            item.completed
                              ? "bg-green-600 text-white hover:bg-green-700"
                              : "bg-white/70 text-black/70 hover:bg-white"
                          } ${toggling === item.id ? "cursor-not-allowed opacity-60" : ""}`}
                          aria-label={
                            item.completed
                              ? "Desmarcar feito hoje"
                              : "Marcar feito hoje"
                          }
                          title={item.completed ? "Feito hoje" : "Marcar feito"}
                        >
                          {toggling === item.id
                            ? "Salvando"
                            : item.completed
                              ? "✓ Feito"
                              : "○ Marcar"}
                        </button>
                        <span className="rounded-full bg-white/50 px-3 py-1 text-xs font-semibold text-black/60">
                          {item.duration}
                        </span>
                      </div>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>

          {unscheduledHabits.length > 0 && (
            <div className="mt-6 rounded-2xl border border-white/60 bg-white/80 px-6 py-4 shadow-sm">
              <p className="text-xs uppercase tracking-[0.3em] text-gray-500">
                Sem Horário
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {unscheduledHabits.map((habit) => (
                  <span
                    key={habit.id ?? habit.title}
                    className="rounded-full bg-gray-900 px-3 py-1 text-xs font-semibold text-white"
                  >
                    {habit.title ?? "Hábito"}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

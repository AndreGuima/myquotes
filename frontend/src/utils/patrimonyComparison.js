export function buildPatrimonyComparisonSummary(
  points = [],
  referenceDateKey = null,
) {
  const normalizedPoints = (points || [])
    .filter((point) => Number.isFinite(Number(point?.total)))
    .map((point) => ({
      dateKey: point.dateKey,
      total: Number(point.total),
    }))
    .sort((a, b) => a.dateKey.localeCompare(b.dateKey));

  if (normalizedPoints.length === 0) {
    return [
      { label: "Patrimônio atual", value: 0 },
      { label: "Ontem", value: 0 },
      { label: "Semana passada", value: 0 },
      { label: "Mês passado", value: 0 },
    ];
  }

  const reference =
    referenceDateKey || normalizedPoints[normalizedPoints.length - 1]?.dateKey;
  if (!reference) {
    return [
      { label: "Patrimônio atual", value: 0 },
      { label: "Ontem", value: 0 },
      { label: "Semana passada", value: 0 },
      { label: "Mês passado", value: 0 },
    ];
  }

  const referenceDate = new Date(`${reference}T00:00:00`);
  const previousDay = new Date(referenceDate);
  previousDay.setDate(referenceDate.getDate() - 1);
  const previousWeek = new Date(referenceDate);
  previousWeek.setDate(referenceDate.getDate() - 7);
  const previousMonth = new Date(referenceDate);
  previousMonth.setMonth(referenceDate.getMonth() - 1);

  const findClosestPoint = (date) => {
    const target = date.toISOString().slice(0, 10);
    const exact = normalizedPoints.find((point) => point.dateKey === target);
    if (exact) return exact.total;

    let lastValue = normalizedPoints[0]?.total ?? 0;
    let lastDate = normalizedPoints[0]?.dateKey;

    for (const point of normalizedPoints) {
      if (point.dateKey > target) break;
      lastValue = point.total;
      lastDate = point.dateKey;
    }

    return lastDate && lastDate <= target
      ? lastValue
      : (normalizedPoints[0]?.total ?? 0);
  };

  return [
    {
      label: "Patrimônio atual",
      value: normalizedPoints[normalizedPoints.length - 1]?.total ?? 0,
    },
    { label: "Ontem", value: findClosestPoint(previousDay) },
    { label: "Semana passada", value: findClosestPoint(previousWeek) },
    { label: "Mês passado", value: findClosestPoint(previousMonth) },
  ];
}

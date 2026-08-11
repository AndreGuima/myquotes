export function parseLocalDate(value) {
  const raw = String(value || "");
  const match = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);

  if (match) {
    const [, year, month, day] = match;
    return new Date(Number(year), Number(month) - 1, Number(day));
  }

  const date = new Date(raw);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function localDateTimestamp(value) {
  return parseLocalDate(value)?.getTime() || 0;
}

export function localMonthKey(value) {
  const date = parseLocalDate(value);
  if (!date) return null;

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
}

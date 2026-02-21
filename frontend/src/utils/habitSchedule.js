export function isMonthlyHabitForDate(monthDay, targetDate) {
  if (!Number.isInteger(monthDay)) return false;

  const year = targetDate.getFullYear();
  const month = targetDate.getMonth();
  const lastDayOfMonth = new Date(year, month + 1, 0).getDate();
  const effectiveDay = Math.min(monthDay, lastDayOfMonth);

  return targetDate.getDate() === effectiveDay;
}

export function isHabitScheduledForDate(habit, targetDate) {
  const frequency = habit?.frequency_type;

  if (frequency === "daily") {
    return true;
  }

  if (frequency === "weekly") {
    const weekdays = Array.isArray(habit?.weekdays) ? habit.weekdays : [];
    return weekdays.includes(targetDate.getDay());
  }

  if (frequency === "monthly") {
    const monthDay = Number(habit?.month_day);
    return isMonthlyHabitForDate(monthDay, targetDate);
  }

  return false;
}

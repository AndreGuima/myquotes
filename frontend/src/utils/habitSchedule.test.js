import assert from "node:assert/strict";
import test from "node:test";
import { isHabitScheduledForDate } from "./habitSchedule.js";

test("monthly habit with day 31 applies on February 28 in non-leap year", () => {
  const habit = {
    frequency_type: "monthly",
    month_day: 31,
  };

  assert.equal(isHabitScheduledForDate(habit, new Date(2025, 1, 28, 12)), true);
  assert.equal(
    isHabitScheduledForDate(habit, new Date(2025, 1, 27, 12)),
    false,
  );
});

test("monthly habit with day 31 applies on February 29 in leap year", () => {
  const habit = {
    frequency_type: "monthly",
    month_day: 31,
  };

  assert.equal(isHabitScheduledForDate(habit, new Date(2024, 1, 29, 12)), true);
  assert.equal(
    isHabitScheduledForDate(habit, new Date(2024, 1, 28, 12)),
    false,
  );
});

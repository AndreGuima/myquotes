import test from "node:test";
import assert from "node:assert/strict";

import { buildPatrimonyComparisonSummary } from "./patrimonyComparison.js";

test("buildPatrimonyComparisonSummary returns current, yesterday, week and month values", () => {
  const points = [
    { dateKey: "2024-01-01", total: 100 },
    { dateKey: "2024-01-08", total: 130 },
    { dateKey: "2024-01-31", total: 140 },
    { dateKey: "2024-02-01", total: 150 },
  ];

  const summary = buildPatrimonyComparisonSummary(points, "2024-02-01");

  assert.deepEqual(
    summary.map((item) => item.label),
    ["Patrimônio atual", "Ontem", "Semana passada", "Mês passado"],
  );
  assert.equal(summary[0].value, 150);
  assert.equal(summary[1].value, 140);
  assert.equal(summary[2].value, 130);
  assert.equal(summary[3].value, 100);
});

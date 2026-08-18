import api from "./api";

const reportsService = {
  dailyCashflow(filters = {}) {
    const params = new URLSearchParams();
    if (filters.from) params.set("from", filters.from);
    if (filters.to) params.set("to", filters.to);
    const query = params.toString();
    return api.get(
      query ? `/reports/daily-cashflow?${query}` : "/reports/daily-cashflow",
    );
  },
};

export default reportsService;

import api from "./api";

const investmentIncomesService = {
  list(filters = {}) {
    const params = new URLSearchParams();

    if (filters.fromDate) params.set("from", filters.fromDate);
    if (filters.toDate) params.set("to", filters.toDate);

    const query = params.toString();
    return api.get(
      query ? `/investment-incomes?${query}` : "/investment-incomes",
    );
  },

  create(payload) {
    return api.post("/investment-incomes", payload);
  },

  update(id, payload) {
    return api.patch(`/investment-incomes/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/investment-incomes/${id}`);
  },
};

export default investmentIncomesService;

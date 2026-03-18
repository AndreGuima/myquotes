import api from "./api";

const investmentsService = {
  async list() {
    return api.get("/investments");
  },

  async create(payload) {
    return api.post("/investments", payload);
  },

  async update(id, payload) {
    return api.patch(`/investments/${id}`, payload);
  },

  async remove(id) {
    return api.delete(`/investments/${id}`);
  },

  async syncPrices() {
    return api.post("/investments/sync-prices");
  },

  async history(id, params = {}) {
    const query = new URLSearchParams();
    if (params.limit) {
      query.set("limit", String(params.limit));
    }
    const suffix = query.toString();
    return api.get(
      suffix
        ? `/investments/${id}/price-history?${suffix}`
        : `/investments/${id}/price-history`,
    );
  },
};

export default investmentsService;

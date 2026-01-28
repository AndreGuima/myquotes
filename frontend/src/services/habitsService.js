import api from "./api";

const habitsService = {
  async list() {
    return api.get("/habits/");
  },

  async create(payload) {
    return api.post("/habits/", payload);
  },

  async update(id, payload) {
    return api.patch(`/habits/${id}/`, payload);
  },

  async toggle(habitId) {
    return api.post(`/habits/${habitId}/toggle/`);
  },

  async stats(habitId) {
    return api.get(`/habits/${habitId}/stats/`);
  },

  async history(habitId, params = {}) {
    return api.get(`/habits/${habitId}/history`, { params });
  },

  async heatmap(habitId, days = 90) {
    return api.get(`/habits/${habitId}/heatmap`, {
      params: { days },
    });
  },
};

export default habitsService;

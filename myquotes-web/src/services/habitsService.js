import api from "./api";

const habitsService = {
  async list() {
    const res = await api.get("/habits/");
    return res.data;
  },

  async create(payload) {
    const res = await api.post("/habits/", payload);
    return res.data;
  },

  async update(id, payload) {
    const res = await api.patch(`/habits/${id}/`, payload);
    return res.data;
  },

  async toggle(habitId) {
    const res = await api.post(`/habits/${habitId}/toggle/`);
    return res.data;
  },

  async stats(habitId) {
    const res = await api.get(`/habits/${habitId}/stats/`);
    return res.data;
  },

  async history(habitId, params = {}) {
    const res = await api.get(`/habits/${habitId}/history`, { params });
    return res.data;
  },
};

export default habitsService;

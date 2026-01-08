import api from "./api";

const preferencesService = {
  async get(category) {
    const res = await api.get(`/preferences/${category}`);
    return res.data;
  },

  async update(category, preferences) {
    const res = await api.put(`/preferences/${category}`, {
      preferences,
    });
    return res.data;
  },
};

export default preferencesService;

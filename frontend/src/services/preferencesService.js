import api from "./api";

const preferencesService = {
  async get(category) {
    return api.get(`/preferences/${category}`);
  },

  async update(category, preferences) {
    return api.put(`/preferences/${category}`, {
      preferences,
    });
  },
};

export default preferencesService;

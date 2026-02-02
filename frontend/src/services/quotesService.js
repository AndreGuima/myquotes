import api from "./api";

const quotesService = {
  async list() {
    return api.get("/quotes");
  },

  async getById(id) {
    return api.get(`/quotes/${id}`);
  },

  async create(data) {
    return api.post("/quotes", data);
  },

  async update(id, data) {
    return api.put(`/quotes/${id}`, data);
  },

  async remove(id) {
    return api.delete(`/quotes/${id}`);
  },

  async getQuoteOfTheDay() {
    return api.get("/quotes/of-the-day");
  },
};

export default quotesService;

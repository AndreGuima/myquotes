import api from "./api";

const quotesService = {
  async list() {
    const res = await api.get("/quotes");
    return res.data;
  },

  async getById(id) {
    const res = await api.get(`/quotes/${id}`);
    return res.data;
  },

  async create(data) {
    const res = await api.post("/quotes", data);
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/quotes/${id}`, data);
    return res.data;
  },

  async remove(id) {
    const res = await api.delete(`/quotes/${id}`);
    return res.data;
  },

  async getQuoteOfTheDay() {
    const res = await api.get("/quotes/of-the-day");
    return res.data;
  },
};

export default quotesService;

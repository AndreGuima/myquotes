import api from "./api";

const readingListService = {
  list(status) {
    const params = status ? { status } : undefined;
    return api.get("/reading-list", { params });
  },

  get(id) {
    return api.get(`/reading-list/${id}`);
  },

  create(payload) {
    return api.post("/reading-list", payload);
  },

  update(id, payload) {
    return api.patch(`/reading-list/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/reading-list/${id}`);
  },

  listLogs(bookId, limit = 30) {
    return api.get(`/reading-list/${bookId}/logs`, { params: { limit } });
  },

  upsertLog(bookId, payload) {
    return api.post(`/reading-list/${bookId}/logs`, payload);
  },
};

export default readingListService;

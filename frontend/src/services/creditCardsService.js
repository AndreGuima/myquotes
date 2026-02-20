import api from "./api";

const creditCardsService = {
  list() {
    return api.get("/credit-cards");
  },

  create(payload) {
    return api.post("/credit-cards", payload);
  },

  update(id, payload) {
    return api.patch(`/credit-cards/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/credit-cards/${id}`);
  },
};

export default creditCardsService;

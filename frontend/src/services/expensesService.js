import api from "./api";

const expensesService = {
  list() {
    return api.get("/expenses");
  },

  create(payload) {
    return api.post("/expenses", payload);
  },

  update(id, payload) {
    return api.patch(`/expenses/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/expenses/${id}`);
  },
};

export default expensesService;

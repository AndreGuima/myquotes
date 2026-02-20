import api from "./api";

const expenseCategoriesService = {
  list() {
    return api.get("/expense-categories");
  },

  create(payload) {
    return api.post("/expense-categories", payload);
  },

  update(id, payload) {
    return api.patch(`/expense-categories/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/expense-categories/${id}`);
  },
};

export default expenseCategoriesService;

import api from "./api";

const bankAccountsService = {
  list() {
    return api.get("/bank-accounts");
  },

  create(payload) {
    return api.post("/bank-accounts", payload);
  },

  update(id, payload) {
    return api.patch(`/bank-accounts/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/bank-accounts/${id}`);
  },
};

export default bankAccountsService;

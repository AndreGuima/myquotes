import api from "./api";

const bankAccountsService = {
  list() {
    return api.get("/bank-accounts");
  },

  snapshots(days = 365) {
    return api.get("/bank-accounts/patrimony-snapshots", {
      params: { days },
    });
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

import api from "./api";

const dreamsService = {
  list() {
    return api.get("/dreams");
  },

  create(payload) {
    return api.post("/dreams", payload);
  },

  update(id, payload) {
    return api.patch(`/dreams/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/dreams/${id}`);
  },

  toggleMilestone(dreamId, milestoneId) {
    return api.post(`/dreams/${dreamId}/milestones/${milestoneId}/toggle`);
  },
};

export default dreamsService;

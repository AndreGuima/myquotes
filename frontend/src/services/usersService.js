import api from "./api";

const usersService = {
  async getAll() {
    return api.get("/admin/users");
  },

  async update(id, data) {
    return api.put(`/admin/users/${id}`, data);
  },

  async remove(id) {
    return api.delete(`/admin/users/${id}`);
  },

  async restore(id) {
    return api.post(`/admin/users/${id}/restore`);
  },
};

export default usersService;

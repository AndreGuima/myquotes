import api from "./api";

const usersService = {
  async getAll() {
    const res = await api.get("/admin/users");
    return res.data;
  },

  async update(id, data) {
    const res = await api.put(`/admin/users/${id}`, data);
    return res.data;
  },

  async remove(id) {
    const res = await api.delete(`/admin/users/${id}`);
    return res.data;
  },

  async restore(id) {
    const res = await api.post(`/admin/users/${id}/restore`);
    return res.data;
  },
};

export default usersService;

import api from "./api";

const usersService = {
  getAll: () => api.get("/admin/users"),
  update: (id, data) => api.put(`/admin/users/${id}`, data),
  remove: (id) => api.delete(`/admin/users/${id}`),
};

export default usersService;


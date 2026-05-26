import api from "./api";

const notesService = {
  list() {
    return api.get("/notes");
  },

  create(payload) {
    return api.post("/notes", payload);
  },

  update(id, payload) {
    return api.patch(`/notes/${id}`, payload);
  },

  remove(id) {
    return api.delete(`/notes/${id}`);
  },
};

export default notesService;

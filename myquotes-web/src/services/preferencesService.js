import api from "./api";

export function getPreferences(category) {
  return api.get(`/preferences/${category}`).then((res) => res.data);
}

export function updatePreferences(category, preferences) {
  return api
    .put(`/preferences/${category}`, {
      preferences,
    })
    .then((res) => res.data);
}

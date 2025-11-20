import api from "./api";

export async function getQuotes() {
  const response = await api.get("/quotes");
  return response.data;
}

export async function getQuoteById(id) {
  const response = await api.get(`/quotes/${id}`);
  return response.data;
}

export async function createQuote(data) {
  const response = await api.post("/quotes", data);
  return response.data;
}

export async function updateQuote(id, data) {
  const response = await api.put(`/quotes/${id}`, data);
  return response.data;
}

export async function deleteQuote(id) {
  const response = await api.delete(`/quotes/${id}`);
  return response.data;
}

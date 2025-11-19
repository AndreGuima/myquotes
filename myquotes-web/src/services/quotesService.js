// -------------------------------------------------------------
// 📌 MyQuotes Web - Quote Service
// -------------------------------------------------------------

import api from "./api";

// Função auxiliar para pegar token
function authHeader() {
  const token = localStorage.getItem("token");
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

// ================================
// 🔍 LISTAR TODAS AS QUOTES
// ================================
export async function getQuotes() {
  const response = await api.get("/quotes");
  return response.data;
}

// ================================
// 🔍 BUSCAR QUOTE POR ID
// ================================
export async function getQuoteById(id) {
  const response = await api.get(`/quotes/${id}`);
  return response.data;
}

// ================================
// ➕ CRIAR NOVA QUOTE
// ================================
export async function createQuote(data) {
  // Ajuste 1: rota correta é /quotes/
  // Ajuste 2: precisa de Bearer Token!
  const response = await api.post("/quotes/", data, authHeader());
  return response.data;
}

// ================================
// ✏️ ATUALIZAR QUOTE
// ================================
export async function updateQuote(id, data) {
  const response = await api.put(`/quotes/${id}`, data, authHeader());
  return response.data;
}

// ================================
// ❌ DELETAR QUOTE
// ================================
export async function deleteQuote(id) {
  const response = await api.delete(`/quotes/${id}`, authHeader());
  return response.data;
}

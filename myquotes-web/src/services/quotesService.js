// -------------------------------------------------------------
// 📌 MyQuotes Web - Quote Service
// Camada responsável por todas as requisições relacionadas
// às quotes: listar, buscar, criar, atualizar e deletar.
// -------------------------------------------------------------

import api from "./api";

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
  const response = await api.post("/quotes", data);
  return response.data;
}

// ================================
// ✏️ ATUALIZAR QUOTE
// ================================
export async function updateQuote(id, data) {
  const response = await api.put(`/quotes/${id}`, data);
  return response.data;
}

// ================================
// ❌ DELETAR QUOTE
// ================================
export async function deleteQuote(id) {
  const response = await api.delete(`/quotes/${id}`);
  return response.data;
}

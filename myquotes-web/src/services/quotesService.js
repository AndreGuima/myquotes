const API_URL = "http://localhost:8000"; // ajuste se necessário

export async function getQuotes() {
  const res = await fetch(`${API_URL}/quotes`);
  if (!res.ok) throw new Error("Erro ao buscar quotes");
  return await res.json();
}

export async function getQuoteById(id) {
  const res = await fetch(`${API_URL}/quotes/${id}`);
  if (!res.ok) throw new Error("Erro ao buscar quote");
  return await res.json();
}

export async function createQuote(data) {
  const res = await fetch(`${API_URL}/quotes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Erro ao criar quote");
  return await res.json();
}

export async function updateQuote(id, data) {
  const res = await fetch(`${API_URL}/quotes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Erro ao atualizar quote");
  return await res.json();
}

export async function deleteQuote(id) {
  const res = await fetch(`${API_URL}/quotes/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Erro ao deletar quote");
  return true;
}

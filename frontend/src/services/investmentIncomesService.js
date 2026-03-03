const INVESTMENT_INCOMES_STORAGE_KEY = "myquotes_investment_incomes_v1";

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(INVESTMENT_INCOMES_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveToStorage(items) {
  localStorage.setItem(INVESTMENT_INCOMES_STORAGE_KEY, JSON.stringify(items));
}

function createId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return `inc_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

const investmentIncomesService = {
  async list() {
    return loadFromStorage();
  },

  async create(payload) {
    const items = loadFromStorage();
    const item = {
      id: createId(),
      income_type: String(payload.income_type || "dividend"),
      ticker: String(payload.ticker || "")
        .trim()
        .toUpperCase(),
      received_at: String(payload.received_at || ""),
      amount: Number(payload.amount || 0),
      notes: String(payload.notes || "").trim(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    items.push(item);
    saveToStorage(items);
    return item;
  },

  async update(id, payload) {
    const items = loadFromStorage();
    const index = items.findIndex((item) => item.id === id);

    if (index < 0) {
      throw new Error("Lançamento de provento não encontrado");
    }

    const updated = {
      ...items[index],
      income_type: String(payload.income_type || "dividend"),
      ticker: String(payload.ticker || "")
        .trim()
        .toUpperCase(),
      received_at: String(payload.received_at || ""),
      amount: Number(payload.amount || 0),
      notes: String(payload.notes || "").trim(),
      updated_at: new Date().toISOString(),
    };

    items[index] = updated;
    saveToStorage(items);
    return updated;
  },

  async remove(id) {
    const items = loadFromStorage();
    const next = items.filter((item) => item.id !== id);
    saveToStorage(next);
    return { success: true };
  },
};

export default investmentIncomesService;

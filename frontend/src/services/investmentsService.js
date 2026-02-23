import { normalizeInvestmentSector } from "../constants/investmentSectors";

const INVESTMENTS_STORAGE_KEY = "myquotes_investments_v1";

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(INVESTMENTS_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveToStorage(items) {
  localStorage.setItem(INVESTMENTS_STORAGE_KEY, JSON.stringify(items));
}

function createId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  return `inv_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

const investmentsService = {
  async list() {
    return loadFromStorage();
  },

  async create(payload) {
    const items = loadFromStorage();
    const item = {
      id: createId(),
      asset_type: payload.asset_type,
      sector: normalizeInvestmentSector(payload.asset_type, payload.sector),
      ticker: String(payload.ticker || "")
        .trim()
        .toUpperCase(),
      name: String(payload.name || "").trim(),
      quantity: Number(payload.quantity || 0),
      average_price: Number(payload.average_price || 0),
      current_price: Number(payload.current_price || 0),
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
      throw new Error("Investimento não encontrado");
    }

    const existing = items[index];
    const updated = {
      ...existing,
      asset_type: payload.asset_type,
      sector: normalizeInvestmentSector(payload.asset_type, payload.sector),
      ticker: String(payload.ticker || "")
        .trim()
        .toUpperCase(),
      name: String(payload.name || "").trim(),
      quantity: Number(payload.quantity || 0),
      average_price: Number(payload.average_price || 0),
      current_price: Number(payload.current_price || 0),
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

export default investmentsService;

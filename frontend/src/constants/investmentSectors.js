export const INVESTMENT_SECTORS_BY_ASSET_TYPE = Object.freeze({
  stock: Object.freeze([
    "Financeiro",
    "Utilidade Pública",
    "Materiais Básicos",
    "Petróleo/Gás",
  ]),
  fii: Object.freeze(["Papel", "Logistico", "Lajes", "Shopping"]),
});

export function normalizeInvestmentSector(assetType, sector) {
  const options = INVESTMENT_SECTORS_BY_ASSET_TYPE[assetType] || [];
  const normalized = String(sector || "").trim();
  return options.includes(normalized) ? normalized : "";
}

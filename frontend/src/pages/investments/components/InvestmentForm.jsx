import {
  INVESTMENT_SECTORS_BY_ASSET_TYPE,
  normalizeInvestmentSector,
} from "../../../constants/investmentSectors";

function getSectorOptions(assetType) {
  return INVESTMENT_SECTORS_BY_ASSET_TYPE[assetType] || [];
}

export default function InvestmentForm({
  editingId,
  form,
  setForm,
  saving,
  onSubmit,
  onCancelEdit,
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="themed-card themed-border border rounded-xl p-5 mb-6"
    >
      <h2 className="text-xl font-semibold mb-4">
        {editingId ? "Editar investimento" : "Novo investimento"}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-8 gap-3">
        <select
          className="themed-input rounded px-3 py-2"
          value={form.assetType}
          onChange={(e) => {
            const nextAssetType = e.target.value;
            setForm((prev) => ({
              ...prev,
              assetType: nextAssetType,
              sector: normalizeInvestmentSector(nextAssetType, prev.sector),
            }));
          }}
        >
          <option value="stock">Ação</option>
          <option value="fii">FII</option>
        </select>

        <select
          className="themed-input rounded px-3 py-2"
          value={form.sector}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, sector: e.target.value }))
          }
        >
          <option value="">Setor (opcional)</option>
          {getSectorOptions(form.assetType).map((sector) => (
            <option key={sector} value={sector}>
              {sector}
            </option>
          ))}
        </select>

        <input
          type="text"
          className="themed-input rounded px-3 py-2"
          placeholder="Ticker (ex: PETR4)"
          value={form.ticker}
          onChange={(e) =>
            setForm((prev) => ({
              ...prev,
              ticker: e.target.value.toUpperCase(),
            }))
          }
        />

        <input
          type="text"
          className="themed-input rounded px-3 py-2 md:col-span-2"
          placeholder="Nome do ativo"
          value={form.name}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, name: e.target.value }))
          }
        />

        <input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          className="themed-input rounded px-3 py-2"
          placeholder="Quantidade"
          value={form.quantity}
          onChange={(e) =>
            setForm((prev) => ({
              ...prev,
              quantity: e.target.value.replace(/\D/g, ""),
            }))
          }
        />

        <input
          type="number"
          step="0.0001"
          min="0"
          className="themed-input rounded px-3 py-2"
          placeholder="Preço médio"
          value={form.averagePrice}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, averagePrice: e.target.value }))
          }
        />
      </div>

      <p className="themed-muted text-sm mt-3">
        O preço atual é sincronizado automaticamente via BRAPI e salvo no
        histórico.
      </p>
      <div className="flex gap-2 mt-4">
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-60"
          disabled={saving}
        >
          {saving
            ? "Salvando..."
            : editingId
              ? "Salvar alterações"
              : "Cadastrar"}
        </button>

        {editingId && (
          <button
            type="button"
            onClick={onCancelEdit}
            className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
          >
            Cancelar edição
          </button>
        )}
      </div>
    </form>
  );
}

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import investmentsService from "../services/investmentsService";
import { confirm, notify } from "../core/toast";
import {
  INVESTMENT_SECTORS_BY_ASSET_TYPE,
  normalizeInvestmentSector,
} from "../constants/investmentSectors";

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function getInitialForm() {
  return {
    assetType: "stock",
    sector: "",
    ticker: "",
    name: "",
    quantity: "",
    averagePrice: "",
    currentPrice: "",
  };
}

function getAssetTypeLabel(type) {
  if (type === "fii") return "FII";
  return "Ação";
}

function getSectorOptions(assetType) {
  return INVESTMENT_SECTORS_BY_ASSET_TYPE[assetType] || [];
}

export default function Investments() {
  const [investments, setInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState(null);
  const [editingId, setEditingId] = useState(null);

  const [form, setForm] = useState(getInitialForm);
  const [filters, setFilters] = useState({
    query: "",
    assetType: "",
  });

  useEffect(() => {
    async function loadData() {
      try {
        const data = await investmentsService.list();
        setInvestments(Array.isArray(data) ? data : []);
      } catch {
        notify.error("Erro ao carregar investimentos");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const totalInvested = useMemo(
    () =>
      investments.reduce(
        (acc, item) =>
          acc + Number(item.quantity || 0) * Number(item.average_price || 0),
        0,
      ),
    [investments],
  );

  const totalCurrent = useMemo(
    () =>
      investments.reduce(
        (acc, item) =>
          acc + Number(item.quantity || 0) * Number(item.current_price || 0),
        0,
      ),
    [investments],
  );

  const profitability = useMemo(() => {
    if (totalInvested <= 0) return 0;
    return ((totalCurrent - totalInvested) / totalInvested) * 100;
  }, [totalCurrent, totalInvested]);

  const filteredInvestments = useMemo(() => {
    const normalizedQuery = filters.query.trim().toLowerCase();

    return investments.filter((item) => {
      const matchesType = filters.assetType
        ? item.asset_type === filters.assetType
        : true;

      const matchesQuery = normalizedQuery
        ? [item.ticker, item.name, item.sector]
            .filter(Boolean)
            .join(" ")
            .toLowerCase()
            .includes(normalizedQuery)
        : true;

      return matchesType && matchesQuery;
    });
  }, [investments, filters]);

  function resetForm() {
    setForm(getInitialForm());
    setEditingId(null);
  }

  function startEditing(item) {
    setEditingId(item.id);
    setForm({
      assetType: item.asset_type || "stock",
      sector: normalizeInvestmentSector(item.asset_type, item.sector),
      ticker: String(item.ticker || ""),
      name: String(item.name || ""),
      quantity: String(item.quantity || ""),
      averagePrice: String(item.average_price || ""),
      currentPrice: String(item.current_price || ""),
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();

    const quantity = Number(form.quantity);
    const averagePrice = Number(form.averagePrice);
    const currentPrice = Number(form.currentPrice);
    const ticker = form.ticker.trim().toUpperCase();

    if (!ticker) {
      notify.error("Informe o ticker do ativo");
      return;
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      notify.error("Informe uma quantidade válida");
      return;
    }

    if (!Number.isFinite(averagePrice) || averagePrice < 0) {
      notify.error("Informe um preço médio válido");
      return;
    }

    if (!Number.isFinite(currentPrice) || currentPrice < 0) {
      notify.error("Informe um preço atual válido");
      return;
    }

    const payload = {
      asset_type: form.assetType,
      sector: normalizeInvestmentSector(form.assetType, form.sector),
      ticker,
      name: form.name,
      quantity,
      average_price: averagePrice,
      current_price: currentPrice,
    };

    setSaving(true);
    try {
      if (editingId) {
        const updated = await investmentsService.update(editingId, payload);
        setInvestments((prev) =>
          prev.map((item) => (item.id === editingId ? updated : item)),
        );
        notify.success("Investimento atualizado");
      } else {
        const created = await investmentsService.create(payload);
        setInvestments((prev) => [...prev, created]);
        notify.success("Investimento cadastrado");
      }

      resetForm();
    } catch {
      notify.error("Erro ao salvar investimento");
    } finally {
      setSaving(false);
    }
  }

  function handleRemove(id) {
    confirm({
      message: "Deseja remover este investimento?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        setRemovingId(id);
        try {
          await investmentsService.remove(id);
          setInvestments((prev) => prev.filter((item) => item.id !== id));
          if (editingId === id) resetForm();
          notify.success("Investimento removido");
        } catch {
          notify.error("Erro ao remover investimento");
        } finally {
          setRemovingId(null);
        }
      },
    });
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Investimentos</h1>
        <Link
          to="/finances"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Finanças
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Cadastre suas ações e FIIs para acompanhar posição e rentabilidade.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Valor Investido</h2>
          <p className="text-2xl font-bold">{formatCurrency(totalInvested)}</p>
          <p className="themed-muted text-sm mt-1">Baseado no preço médio</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Valor Atual</h2>
          <p className="text-2xl font-bold">{formatCurrency(totalCurrent)}</p>
          <p className="themed-muted text-sm mt-1">Posição atual da carteira</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Rentabilidade</h2>
          <p
            className={`text-2xl font-bold ${
              profitability >= 0 ? "text-green-600" : "text-red-600"
            }`}
          >
            {profitability.toFixed(2)}%
          </p>
          <p className="themed-muted text-sm mt-1">
            {formatCurrency(totalCurrent - totalInvested)} no total
          </p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Dashboards</h2>
          <p className="themed-muted text-sm mt-1 mb-4">
            Visualize a carteira por setor em ações e FIIs.
          </p>
          <Link
            to="/finances/investments/dashboards"
            className="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Abrir dashboard
          </Link>
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
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
            type="number"
            step="0.0001"
            min="0"
            className="themed-input rounded px-3 py-2"
            placeholder="Quantidade"
            value={form.quantity}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, quantity: e.target.value }))
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

          <input
            type="number"
            step="0.0001"
            min="0"
            className="themed-input rounded px-3 py-2"
            placeholder="Preço atual"
            value={form.currentPrice}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, currentPrice: e.target.value }))
            }
          />
        </div>

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
              onClick={resetForm}
              className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
            >
              Cancelar edição
            </button>
          )}
        </div>
      </form>

      <div className="themed-card themed-border border rounded-xl p-5 mb-4">
        <h2 className="text-xl font-semibold mb-4">Filtrar carteira</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            className="themed-input rounded px-3 py-2"
            placeholder="Buscar por ticker ou nome"
            value={filters.query}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, query: e.target.value }))
            }
          />

          <select
            className="themed-input rounded px-3 py-2"
            value={filters.assetType}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, assetType: e.target.value }))
            }
          >
            <option value="">Todos os tipos</option>
            <option value="stock">Ação</option>
            <option value="fii">FII</option>
          </select>

          <button
            type="button"
            onClick={() => setFilters({ query: "", assetType: "" })}
            className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
          >
            Limpar filtros
          </button>
        </div>
      </div>

      <div className="themed-card themed-border border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="themed-subtle">
              <tr>
                <th className="py-3 px-4">Tipo</th>
                <th className="py-3 px-4">Setor</th>
                <th className="py-3 px-4">Ticker</th>
                <th className="py-3 px-4">Nome</th>
                <th className="py-3 px-4 text-right">Qtd</th>
                <th className="py-3 px-4 text-right">Preço Médio</th>
                <th className="py-3 px-4 text-right">Preço Atual</th>
                <th className="py-3 px-4 text-right">Investido</th>
                <th className="py-3 px-4 text-right">Atual</th>
                <th className="py-3 px-4 text-right">Resultado</th>
                <th className="py-3 px-4 text-right">Ações</th>
              </tr>
            </thead>

            <tbody>
              {!loading && filteredInvestments.length === 0 && (
                <tr>
                  <td colSpan={11} className="py-6 text-center themed-muted">
                    Nenhum investimento cadastrado.
                  </td>
                </tr>
              )}

              {filteredInvestments.map((item) => {
                const invested =
                  Number(item.quantity || 0) * Number(item.average_price || 0);
                const current =
                  Number(item.quantity || 0) * Number(item.current_price || 0);
                const result = current - invested;

                return (
                  <tr key={item.id} className="border-t themed-border">
                    <td className="py-3 px-4">
                      {getAssetTypeLabel(item.asset_type)}
                    </td>
                    <td className="py-3 px-4">{item.sector || "-"}</td>
                    <td className="py-3 px-4 font-semibold">{item.ticker}</td>
                    <td className="py-3 px-4">{item.name || "-"}</td>
                    <td className="py-3 px-4 text-right">
                      {Number(item.quantity || 0)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {formatCurrency(item.average_price)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {formatCurrency(item.current_price)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {formatCurrency(invested)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {formatCurrency(current)}
                    </td>
                    <td
                      className={`py-3 px-4 text-right font-semibold ${
                        result >= 0 ? "text-green-600" : "text-red-600"
                      }`}
                    >
                      {formatCurrency(result)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="inline-flex gap-2">
                        <button
                          type="button"
                          onClick={() => startEditing(item)}
                          className="themed-card themed-border border px-3 py-1 rounded hover:opacity-90"
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          onClick={() => handleRemove(item.id)}
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded disabled:opacity-60"
                          disabled={removingId === item.id}
                        >
                          {removingId === item.id ? "Removendo..." : "Excluir"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

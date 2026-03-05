import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { confirm, notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";
import bankAccountsService from "../services/bankAccountsService";
import investmentIncomesService from "../services/investmentIncomesService";
import investmentsService from "../services/investmentsService";

const INCOME_TYPE_OPTIONS = [
  { value: "dividend", label: "Dividendo" },
  { value: "jcp", label: "JCP" },
  { value: "rendimento", label: "Rendimento" },
];

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function getInitialForm() {
  return {
    incomeType: "dividend",
    ticker: "",
    accountId: "",
    receivedAt: new Date().toISOString().slice(0, 10),
    amount: "",
  };
}

function getIncomeTypeLabel(value) {
  return (
    INCOME_TYPE_OPTIONS.find((option) => option.value === value)?.label ||
    "Dividendo"
  );
}

function toTimestamp(value) {
  const ts = new Date(value || "").getTime();
  return Number.isFinite(ts) ? ts : 0;
}

function parseLocaleAmount(value) {
  const raw = String(value || "").trim();
  if (!raw) return Number.NaN;

  const validFormat =
    /^(0|[1-9]\d*)(,\d+)?$/.test(raw) ||
    /^(0|[1-9]\d*)\.\d+$/.test(raw) ||
    /^([1-9]\d{0,2})(\.\d{3})+(,\d+)?$/.test(raw);

  if (!validFormat) return Number.NaN;

  const hasComma = raw.includes(",");
  const hasDot = raw.includes(".");

  let normalized = raw.replace(/\s+/g, "");

  if (hasComma && hasDot) {
    normalized = normalized.replace(/\./g, "").replace(",", ".");
  } else if (hasComma) {
    normalized = normalized.replace(",", ".");
  }

  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : Number.NaN;
}

function getErrorMessage(error, fallback) {
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return getApiErrorMessage(error, fallback);
}

export default function InvestmentIncomes() {
  const [items, setItems] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [availableTickers, setAvailableTickers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(getInitialForm);

  useEffect(() => {
    async function loadData() {
      try {
        const [incomesData, investmentsData, accountsData] = await Promise.all([
          investmentIncomesService.list(),
          investmentsService.list(),
          bankAccountsService.list(),
        ]);

        setItems(Array.isArray(incomesData) ? incomesData : []);
        setAccounts(Array.isArray(accountsData) ? accountsData : []);
        const tickers = Array.isArray(investmentsData)
          ? [
              ...new Set(
                investmentsData
                  .map((item) =>
                    String(item.ticker || "")
                      .trim()
                      .toUpperCase(),
                  )
                  .filter(Boolean),
              ),
            ].sort((a, b) =>
              a.localeCompare(b, "pt-BR", { sensitivity: "base" }),
            )
          : [];
        setAvailableTickers(tickers);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar dividendos"));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => {
      const byDate = toTimestamp(b.received_at) - toTimestamp(a.received_at);
      if (byDate !== 0) return byDate;
      return toTimestamp(b.created_at) - toTimestamp(a.created_at);
    });
  }, [items]);

  const totalAmount = useMemo(
    () => items.reduce((acc, item) => acc + Number(item.amount || 0), 0),
    [items],
  );
  const tickerOptions = useMemo(() => {
    if (!form.ticker || availableTickers.includes(form.ticker)) {
      return availableTickers;
    }
    return [form.ticker, ...availableTickers];
  }, [availableTickers, form.ticker]);
  const accountOptions = useMemo(() => {
    const sorted = [...accounts].sort((a, b) =>
      String(a.name || "").localeCompare(String(b.name || ""), "pt-BR", {
        sensitivity: "base",
      }),
    );
    if (
      !form.accountId ||
      sorted.some((item) => String(item.id) === form.accountId)
    ) {
      return sorted;
    }

    return [
      {
        id: form.accountId,
        name: `Conta #${form.accountId}`,
      },
      ...sorted,
    ];
  }, [accounts, form.accountId]);
  const accountNameById = useMemo(() => {
    const map = new Map();
    accounts.forEach((account) => {
      map.set(String(account.id), String(account.name || ""));
    });
    return map;
  }, [accounts]);

  function resetForm() {
    setForm(getInitialForm());
    setEditingId(null);
  }

  function startEditing(item) {
    setEditingId(item.id);
    setForm({
      incomeType: String(item.income_type || "dividend"),
      ticker: String(item.ticker || ""),
      accountId: item.bank_account_id ? String(item.bank_account_id) : "",
      receivedAt: String(item.received_at || "").slice(0, 10),
      amount: String(item.amount || ""),
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();

    const ticker = form.ticker.trim().toUpperCase();
    const bankAccountId = Number(form.accountId);
    const amount = parseLocaleAmount(form.amount);
    const receivedAt = String(form.receivedAt || "").trim();
    const receivedDate = new Date(`${receivedAt}T00:00:00`);

    if (!ticker) {
      notify.error("Informe o ticker");
      return;
    }
    if (availableTickers.length === 0) {
      notify.error("Cadastre ao menos um investimento para selecionar ticker");
      return;
    }

    if (!receivedAt) {
      notify.error("Informe a data de recebimento");
      return;
    }

    if (
      !/^\d{4}-\d{2}-\d{2}$/.test(receivedAt) ||
      Number.isNaN(receivedDate.getTime())
    ) {
      notify.error("Data inválida");
      return;
    }

    if (!Number.isFinite(amount) || amount <= 0) {
      notify.error("Informe um valor válido");
      return;
    }
    if (!Number.isFinite(bankAccountId) || bankAccountId <= 0) {
      notify.error("Selecione a conta de recebimento");
      return;
    }

    const payload = {
      income_type: form.incomeType,
      ticker,
      bank_account_id: bankAccountId,
      received_at: receivedAt,
      amount,
    };

    setSaving(true);
    try {
      if (editingId) {
        const updated = await investmentIncomesService.update(
          editingId,
          payload,
        );
        setItems((prev) =>
          prev.map((item) => (item.id === editingId ? updated : item)),
        );
        notify.success("Lançamento atualizado");
      } else {
        const created = await investmentIncomesService.create(payload);
        setItems((prev) => [...prev, created]);
        notify.success("Lançamento cadastrado");
      }
      resetForm();
    } catch (err) {
      notify.error(getErrorMessage(err, "Erro ao salvar lançamento"));
    } finally {
      setSaving(false);
    }
  }

  function handleRemove(id) {
    confirm({
      message: "Deseja remover este lançamento?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        setRemovingId(id);
        try {
          const target = items.find((item) => item.id === id);
          if (!target) {
            notify.error("Lançamento não encontrado");
            return;
          }
          await investmentIncomesService.remove(id);
          setItems((prev) => prev.filter((item) => item.id !== id));
          if (editingId === id) resetForm();
          notify.success("Lançamento removido");
        } catch (err) {
          notify.error(getErrorMessage(err, "Erro ao remover lançamento"));
        } finally {
          setRemovingId(null);
        }
      },
    });
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6 gap-3">
        <h1 className="text-3xl font-bold">Proventos e Dividendos</h1>
        <Link
          to="/finances/investments"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Investimentos
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Registre os dividendos recebidos e escolha a conta para crédito.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Total Recebido</h2>
          <p className="text-2xl font-bold">{formatCurrency(totalAmount)}</p>
        </div>
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Lançamentos</h2>
          <p className="text-2xl font-bold">{items.length}</p>
        </div>
        <Link
          to="/finances/investments/incomes/dashboards"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition block"
        >
          <h2 className="font-semibold mb-1">Dashboards</h2>
          <p className="text-2xl font-bold">Abrir</p>
          <p className="themed-muted text-sm mt-1">
            Visualize os painéis de proventos
          </p>
        </Link>
      </div>

      <form
        onSubmit={handleSubmit}
        className="themed-card themed-border border rounded-xl p-5 mb-6"
      >
        <h2 className="font-semibold mb-4">
          {editingId ? "Editar lançamento" : "Novo lançamento"}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          <label className="flex flex-col text-sm">
            <span className="mb-1 themed-muted">Tipo</span>
            <select
              value={form.incomeType}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, incomeType: e.target.value }))
              }
              className="themed-input themed-border border rounded px-3 py-2"
            >
              {INCOME_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col text-sm">
            <span className="mb-1 themed-muted">Ticker</span>
            <select
              value={form.ticker}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, ticker: e.target.value }))
              }
              disabled={availableTickers.length === 0}
              className="themed-input themed-border border rounded px-3 py-2"
            >
              <option value="">
                {availableTickers.length === 0
                  ? "Cadastre investimentos primeiro"
                  : "Selecione um ticker"}
              </option>
              {tickerOptions.map((ticker) => (
                <option key={ticker} value={ticker}>
                  {ticker}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col text-sm">
            <span className="mb-1 themed-muted">Conta de recebimento</span>
            <select
              value={form.accountId}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, accountId: e.target.value }))
              }
              disabled={accountOptions.length === 0}
              className="themed-input themed-border border rounded px-3 py-2"
            >
              <option value="">
                {accountOptions.length === 0
                  ? "Cadastre uma conta primeiro"
                  : "Selecione a conta"}
              </option>
              {accountOptions.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col text-sm">
            <span className="mb-1 themed-muted">Data de recebimento</span>
            <input
              type="date"
              value={form.receivedAt}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, receivedAt: e.target.value }))
              }
              className="themed-input themed-border border rounded px-3 py-2"
            />
          </label>

          <label className="flex flex-col text-sm">
            <span className="mb-1 themed-muted">Valor</span>
            <input
              type="text"
              inputMode="decimal"
              value={form.amount}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, amount: e.target.value }))
              }
              placeholder="150,25"
              className="themed-input themed-border border rounded px-3 py-2"
            />
          </label>
        </div>

        <div className="flex items-center gap-2 mt-4">
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white px-4 py-2 rounded"
          >
            {saving ? "Salvando..." : editingId ? "Atualizar" : "Adicionar"}
          </button>
          {editingId ? (
            <button
              type="button"
              onClick={resetForm}
              className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
            >
              Cancelar edição
            </button>
          ) : null}
        </div>
      </form>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="font-semibold mb-3">Histórico de recebimentos</h2>
        {loading ? (
          <p className="themed-muted text-sm">Carregando...</p>
        ) : sortedItems.length === 0 ? (
          <p className="themed-muted text-sm">
            Nenhum lançamento cadastrado ainda.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-sm">
              <thead>
                <tr className="text-left border-b themed-border">
                  <th className="py-2 pr-3">Data</th>
                  <th className="py-2 pr-3">Tipo</th>
                  <th className="py-2 pr-3">Ticker</th>
                  <th className="py-2 pr-3">Conta</th>
                  <th className="py-2 pr-3">Valor</th>
                  <th className="py-2 text-right">Ações</th>
                </tr>
              </thead>
              <tbody>
                {sortedItems.map((item) => (
                  <tr
                    key={item.id}
                    className={`border-b themed-border last:border-b-0 ${
                      editingId === item.id
                        ? "bg-blue-50 dark:bg-blue-900/20"
                        : ""
                    }`}
                  >
                    <td className="py-2 pr-3">
                      {new Date(
                        `${item.received_at}T00:00:00`,
                      ).toLocaleDateString("pt-BR")}
                    </td>
                    <td className="py-2 pr-3">
                      {getIncomeTypeLabel(item.income_type)}
                    </td>
                    <td className="py-2 pr-3 font-medium">{item.ticker}</td>
                    <td className="py-2 pr-3">
                      {item.bank_account_name ||
                        accountNameById.get(String(item.bank_account_id)) ||
                        "-"}
                    </td>
                    <td className="py-2 pr-3">{formatCurrency(item.amount)}</td>
                    <td className="py-2 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => startEditing(item)}
                          className="themed-card themed-border border px-2.5 py-1 rounded hover:opacity-90"
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          onClick={() => handleRemove(item.id)}
                          disabled={removingId === item.id}
                          className="bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white px-2.5 py-1 rounded"
                        >
                          {removingId === item.id ? "Removendo..." : "Excluir"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

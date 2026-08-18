import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import DataTable from "../components/DataTable";
import bankAccountsService from "../services/bankAccountsService";
import dreamsService from "../services/dreamsService";
import { confirm, notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

function formatCurrencyInput(value) {
  const digits = String(value || "").replace(/\D/g, "");
  if (!digits) return "";

  const numberValue = Number(digits) / 100;
  return numberValue.toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function parseCurrencyInput(value) {
  const digits = String(value || "").replace(/\D/g, "");
  if (!digits) return 0;
  return Number(digits) / 100;
}

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function getInitialAccountForm() {
  return {
    name: "",
    objectiveDreamId: "",
    totalValue: "",
    allowInvestmentIncome: false,
  };
}

export default function BankAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [dreams, setDreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingAccount, setSavingAccount] = useState(false);
  const [updatingValueId, setUpdatingValueId] = useState(null);
  const [updatingValueInput, setUpdatingValueInput] = useState("");
  const [savingValueId, setSavingValueId] = useState(null);
  const [accountForm, setAccountForm] = useState(getInitialAccountForm);
  const [filters, setFilters] = useState({
    name: "",
    objectiveDreamId: "",
    totalValue: "",
  });

  useEffect(() => {
    async function loadData() {
      try {
        const [accountsData, dreamsData] = await Promise.all([
          bankAccountsService.list(),
          dreamsService.list(),
        ]);
        setAccounts(Array.isArray(accountsData) ? accountsData : []);
        setDreams(Array.isArray(dreamsData) ? dreamsData : []);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar contas"));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const totalBalance = useMemo(
    () =>
      accounts.reduce(
        (acc, account) => acc + Number(account.total_value || 0),
        0,
      ),
    [accounts],
  );

  const filteredAccounts = useMemo(() => {
    const normalizedName = filters.name.trim().toLowerCase();
    const objectiveDreamId = Number(filters.objectiveDreamId);
    const minValue = parseCurrencyInput(filters.totalValue);

    return accounts.filter((account) => {
      const matchesName = normalizedName
        ? String(account.name || "")
            .toLowerCase()
            .includes(normalizedName)
        : true;
      const matchesObjective = objectiveDreamId
        ? account.objective_dream_id === objectiveDreamId
        : true;
      const matchesValue =
        Number.isFinite(minValue) && filters.totalValue !== ""
          ? Number(account.total_value || 0) >= minValue
          : true;

      return matchesName && matchesObjective && matchesValue;
    });
  }, [accounts, filters]);

  function resetAccountForm() {
    setAccountForm(getInitialAccountForm());
  }

  async function handleCreateAccount(e) {
    e.preventDefault();

    const name = String(accountForm.name || "").trim();
    const objectiveDreamId = Number(accountForm.objectiveDreamId);
    const totalValue = parseCurrencyInput(accountForm.totalValue);

    if (!name) {
      notify.error("Informe o nome da conta");
      return;
    }

    if (!objectiveDreamId) {
      notify.error("Selecione um objetivo");
      return;
    }

    if (!Number.isFinite(totalValue) || totalValue < 0) {
      notify.error("Informe um valor total válido");
      return;
    }

    setSavingAccount(true);
    try {
      const created = await bankAccountsService.create({
        name,
        objective_dream_id: objectiveDreamId,
        total_value: totalValue,
        allow_investment_income: Boolean(accountForm.allowInvestmentIncome),
      });
      setAccounts((prev) => [created, ...prev]);
      notify.success("Conta criada");
      resetAccountForm();
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao criar conta"));
    } finally {
      setSavingAccount(false);
    }
  }

  function handleRemove(accountId) {
    confirm({
      message: "Deseja remover esta conta bancária?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        try {
          await bankAccountsService.remove(accountId);
          setAccounts((prev) => prev.filter((item) => item.id !== accountId));
          notify.success("Conta removida");
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover conta"));
        }
      },
    });
  }

  function startUpdateValue(account) {
    setUpdatingValueId(account.id);
    setUpdatingValueInput(
      formatCurrencyInput(String(account.total_value || "")),
    );
  }

  function cancelUpdateValue() {
    setUpdatingValueId(null);
    setUpdatingValueInput("");
  }

  async function handleUpdateValue(accountId) {
    const totalValue = parseCurrencyInput(updatingValueInput);

    if (!Number.isFinite(totalValue) || totalValue < 0) {
      notify.error("Informe um valor total válido");
      return;
    }

    setSavingValueId(accountId);
    try {
      const updated = await bankAccountsService.update(accountId, {
        total_value: totalValue,
      });
      setAccounts((prev) =>
        prev.map((item) => (item.id === accountId ? updated : item)),
      );
      notify.success("Valor atualizado");
      cancelUpdateValue();
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao atualizar valor"));
    } finally {
      setSavingValueId(null);
    }
  }

  async function handleToggleInvestmentIncome(account) {
    try {
      const updated = await bankAccountsService.update(account.id, {
        allow_investment_income: !account.allow_investment_income,
      });
      setAccounts((prev) =>
        prev.map((item) => (item.id === account.id ? updated : item)),
      );
      notify.success("Configuração de proventos atualizada");
    } catch (err) {
      notify.error(
        getApiErrorMessage(err, "Erro ao atualizar configuração de proventos"),
      );
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Contas Bancárias</h1>
        <Link
          to="/finances/patrimony"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Patrimônio
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Cadastre e gerencie as contas usadas no cálculo do patrimônio.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Contas Cadastradas</h2>
          <p className="text-2xl font-bold">{accounts.length}</p>
          <p className="themed-muted text-sm mt-1">Quantidade de contas</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Saldo Total</h2>
          <p className="text-2xl font-bold">{formatCurrency(totalBalance)}</p>
          <p className="themed-muted text-sm mt-1">Total consolidado</p>
        </div>

        <Link
          to="/dreams"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition block"
        >
          <h2 className="font-semibold mb-1">Objetivos Disponíveis</h2>
          <p className="text-2xl font-bold">{dreams.length}</p>
          <p className="themed-muted text-sm mt-1">Sonhos para vincular</p>
        </Link>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="text-xl font-semibold mb-4">Nova Conta Bancária</h2>

        <form
          onSubmit={handleCreateAccount}
          className="grid grid-cols-1 md:grid-cols-5 gap-3"
        >
          <input
            type="text"
            className="themed-input rounded px-3 py-2"
            placeholder="Nome da conta"
            autoComplete="off"
            value={accountForm.name}
            onChange={(e) =>
              setAccountForm((prev) => ({ ...prev, name: e.target.value }))
            }
          />

          <div className="flex flex-col gap-1">
            <select
              className="themed-input rounded px-3 py-2"
              value={accountForm.objectiveDreamId}
              onChange={(e) =>
                setAccountForm((prev) => ({
                  ...prev,
                  objectiveDreamId: e.target.value,
                }))
              }
            >
              <option value="">Selecione um objetivo</option>
              {dreams.map((dream) => (
                <option key={dream.id} value={dream.id}>
                  {dream.title}
                </option>
              ))}
            </select>
            <Link
              to="/dreams"
              className="text-sm font-medium text-blue-500 hover:underline"
            >
              + adicionar objetivo
            </Link>
          </div>

          <input
            type="text"
            inputMode="decimal"
            className="themed-input rounded px-3 py-2"
            placeholder="Valor total"
            value={accountForm.totalValue}
            onChange={(e) =>
              setAccountForm((prev) => ({
                ...prev,
                totalValue: formatCurrencyInput(e.target.value),
              }))
            }
          />

          <label className="themed-input rounded px-3 py-2 flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={Boolean(accountForm.allowInvestmentIncome)}
              onChange={(e) =>
                setAccountForm((prev) => ({
                  ...prev,
                  allowInvestmentIncome: e.target.checked,
                }))
              }
            />
            Habilitar para proventos
          </label>

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={savingAccount}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {savingAccount ? "Salvando..." : "Cadastrar"}
            </button>
            <button
              type="button"
              onClick={resetAccountForm}
              className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
            >
              Limpar
            </button>
          </div>
        </form>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5 mt-6">
        <h2 className="text-xl font-semibold mb-4">Filtrar Contas Bancárias</h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            type="text"
            className="themed-input rounded px-3 py-2"
            placeholder="Banco XYZ"
            autoComplete="off"
            name="bank-account-name-filter"
            value={filters.name}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, name: e.target.value }))
            }
          />

          <select
            className="themed-input rounded px-3 py-2"
            value={filters.objectiveDreamId}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                objectiveDreamId: e.target.value,
              }))
            }
          >
            <option value="">Todos os objetivos</option>
            {dreams.map((dream) => (
              <option key={dream.id} value={dream.id}>
                {dream.title}
              </option>
            ))}
          </select>

          <input
            type="text"
            inputMode="decimal"
            className="themed-input rounded px-3 py-2"
            placeholder="Valor mínimo"
            value={filters.totalValue}
            onChange={(e) =>
              setFilters((prev) => ({
                ...prev,
                totalValue: formatCurrencyInput(e.target.value),
              }))
            }
          />

          <div className="flex gap-2">
            <button
              type="button"
              onClick={() =>
                setFilters({
                  name: "",
                  objectiveDreamId: "",
                  totalValue: "",
                })
              }
              className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
            >
              Limpar filtros
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6">
        {loading ? (
          <p className="themed-muted">Carregando contas...</p>
        ) : (
          <DataTable
            title="Contas Cadastradas"
            columns={[
              { key: "name", label: "Conta" },
              { key: "objective", label: "Objetivo" },
              { key: "total_value", label: "Valor Total" },
              { key: "investment_income", label: "Proventos" },
              { key: "actions", label: "Ações", width: 360 },
            ]}
            data={filteredAccounts}
            renderRow={(account) => {
              const isUpdatingValue = updatingValueId === account.id;
              const isSavingValue = savingValueId === account.id;

              return (
                <tr key={account.id} className="border themed-border">
                  <td className="p-2 border themed-border font-medium">
                    {account.name}
                  </td>
                  <td className="p-2 border themed-border">
                    {account.objective_dream_title || "—"}
                  </td>
                  <td className="p-2 border themed-border">
                    {isUpdatingValue ? (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          handleUpdateValue(account.id);
                        }}
                        className="flex min-w-[260px] items-center gap-2"
                      >
                        <input
                          type="text"
                          inputMode="decimal"
                          className="themed-input rounded px-3 py-2 w-full"
                          placeholder="Novo valor"
                          value={updatingValueInput}
                          onChange={(e) =>
                            setUpdatingValueInput(
                              formatCurrencyInput(e.target.value),
                            )
                          }
                        />
                        <button
                          type="submit"
                          disabled={isSavingValue}
                          className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                        >
                          {isSavingValue ? "Salvando..." : "Salvar"}
                        </button>
                      </form>
                    ) : (
                      formatCurrency(account.total_value)
                    )}
                  </td>
                  <td className="p-2 border themed-border">
                    {account.allow_investment_income
                      ? "Habilitado"
                      : "Desabilitado"}
                  </td>
                  <td className="p-2 border themed-border">
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => handleToggleInvestmentIncome(account)}
                        className="px-2 py-1 bg-slate-600 text-white rounded hover:opacity-90"
                      >
                        {account.allow_investment_income
                          ? "Desabilitar proventos"
                          : "Habilitar proventos"}
                      </button>
                      <button
                        type="button"
                        disabled={isSavingValue}
                        onClick={() =>
                          isUpdatingValue
                            ? cancelUpdateValue()
                            : startUpdateValue(account)
                        }
                        className="px-2 py-1 bg-blue-500 text-white rounded disabled:opacity-50"
                      >
                        {isUpdatingValue ? "Cancelar" : "Atualizar Valor"}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleRemove(account.id)}
                        className="px-2 py-1 bg-red-500 text-white rounded"
                      >
                        Remover
                      </button>
                    </div>
                  </td>
                </tr>
              );
            }}
          />
        )}
      </div>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import { ArrowLeftRight } from "lucide-react";
import { Link } from "react-router-dom";
import { getApiErrorMessage } from "../core/apiError";
import { notify } from "../core/toast";
import bankAccountsService from "../services/bankAccountsService";

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function getInitialForm() {
  return {
    fromAccountId: "",
    toAccountId: "",
    amount: "",
  };
}

export default function BankAccountTransfers() {
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState(getInitialForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAccounts() {
      try {
        const data = await bankAccountsService.list();
        const list = Array.isArray(data) ? data : [];
        setAccounts(list);
        if (list.length >= 2) {
          setForm({
            fromAccountId: String(list[0].id),
            toAccountId: String(list[1].id),
            amount: "",
          });
        }
      } catch (err) {
        notify.error(
          getApiErrorMessage(err, "Erro ao carregar contas para transferência"),
        );
      } finally {
        setLoading(false);
      }
    }

    loadAccounts();
  }, []);

  const fromAccount = useMemo(
    () =>
      accounts.find(
        (account) => String(account.id) === String(form.fromAccountId),
      ) || null,
    [accounts, form.fromAccountId],
  );

  const destinationOptions = useMemo(
    () =>
      accounts.filter(
        (account) => String(account.id) !== String(form.fromAccountId),
      ),
    [accounts, form.fromAccountId],
  );

  const totalBalance = useMemo(
    () =>
      accounts.reduce(
        (acc, account) => acc + Number(account.total_value || 0),
        0,
      ),
    [accounts],
  );

  async function handleSubmit(event) {
    event.preventDefault();

    const amount = Number(form.amount);
    if (!form.fromAccountId) {
      notify.error("Selecione a conta de origem");
      return;
    }
    if (!form.toAccountId) {
      notify.error("Selecione a conta de destino");
      return;
    }
    if (form.fromAccountId === form.toAccountId) {
      notify.error("Selecione contas diferentes");
      return;
    }
    if (!Number.isFinite(amount) || amount <= 0) {
      notify.error("Informe um valor de transferência válido");
      return;
    }
    if (fromAccount && amount > Number(fromAccount.total_value || 0)) {
      notify.error("O valor excede o saldo disponível na conta de origem");
      return;
    }

    setSaving(true);
    try {
      const result = await bankAccountsService.transfer({
        from_account_id: Number(form.fromAccountId),
        to_account_id: Number(form.toAccountId),
        amount,
      });

      setAccounts((prev) =>
        prev.map((account) => {
          if (account.id === result.from_account.id) return result.from_account;
          if (account.id === result.to_account.id) return result.to_account;
          return account;
        }),
      );
      setForm((prev) => ({
        ...prev,
        amount: "",
      }));
      notify.success(
        `Transferência concluída: ${formatCurrency(result.transferred_amount)}.`,
      );
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao transferir valores"));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Transferência entre Contas</h1>
        <Link
          to="/finances"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Finanças
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Mova saldo entre suas contas bancárias sem alterar o patrimônio total.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Contas Disponíveis</h2>
          <p className="text-2xl font-bold">{accounts.length}</p>
          <p className="themed-muted text-sm mt-1">
            Contas aptas para origem ou destino.
          </p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Saldo Total</h2>
          <p className="text-2xl font-bold">{formatCurrency(totalBalance)}</p>
          <p className="themed-muted text-sm mt-1">
            Total consolidado entre todas as contas.
          </p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Regra da Transferência</h2>
          <p className="text-base font-semibold">
            Mesmo patrimônio, novo saldo
          </p>
          <p className="themed-muted text-sm mt-1">
            O valor sai de uma conta e entra em outra.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] gap-6">
        <form
          onSubmit={handleSubmit}
          className="themed-card themed-border border rounded-xl p-5"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full themed-border border flex items-center justify-center">
              <ArrowLeftRight size={18} />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Nova Transferência</h2>
              <p className="themed-muted text-sm">
                Escolha a origem, o destino e o valor.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="block">
              <span className="text-sm font-medium">Conta de origem</span>
              <select
                className="themed-input rounded px-3 py-2 w-full mt-1"
                value={form.fromAccountId}
                onChange={(event) => {
                  const nextFromAccountId = event.target.value;
                  const nextDestinationExists = accounts.some(
                    (account) =>
                      String(account.id) === String(form.toAccountId) &&
                      String(account.id) !== nextFromAccountId,
                  );

                  setForm((prev) => ({
                    ...prev,
                    fromAccountId: nextFromAccountId,
                    toAccountId: nextDestinationExists
                      ? prev.toAccountId
                      : String(
                          accounts.find(
                            (account) =>
                              String(account.id) !== nextFromAccountId,
                          )?.id || "",
                        ),
                  }));
                }}
                disabled={loading || accounts.length < 2 || saving}
              >
                <option value="">Selecione a conta de origem</option>
                {accounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name} ({formatCurrency(account.total_value)})
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="text-sm font-medium">Conta de destino</span>
              <select
                className="themed-input rounded px-3 py-2 w-full mt-1"
                value={form.toAccountId}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    toAccountId: event.target.value,
                  }))
                }
                disabled={loading || accounts.length < 2 || saving}
              >
                <option value="">Selecione a conta de destino</option>
                {destinationOptions.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.name} ({formatCurrency(account.total_value)})
                  </option>
                ))}
              </select>
            </label>

            <label className="block md:col-span-2">
              <span className="text-sm font-medium">
                Valor da transferência
              </span>
              <input
                type="number"
                min="0.01"
                step="0.01"
                inputMode="decimal"
                className="themed-input rounded px-3 py-2 w-full mt-1"
                placeholder="0,00"
                value={form.amount}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    amount: event.target.value,
                  }))
                }
                disabled={loading || accounts.length < 2 || saving}
              />
            </label>
          </div>

          <div className="mt-6 flex items-center justify-between gap-3">
            <p className="themed-muted text-sm">
              {fromAccount
                ? `Saldo disponível: ${formatCurrency(fromAccount.total_value)}`
                : "Selecione a conta de origem para ver o saldo."}
            </p>
            <button
              type="submit"
              className="bg-emerald-600 hover:bg-emerald-700 text-white rounded px-4 py-2 transition disabled:opacity-60"
              disabled={loading || accounts.length < 2 || saving}
            >
              {saving ? "Transferindo..." : "Transferir valor"}
            </button>
          </div>
        </form>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="text-xl font-semibold mb-4">Saldos Atuais</h2>

          {accounts.length === 0 ? (
            <p className="themed-muted text-sm">
              Nenhuma conta encontrada. Cadastre contas em patrimônio para usar
              esta funcionalidade.
            </p>
          ) : accounts.length === 1 ? (
            <p className="themed-muted text-sm">
              É preciso ter pelo menos duas contas para realizar uma
              transferência.
            </p>
          ) : (
            <div className="space-y-3">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  className="themed-subtle rounded-lg px-4 py-3 flex items-center justify-between gap-4"
                >
                  <div>
                    <p className="font-medium">{account.name}</p>
                    <p className="themed-muted text-sm">
                      Objetivo: {account.objective_dream_title}
                    </p>
                  </div>
                  <p className="font-semibold">
                    {formatCurrency(account.total_value)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

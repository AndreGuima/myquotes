import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import bankAccountsService from "../services/bankAccountsService";
import dreamsService from "../services/dreamsService";
import { confirm, notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const PATRIMONY_SHOW_VALUES_KEY = "patrimony_show_values";

export default function Patrimony() {
  const [accounts, setAccounts] = useState([]);
  const [dreams, setDreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [showValues, setShowValues] = useState(() => {
    const stored = localStorage.getItem(PATRIMONY_SHOW_VALUES_KEY);
    if (stored === null) return true;
    return stored === "true";
  });

  const [form, setForm] = useState({
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
        notify.error(getApiErrorMessage(err, "Erro ao carregar patrimônio"));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  useEffect(() => {
    localStorage.setItem(PATRIMONY_SHOW_VALUES_KEY, String(showValues));
  }, [showValues]);

  const totalPatrimony = useMemo(
    () =>
      accounts.reduce(
        (acc, account) => acc + Number(account.total_value || 0),
        0,
      ),
    [accounts],
  );

  const formattedTotal = useMemo(
    () =>
      totalPatrimony.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
      }),
    [totalPatrimony],
  );

  const maskedMoney = "R$ •••••";

  function resetForm() {
    setEditingId(null);
    setForm({
      name: "",
      objectiveDreamId: "",
      totalValue: "",
    });
  }

  function startEdit(account) {
    setEditingId(account.id);
    setForm({
      name: account.name || "",
      objectiveDreamId: String(account.objective_dream_id || ""),
      totalValue: String(account.total_value || ""),
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();

    const cleanName = form.name.trim();
    const objectiveDreamId = Number(form.objectiveDreamId);
    const totalValue = Number(form.totalValue);

    if (!cleanName) {
      notify.error("Informe o nome da conta");
      return;
    }

    if (!objectiveDreamId) {
      notify.error("Selecione o objetivo");
      return;
    }

    if (!Number.isFinite(totalValue) || totalValue < 0) {
      notify.error("Informe um valor total válido");
      return;
    }

    const payload = {
      name: cleanName,
      objective_dream_id: objectiveDreamId,
      total_value: totalValue,
    };

    setSaving(true);
    try {
      if (editingId) {
        const updated = await bankAccountsService.update(editingId, payload);
        setAccounts((prev) =>
          prev.map((item) => (item.id === editingId ? updated : item)),
        );
        notify.success("Conta atualizada");
      } else {
        const created = await bankAccountsService.create(payload);
        setAccounts((prev) => [created, ...prev]);
        notify.success("Conta criada");
      }

      resetForm();
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar conta"));
    } finally {
      setSaving(false);
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
          if (editingId === accountId) {
            resetForm();
          }
          notify.success("Conta removida");
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover conta"));
        }
      },
    });
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Patrimônio</h1>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowValues((prev) => !prev)}
            className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition inline-flex items-center gap-2"
            aria-label={showValues ? "Ocultar valores" : "Mostrar valores"}
            title={showValues ? "Ocultar valores" : "Mostrar valores"}
          >
            {showValues ? <EyeOff size={18} /> : <Eye size={18} />}
            <span className="hidden sm:inline">
              {showValues ? "Ocultar valores" : "Mostrar valores"}
            </span>
          </button>
          <Link
            to="/finances"
            className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
          >
            Voltar para Finanças
          </Link>
        </div>
      </div>

      <p className="themed-muted mb-6">
        Acompanhe seus ativos, passivos e evolução patrimonial.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Total em Contas</h2>
          <p className="text-2xl font-bold">
            {showValues ? formattedTotal : maskedMoney}
          </p>
          <p className="themed-muted text-sm mt-1">Soma do valor total</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Contas Cadastradas</h2>
          <p className="text-2xl font-bold">{accounts.length}</p>
          <p className="themed-muted text-sm mt-1">Quantidade de contas</p>
        </div>

        <div className="themed-card themed-border border rounded-xl p-5">
          <h2 className="font-semibold mb-1">Objetivos Disponíveis</h2>
          <p className="text-2xl font-bold">{dreams.length}</p>
          <p className="themed-muted text-sm mt-1">Sonhos para vincular</p>
        </div>

        <Link
          to="/finances/patrimony/dashboards"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition block"
        >
          <h2 className="font-semibold mb-1">Dashboards</h2>
          <p className="text-2xl font-bold">Abrir</p>
          <p className="themed-muted text-sm mt-1">
            Visualize os painéis do patrimônio.
          </p>
        </Link>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5 mt-6">
        <h2 className="text-xl font-semibold mb-4">
          {editingId ? "Editar Conta Bancária" : "Nova Conta Bancária"}
        </h2>

        {dreams.length === 0 && (
          <p className="themed-muted mb-4">
            Você precisa cadastrar ao menos um sonho no módulo de sonhos para
            usar o campo objetivo.{" "}
            <Link to="/dreams" className="themed-link underline">
              Ir para Sonhos
            </Link>
          </p>
        )}

        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 md:grid-cols-4 gap-3"
        >
          <input
            type="text"
            className="themed-input rounded px-3 py-2"
            placeholder="Nome da conta"
            value={form.name}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, name: e.target.value }))
            }
          />

          <select
            className="themed-input rounded px-3 py-2"
            value={form.objectiveDreamId}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, objectiveDreamId: e.target.value }))
            }
          >
            <option value="">Selecione o objetivo</option>
            {dreams.map((dream) => (
              <option key={dream.id} value={dream.id}>
                {dream.title}
              </option>
            ))}
          </select>

          <input
            type={showValues ? "number" : "password"}
            step="0.01"
            min="0"
            className="themed-input rounded px-3 py-2"
            placeholder="Valor total"
            value={form.totalValue}
            onChange={(e) =>
              setForm((prev) => ({ ...prev, totalValue: e.target.value }))
            }
          />

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={saving || dreams.length === 0}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Salvando..." : editingId ? "Atualizar" : "Criar"}
            </button>

            {editingId && (
              <button
                type="button"
                onClick={resetForm}
                className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
              >
                Cancelar
              </button>
            )}
          </div>
        </form>
      </div>

      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-4">Contas Bancárias</h2>

        {loading ? (
          <p className="themed-muted">Carregando contas...</p>
        ) : accounts.length === 0 ? (
          <p className="themed-muted">Nenhuma conta bancária cadastrada.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {accounts.map((account) => (
              <div
                key={account.id}
                className="themed-card themed-border border rounded-xl p-4"
              >
                <h3 className="text-lg font-semibold">{account.name}</h3>
                <p className="themed-muted text-sm mt-1">
                  Objetivo: {account.objective_dream_title}
                </p>
                <p className="text-xl font-bold mt-2">
                  {showValues
                    ? Number(account.total_value).toLocaleString("pt-BR", {
                        style: "currency",
                        currency: "BRL",
                      })
                    : maskedMoney}
                </p>

                <div className="flex gap-4 text-sm mt-3">
                  <button
                    type="button"
                    onClick={() => startEdit(account)}
                    className="themed-link hover:underline"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRemove(account.id)}
                    className="text-red-600 hover:underline"
                  >
                    Remover
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

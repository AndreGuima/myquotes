import { useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import creditCardsService from "../services/creditCardsService";
import { confirm, notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

function getInitialForm() {
  return {
    name: "",
  };
}

export default function CreditCards() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState(getInitialForm());

  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState("");
  const [updatingId, setUpdatingId] = useState(null);

  useEffect(() => {
    async function loadCards() {
      try {
        const data = await creditCardsService.list();
        setCards(Array.isArray(data) ? data : []);
      } catch (err) {
        notify.error(
          getApiErrorMessage(err, "Erro ao carregar cartões de crédito"),
        );
      } finally {
        setLoading(false);
      }
    }

    loadCards();
  }, []);

  function resetForm() {
    setForm(getInitialForm());
  }

  async function handleCreate(e) {
    e.preventDefault();

    const name = String(form.name || "").trim();

    if (!name) {
      notify.error("Informe o nome do cartão");
      return;
    }

    setSaving(true);

    try {
      const created = await creditCardsService.create({
        name,
      });

      setCards((prev) => [created, ...prev]);
      notify.success("Cartão criado");
      resetForm();
    } catch (err) {
      notify.error(
        getApiErrorMessage(err, "Erro ao criar cartão de crédito"),
      );
    } finally {
      setSaving(false);
    }
  }

  function startEdit(card) {
    setEditingId(card.id);
    setEditingName(card.name || "");
  }

  function cancelEdit() {
    setEditingId(null);
    setEditingName("");
  }

  async function handleUpdate(cardId) {
    const name = String(editingName || "").trim();

    if (!name) {
      notify.error("Informe o nome do cartão");
      return;
    }

    setUpdatingId(cardId);

    try {
      const updated = await creditCardsService.update(cardId, {
        name,
      });

      setCards((prev) =>
        prev.map((card) => (card.id === cardId ? updated : card)),
      );

      notify.success("Cartão atualizado");
      cancelEdit();
    } catch (err) {
      notify.error(
        getApiErrorMessage(err, "Erro ao atualizar cartão de crédito"),
      );
    } finally {
      setUpdatingId(null);
    }
  }

  function handleRemove(cardId) {
    confirm({
      message: "Deseja remover este cartão de crédito?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        try {
          await creditCardsService.remove(cardId);

          setCards((prev) => prev.filter((card) => card.id !== cardId));

          notify.success("Cartão removido");
        } catch (err) {
          notify.error(
            getApiErrorMessage(err, "Erro ao remover cartão de crédito"),
          );
        }
      },
    });
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Cartões de Crédito</h1>

        <p className="themed-muted mt-2">
          Cadastre e gerencie os cartões de crédito utilizados nas despesas.
        </p>
      </div>

      <div className="themed-card themed-border border rounded-xl p-5">
        <h2 className="text-xl font-semibold mb-4">
          Novo Cartão de Crédito
        </h2>

        <form
          onSubmit={handleCreate}
          className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-3 items-start"
        >
          <input
            type="text"
            className="themed-input rounded px-3 py-2"
            placeholder="Nome do cartão"
            autoComplete="off"
            maxLength={120}
            value={form.name}
            onChange={(e) =>
              setForm((prev) => ({
                ...prev,
                name: e.target.value,
              }))
            }
          />

          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Salvando..." : "Cadastrar"}
          </button>

          <button
            type="button"
            onClick={resetForm}
            className="themed-card themed-border border px-4 py-2 rounded hover:opacity-90"
          >
            Limpar
          </button>
        </form>
      </div>

      <div className="mt-6">
        {loading ? (
          <p className="themed-muted">Carregando cartões...</p>
        ) : (
          <DataTable
            title="Cartões Cadastrados"
            columns={[
              {
                key: "name",
                label: "Cartão",
              },
              {
                key: "created_at",
                label: "Data de Cadastro",
              },
              {
                key: "actions",
                label: "Ações",
                width: 300,
              },
            ]}
            data={cards}
            enableSearch
            searchPlaceholder="Buscar cartão..."
            searchKeys={["name"]}
            renderRow={(card) => {
              const isEditing = editingId === card.id;
              const isUpdating = updatingId === card.id;

              return (
                <tr key={card.id} className="border themed-border">
                  <td className="p-2 border themed-border font-medium">
                    {isEditing ? (
                      <input
                        type="text"
                        className="themed-input rounded px-3 py-2 w-full"
                        maxLength={120}
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === "Escape") {
                            cancelEdit();
                          }

                          if (e.key === "Enter") {
                            e.preventDefault();
                            handleUpdate(card.id);
                          }
                        }}
                      />
                    ) : (
                      card.name
                    )}
                  </td>

                  <td className="p-2 border themed-border">
                    {card.created_at
                      ? new Date(card.created_at).toLocaleDateString("pt-BR")
                      : "—"}
                  </td>

                  <td className="p-2 border themed-border">
                    <div className="flex flex-wrap gap-2">
                      {isEditing ? (
                        <>
                          <button
                            type="button"
                            disabled={isUpdating}
                            onClick={() => handleUpdate(card.id)}
                            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                          >
                            {isUpdating ? "Salvando..." : "Salvar"}
                          </button>

                          <button
                            type="button"
                            disabled={isUpdating}
                            onClick={cancelEdit}
                            className="px-3 py-1 themed-card themed-border border rounded hover:opacity-90 disabled:opacity-50"
                          >
                            Cancelar
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            type="button"
                            onClick={() => startEdit(card)}
                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                          >
                            Editar
                          </button>

                          <button
                            type="button"
                            onClick={() => handleRemove(card.id)}
                            className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                          >
                            Remover
                          </button>
                        </>
                      )}
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
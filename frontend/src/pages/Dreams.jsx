import { useEffect, useMemo, useState } from "react";
import { confirm, notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";
import habitsService from "../services/habitsService";
import dreamsService from "../services/dreamsService";

function newDraft() {
  return {
    title: "",
    description: "",
    smart: {
      specific: "",
      measurable: "",
      achievable: "",
      relevant: "",
      timeBound: "",
      targetDate: "",
    },
    linkedHabitIds: [],
    milestones: [],
  };
}

function draftFromDream(dream) {
  return {
    title: dream.title || "",
    description: dream.description || "",
    smart: {
      specific: dream.smart?.specific || "",
      measurable: dream.smart?.measurable || "",
      achievable: dream.smart?.achievable || "",
      relevant: dream.smart?.relevant || "",
      timeBound: dream.smart?.timeBound || "",
      targetDate: dream.smart?.targetDate || "",
    },
    linkedHabitIds: [...(dream.linkedHabitIds || [])],
    milestones: (dream.milestones || []).map((milestone, index) => ({
      id: milestone.id,
      title: milestone.title,
      targetDate: milestone.targetDate || "",
      completedAt: milestone.completedAt || null,
      position: milestone.position ?? index,
    })),
  };
}

function dreamPayloadFromDraft(draft) {
  return {
    title: draft.title.trim(),
    description: draft.description.trim() || null,
    smart: {
      specific: draft.smart.specific || null,
      measurable: draft.smart.measurable || null,
      achievable: draft.smart.achievable || null,
      relevant: draft.smart.relevant || null,
      timeBound: draft.smart.timeBound || null,
      targetDate: draft.smart.targetDate || null,
    },
    linkedHabitIds: draft.linkedHabitIds,
    milestones: draft.milestones.map((milestone) => ({
      id: typeof milestone.id === "number" ? milestone.id : undefined,
      title: milestone.title,
      targetDate: milestone.targetDate || null,
      completedAt: milestone.completedAt || null,
    })),
  };
}

function toDateLabel(date) {
  if (!date) return "Sem data";
  return new Date(`${date}T00:00:00`).toLocaleDateString("pt-BR");
}

function sortByDate(items) {
  return [...items].sort((a, b) => {
    if (!a.targetDate && !b.targetDate) return 0;
    if (!a.targetDate) return 1;
    if (!b.targetDate) return -1;
    return a.targetDate.localeCompare(b.targetDate);
  });
}

function computeSmartScore(dream) {
  const fields = [
    dream.smart?.specific,
    dream.smart?.measurable,
    dream.smart?.achievable,
    dream.smart?.relevant,
    dream.smart?.timeBound,
  ];

  const done = fields.filter((item) => String(item || "").trim().length > 0);
  return Math.round((done.length / fields.length) * 100);
}

function computeMilestoneProgress(dream) {
  const total = dream.milestones?.length ?? 0;
  if (!total) return 0;
  const completed = dream.milestones.filter((m) =>
    Boolean(m.completedAt),
  ).length;
  return Math.round((completed / total) * 100);
}

function computeXp(dream, habitsById) {
  const completedMilestones =
    dream.milestones?.filter((m) => Boolean(m.completedAt)).length ?? 0;
  const smartScore = computeSmartScore(dream);

  const linkedHabits = dream.linkedHabitIds
    .map((id) => habitsById.get(id))
    .filter(Boolean);

  const todayDone = linkedHabits.filter((h) => h.stats?.today_completed).length;
  const streakBonus = linkedHabits.reduce(
    (acc, h) => acc + Math.min(h.stats?.current_streak ?? 0, 30),
    0,
  );

  return (
    completedMilestones * 120 + smartScore * 2 + todayDone * 25 + streakBonus
  );
}

function updateDraftState(setDraftState, path, value) {
  if (path.startsWith("smart.")) {
    const key = path.replace("smart.", "");
    setDraftState((prev) => ({
      ...prev,
      smart: {
        ...prev.smart,
        [key]: value,
      },
    }));
    return;
  }

  setDraftState((prev) => ({ ...prev, [path]: value }));
}

function toggleLinkedHabit(setDraftState, habitId) {
  setDraftState((prev) => {
    const alreadyLinked = prev.linkedHabitIds.includes(habitId);
    return {
      ...prev,
      linkedHabitIds: alreadyLinked
        ? prev.linkedHabitIds.filter((id) => id !== habitId)
        : [...prev.linkedHabitIds, habitId],
    };
  });
}

function addMilestone(setDraftState, title, targetDate, setTitle, setDate) {
  const cleanTitle = title.trim();
  if (!cleanTitle) {
    notify.error("Informe o nome do marco");
    return;
  }

  setDraftState((prev) => ({
    ...prev,
    milestones: [
      ...prev.milestones,
      {
        id: `draft-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        title: cleanTitle,
        targetDate: targetDate || "",
        completedAt: null,
        position: prev.milestones.length,
      },
    ],
  }));
  setTitle("");
  setDate("");
}

function removeMilestone(setDraftState, milestoneId) {
  setDraftState((prev) => ({
    ...prev,
    milestones: prev.milestones.filter((m) => m.id !== milestoneId),
  }));
}

export default function Dreams() {
  const [dreams, setDreams] = useState([]);
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingDream, setSavingDream] = useState(false);
  const [savingEdit, setSavingEdit] = useState(false);

  const [draft, setDraft] = useState(newDraft);
  const [milestoneTitle, setMilestoneTitle] = useState("");
  const [milestoneDate, setMilestoneDate] = useState("");

  const [editingDreamId, setEditingDreamId] = useState(null);
  const [editDraft, setEditDraft] = useState(newDraft);
  const [editMilestoneTitle, setEditMilestoneTitle] = useState("");
  const [editMilestoneDate, setEditMilestoneDate] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const [dreamsData, habitsData] = await Promise.all([
          dreamsService.list(),
          habitsService.list({ include_stats: true }),
        ]);
        setDreams(dreamsData);
        setHabits(habitsData);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar sonhos"));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const habitsById = useMemo(
    () => new Map(habits.map((habit) => [habit.id, habit])),
    [habits],
  );

  async function handleCreateDream(e) {
    e.preventDefault();

    if (!draft.title.trim()) {
      notify.error("Informe o nome do sonho");
      return;
    }

    setSavingDream(true);

    try {
      const createdDream = await dreamsService.create(
        dreamPayloadFromDraft(draft),
      );
      setDreams((prev) => [createdDream, ...prev]);
      setDraft(newDraft());
      setMilestoneTitle("");
      setMilestoneDate("");
      notify.success("Sonho criado com sucesso");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao criar sonho"));
    } finally {
      setSavingDream(false);
    }
  }

  function startEdit(dream) {
    setEditingDreamId(dream.id);
    setEditDraft(draftFromDream(dream));
    setEditMilestoneTitle("");
    setEditMilestoneDate("");
  }

  function cancelEdit() {
    setEditingDreamId(null);
    setEditDraft(newDraft());
    setEditMilestoneTitle("");
    setEditMilestoneDate("");
  }

  async function saveEdit(dreamId) {
    if (!editDraft.title.trim()) {
      notify.error("Informe o nome do sonho");
      return;
    }

    setSavingEdit(true);
    try {
      const updatedDream = await dreamsService.update(
        dreamId,
        dreamPayloadFromDraft(editDraft),
      );

      setDreams((prev) =>
        prev.map((dream) => (dream.id === dreamId ? updatedDream : dream)),
      );
      notify.success("Sonho atualizado");
      cancelEdit();
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao atualizar sonho"));
    } finally {
      setSavingEdit(false);
    }
  }

  function handleDeleteDream(dreamId) {
    confirm({
      message: "Deseja remover este sonho?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        try {
          await dreamsService.remove(dreamId);
          setDreams((prev) => prev.filter((dream) => dream.id !== dreamId));
          if (editingDreamId === dreamId) {
            cancelEdit();
          }
          notify.success("Sonho removido");
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover sonho"));
        }
      },
    });
  }

  async function toggleMilestone(dreamId, milestoneId) {
    try {
      const toggled = await dreamsService.toggleMilestone(dreamId, milestoneId);

      setDreams((prev) =>
        prev.map((dream) => {
          if (dream.id !== dreamId) return dream;
          return {
            ...dream,
            milestones: dream.milestones.map((milestone) => {
              if (milestone.id !== milestoneId) return milestone;
              return {
                ...milestone,
                completedAt: toggled.completedAt,
              };
            }),
          };
        }),
      );
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao atualizar marco"));
    }
  }

  const orderedDreams = useMemo(
    () =>
      [...dreams].sort((a, b) => {
        const aXp = computeXp(a, habitsById);
        const bXp = computeXp(b, habitsById);
        return bXp - aXp;
      }),
    [dreams, habitsById],
  );

  if (loading) {
    return <p className="p-4 themed-muted">Carregando sonhos...</p>;
  }

  return (
    <div className="dreams-page p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Gerenciamento de Sonhos</h1>
        <p className="themed-muted mt-2">
          Estruture seus sonhos no modelo SMART, conecte hábitos e acompanhe
          marcos em timeline.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <form
          onSubmit={handleCreateDream}
          className="xl:col-span-1 themed-card border themed-border rounded-xl p-5 shadow-sm space-y-4 h-fit"
        >
          <h2 className="text-xl font-semibold">Novo sonho</h2>

          <div>
            <label className="block text-sm font-medium mb-1">Nome</label>
            <input
              value={draft.title}
              onChange={(e) =>
                updateDraftState(setDraft, "title", e.target.value)
              }
              placeholder="Ex: Correr minha primeira meia maratona"
              className="w-full border themed-border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Descrição</label>
            <textarea
              value={draft.description}
              onChange={(e) =>
                updateDraftState(setDraft, "description", e.target.value)
              }
              rows={3}
              className="w-full border themed-border rounded px-3 py-2"
            />
          </div>

          <div className="border themed-border rounded-lg p-3 themed-subtle">
            <h3 className="font-medium mb-2">SMART</h3>
            <div className="space-y-2">
              <input
                value={draft.smart.specific}
                onChange={(e) =>
                  updateDraftState(setDraft, "smart.specific", e.target.value)
                }
                className="w-full border themed-border rounded px-3 py-2"
                placeholder="S - Específico"
              />
              <input
                value={draft.smart.measurable}
                onChange={(e) =>
                  updateDraftState(setDraft, "smart.measurable", e.target.value)
                }
                className="w-full border themed-border rounded px-3 py-2"
                placeholder="M - Mensurável"
              />
              <input
                value={draft.smart.achievable}
                onChange={(e) =>
                  updateDraftState(setDraft, "smart.achievable", e.target.value)
                }
                className="w-full border themed-border rounded px-3 py-2"
                placeholder="A - Atingível"
              />
              <input
                value={draft.smart.relevant}
                onChange={(e) =>
                  updateDraftState(setDraft, "smart.relevant", e.target.value)
                }
                className="w-full border themed-border rounded px-3 py-2"
                placeholder="R - Relevante"
              />
              <input
                value={draft.smart.timeBound}
                onChange={(e) =>
                  updateDraftState(setDraft, "smart.timeBound", e.target.value)
                }
                className="w-full border themed-border rounded px-3 py-2"
                placeholder="T - Temporal"
              />
              <div>
                <label className="block text-sm mb-1">Data alvo final</label>
                <input
                  type="date"
                  value={draft.smart.targetDate}
                  onChange={(e) =>
                    updateDraftState(
                      setDraft,
                      "smart.targetDate",
                      e.target.value,
                    )
                  }
                  className="w-full border themed-border rounded px-3 py-2"
                />
              </div>
            </div>
          </div>

          <div className="border themed-border rounded-lg p-3">
            <h3 className="font-medium mb-2">Hábitos vinculados</h3>
            {habits.length === 0 ? (
              <p className="text-sm themed-muted">
                Cadastre hábitos antes de vincular.
              </p>
            ) : (
              <div className="space-y-2 max-h-44 overflow-auto pr-1">
                {habits.map((habit) => (
                  <label
                    key={habit.id}
                    className="flex items-center justify-between gap-2 text-sm"
                  >
                    <span>{habit.title}</span>
                    <input
                      type="checkbox"
                      checked={draft.linkedHabitIds.includes(habit.id)}
                      onChange={() => toggleLinkedHabit(setDraft, habit.id)}
                    />
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="border themed-border rounded-lg p-3">
            <h3 className="font-medium mb-2">Marcos</h3>
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
              <input
                value={milestoneTitle}
                onChange={(e) => setMilestoneTitle(e.target.value)}
                placeholder="Nome do marco"
                className="sm:col-span-3 border themed-border rounded px-3 py-2"
              />
              <input
                type="date"
                value={milestoneDate}
                onChange={(e) => setMilestoneDate(e.target.value)}
                className="sm:col-span-2 border themed-border rounded px-3 py-2"
              />
            </div>

            <button
              type="button"
              onClick={() =>
                addMilestone(
                  setDraft,
                  milestoneTitle,
                  milestoneDate,
                  setMilestoneTitle,
                  setMilestoneDate,
                )
              }
              className="mt-2 text-sm themed-link hover:underline"
            >
              + adicionar marco
            </button>

            {draft.milestones.length > 0 && (
              <div className="mt-3 space-y-2">
                {sortByDate(draft.milestones).map((milestone) => (
                  <div
                    key={milestone.id}
                    className="text-sm border themed-border rounded px-3 py-2 flex justify-between gap-2"
                  >
                    <div>
                      <div className="font-medium">{milestone.title}</div>
                      <div className="themed-muted">
                        {toDateLabel(milestone.targetDate)}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeMilestone(setDraft, milestone.id)}
                      className="text-red-600 hover:underline"
                    >
                      remover
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={savingDream}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-60"
          >
            {savingDream ? "Salvando..." : "Salvar sonho"}
          </button>
        </form>

        <div className="xl:col-span-2 space-y-4">
          {orderedDreams.length === 0 ? (
            <div className="themed-card border themed-border rounded-xl p-6 themed-muted">
              Nenhum sonho cadastrado ainda.
            </div>
          ) : (
            orderedDreams.map((dream) => {
              const smartScore = computeSmartScore(dream);
              const progress = computeMilestoneProgress(dream);
              const xp = computeXp(dream, habitsById);
              const linkedHabits = dream.linkedHabitIds
                .map((id) => habitsById.get(id))
                .filter(Boolean);

              const isEditing = editingDreamId === dream.id;

              return (
                <section
                  key={dream.id}
                  className="themed-card border themed-border rounded-xl p-5"
                >
                  <div className="flex justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-semibold">{dream.title}</h2>
                      {dream.description && (
                        <p className="themed-muted mt-1">{dream.description}</p>
                      )}
                    </div>
                    <div className="flex gap-3 h-fit">
                      {isEditing ? (
                        <button
                          onClick={cancelEdit}
                          className="text-sm themed-muted hover:underline"
                        >
                          cancelar
                        </button>
                      ) : (
                        <button
                          onClick={() => startEdit(dream)}
                          className="text-sm themed-link hover:underline"
                        >
                          editar
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteDream(dream.id)}
                        className="text-sm text-red-600 hover:underline"
                      >
                        remover
                      </button>
                    </div>
                  </div>

                  {isEditing && (
                    <div className="mt-4 border themed-border rounded-lg p-4 themed-subtle space-y-3">
                      <h3 className="font-medium">Editar sonho</h3>

                      <input
                        value={editDraft.title}
                        onChange={(e) =>
                          updateDraftState(
                            setEditDraft,
                            "title",
                            e.target.value,
                          )
                        }
                        className="w-full border themed-border rounded px-3 py-2"
                        placeholder="Nome"
                      />

                      <textarea
                        value={editDraft.description}
                        onChange={(e) =>
                          updateDraftState(
                            setEditDraft,
                            "description",
                            e.target.value,
                          )
                        }
                        rows={3}
                        className="w-full border themed-border rounded px-3 py-2"
                        placeholder="Descrição"
                      />

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <input
                          value={editDraft.smart.specific}
                          onChange={(e) =>
                            updateDraftState(
                              setEditDraft,
                              "smart.specific",
                              e.target.value,
                            )
                          }
                          className="border themed-border rounded px-3 py-2"
                          placeholder="S - Específico"
                        />
                        <input
                          value={editDraft.smart.measurable}
                          onChange={(e) =>
                            updateDraftState(
                              setEditDraft,
                              "smart.measurable",
                              e.target.value,
                            )
                          }
                          className="border themed-border rounded px-3 py-2"
                          placeholder="M - Mensurável"
                        />
                        <input
                          value={editDraft.smart.achievable}
                          onChange={(e) =>
                            updateDraftState(
                              setEditDraft,
                              "smart.achievable",
                              e.target.value,
                            )
                          }
                          className="border themed-border rounded px-3 py-2"
                          placeholder="A - Atingível"
                        />
                        <input
                          value={editDraft.smart.relevant}
                          onChange={(e) =>
                            updateDraftState(
                              setEditDraft,
                              "smart.relevant",
                              e.target.value,
                            )
                          }
                          className="border themed-border rounded px-3 py-2"
                          placeholder="R - Relevante"
                        />
                        <input
                          value={editDraft.smart.timeBound}
                          onChange={(e) =>
                            updateDraftState(
                              setEditDraft,
                              "smart.timeBound",
                              e.target.value,
                            )
                          }
                          className="border themed-border rounded px-3 py-2"
                          placeholder="T - Temporal"
                        />
                        <input
                          type="date"
                          value={editDraft.smart.targetDate}
                          onChange={(e) =>
                            updateDraftState(
                              setEditDraft,
                              "smart.targetDate",
                              e.target.value,
                            )
                          }
                          className="border themed-border rounded px-3 py-2"
                        />
                      </div>

                      <div className="border themed-border rounded themed-card p-3">
                        <div className="font-medium text-sm mb-2">
                          Hábitos vinculados
                        </div>
                        <div className="space-y-2 max-h-40 overflow-auto pr-1">
                          {habits.map((habit) => (
                            <label
                              key={habit.id}
                              className="flex items-center justify-between gap-2 text-sm"
                            >
                              <span>{habit.title}</span>
                              <input
                                type="checkbox"
                                checked={editDraft.linkedHabitIds.includes(
                                  habit.id,
                                )}
                                onChange={() =>
                                  toggleLinkedHabit(setEditDraft, habit.id)
                                }
                              />
                            </label>
                          ))}
                        </div>
                      </div>

                      <div className="border themed-border rounded themed-card p-3">
                        <div className="font-medium text-sm mb-2">Marcos</div>
                        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
                          <input
                            value={editMilestoneTitle}
                            onChange={(e) =>
                              setEditMilestoneTitle(e.target.value)
                            }
                            placeholder="Nome do marco"
                            className="sm:col-span-3 border themed-border rounded px-3 py-2"
                          />
                          <input
                            type="date"
                            value={editMilestoneDate}
                            onChange={(e) =>
                              setEditMilestoneDate(e.target.value)
                            }
                            className="sm:col-span-2 border themed-border rounded px-3 py-2"
                          />
                        </div>
                        <button
                          type="button"
                          onClick={() =>
                            addMilestone(
                              setEditDraft,
                              editMilestoneTitle,
                              editMilestoneDate,
                              setEditMilestoneTitle,
                              setEditMilestoneDate,
                            )
                          }
                          className="mt-2 text-sm themed-link hover:underline"
                        >
                          + adicionar marco
                        </button>

                        {editDraft.milestones.length > 0 && (
                          <div className="mt-3 space-y-2">
                            {sortByDate(editDraft.milestones).map(
                              (milestone) => (
                                <div
                                  key={milestone.id}
                                  className="text-sm border themed-border rounded px-3 py-2 flex justify-between gap-2"
                                >
                                  <div>
                                    <div className="font-medium">
                                      {milestone.title}
                                    </div>
                                    <div className="themed-muted">
                                      {toDateLabel(milestone.targetDate)}
                                    </div>
                                  </div>
                                  <button
                                    type="button"
                                    onClick={() =>
                                      removeMilestone(
                                        setEditDraft,
                                        milestone.id,
                                      )
                                    }
                                    className="text-red-600 hover:underline"
                                  >
                                    remover
                                  </button>
                                </div>
                              ),
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={cancelEdit}
                          className="px-3 py-2 text-sm border themed-border rounded hover:opacity-90 themed-subtle"
                        >
                          Cancelar
                        </button>
                        <button
                          onClick={() => saveEdit(dream.id)}
                          disabled={savingEdit}
                          className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-60"
                        >
                          {savingEdit ? "Salvando..." : "Salvar alterações"}
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
                    <div className="border themed-border rounded-lg p-3 bg-blue-50">
                      <div className="text-xs text-blue-900">SMART</div>
                      <div className="text-2xl font-bold text-blue-900">
                        {smartScore}%
                      </div>
                    </div>
                    <div className="border themed-border rounded-lg p-3 bg-green-50">
                      <div className="text-xs text-green-900">Progresso</div>
                      <div className="text-2xl font-bold text-green-900">
                        {progress}%
                      </div>
                    </div>
                    <div className="border themed-border rounded-lg p-3 bg-amber-50">
                      <div className="text-xs text-amber-900">XP</div>
                      <div className="text-2xl font-bold text-amber-900">
                        {xp}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="h-2 bg-[var(--line-color)] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <h3 className="font-medium mb-2">
                      Hábitos ligados ao sonho
                    </h3>
                    {linkedHabits.length === 0 ? (
                      <p className="text-sm themed-muted">
                        Nenhum hábito vinculado.
                      </p>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {linkedHabits.map((habit) => (
                          <span
                            key={habit.id}
                            className={`text-xs px-2 py-1 rounded-full border ${
                              habit.stats?.today_completed
                                ? "bg-green-50 text-green-700 border-green-200"
                                : "themed-subtle themed-muted themed-border"
                            }`}
                          >
                            {habit.title}
                            {habit.stats?.today_completed
                              ? " · feito hoje"
                              : ""}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="mt-5">
                    <h3 className="font-medium mb-3">Timeline de marcos</h3>
                    {dream.milestones.length === 0 ? (
                      <p className="text-sm themed-muted">
                        Nenhum marco cadastrado.
                      </p>
                    ) : (
                      <div className="relative pl-5">
                        <div className="absolute top-0 bottom-0 left-2 w-px bg-[var(--line-color)]" />
                        <div className="space-y-3">
                          {sortByDate(dream.milestones).map((milestone) => (
                            <div key={milestone.id} className="relative">
                              <div
                                className={`absolute -left-[13px] top-1 w-3 h-3 rounded-full border ${
                                  milestone.completedAt
                                    ? "bg-green-500 border-green-500"
                                    : "themed-card border-[var(--muted-text)]"
                                }`}
                              />
                              <div className="border themed-border rounded-lg p-3">
                                <div className="flex justify-between gap-3 items-start">
                                  <div>
                                    <div className="font-medium">
                                      {milestone.title}
                                    </div>
                                    <div className="text-xs themed-muted mt-1">
                                      Previsto:{" "}
                                      {toDateLabel(milestone.targetDate)}
                                    </div>
                                    {milestone.completedAt && (
                                      <div className="text-xs text-green-700 mt-1">
                                        Concluido em{" "}
                                        {new Date(
                                          milestone.completedAt,
                                        ).toLocaleDateString("pt-BR")}
                                      </div>
                                    )}
                                  </div>
                                  <button
                                    onClick={() =>
                                      toggleMilestone(dream.id, milestone.id)
                                    }
                                    className={`text-sm px-2 py-1 rounded ${
                                      milestone.completedAt
                                        ? "bg-green-100 text-green-700"
                                        : "themed-subtle themed-muted"
                                    }`}
                                  >
                                    {milestone.completedAt
                                      ? "Desmarcar"
                                      : "Marcar feito"}
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </section>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

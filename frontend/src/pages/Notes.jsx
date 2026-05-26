import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, FilePlus2, Pencil, Save, Trash2, X } from "lucide-react";
import notesService from "../services/notesService";
import { confirm, notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const emptyForm = {
  title: "",
  content: "",
};

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function Notes() {
  const [notes, setNotes] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const editingNote = useMemo(
    () => notes.find((note) => note.id === editingId),
    [notes, editingId],
  );

  useEffect(() => {
    async function loadNotes() {
      try {
        const data = await notesService.list();
        setNotes(data);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar anotações"));
      } finally {
        setLoading(false);
      }
    }

    loadNotes();
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const payload = {
      title: form.title.trim(),
      content: form.content.trim(),
    };

    if (!payload.title) {
      notify.error("Informe o título da anotação");
      return;
    }

    if (!payload.content) {
      notify.error("Escreva o conteúdo da anotação");
      return;
    }

    setSaving(true);
    try {
      if (editingId) {
        const updated = await notesService.update(editingId, payload);
        setNotes((prev) =>
          prev.map((note) => (note.id === updated.id ? updated : note)),
        );
        notify.success("Anotação atualizada");
      } else {
        const created = await notesService.create(payload);
        setNotes((prev) => [created, ...prev]);
        notify.success("Anotação criada");
      }
      resetForm();
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar anotação"));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (note) => {
    setEditingId(note.id);
    setForm({
      title: note.title,
      content: note.content,
    });
  };

  const handleDelete = (noteId) => {
    confirm({
      message: "Remover esta anotação?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        try {
          await notesService.remove(noteId);
          setNotes((prev) => prev.filter((note) => note.id !== noteId));
          if (editingId === noteId) {
            resetForm();
          }
          notify.success("Anotação removida");
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover anotação"));
        }
      },
    });
  };

  if (loading) {
    return <p className="p-6 themed-muted">Carregando anotações...</p>;
  }

  return (
    <div className="notes-page max-w-6xl mx-auto p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Anotações</h1>
          <p className="themed-muted">
            {notes.length === 1
              ? "1 anotação salva"
              : `${notes.length} anotações salvas`}
          </p>
        </div>

        <Link
          to="/finances"
          className="inline-flex items-center gap-2 themed-link font-medium"
        >
          <ArrowLeft size={18} />
          Voltar para Finanças
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6 items-start">
        <form
          onSubmit={handleSubmit}
          className="themed-card themed-border border rounded-lg p-5 shadow-sm"
        >
          <div className="flex items-center justify-between gap-3 mb-4">
            <h2 className="text-xl font-semibold">
              {editingNote ? "Editar anotação" : "Nova anotação"}
            </h2>
            {editingNote ? (
              <button
                type="button"
                onClick={resetForm}
                className="themed-border border rounded p-2 hover:opacity-80"
                aria-label="Cancelar edição"
                title="Cancelar edição"
              >
                <X size={18} />
              </button>
            ) : (
              <FilePlus2 className="themed-muted" size={22} />
            )}
          </div>

          <label
            className="block text-sm font-medium mb-2"
            htmlFor="note-title"
          >
            Título
          </label>
          <input
            id="note-title"
            type="text"
            className="themed-input rounded px-3 py-2 w-full mb-4"
            value={form.title}
            maxLength={200}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, title: event.target.value }))
            }
          />

          <label
            className="block text-sm font-medium mb-2"
            htmlFor="note-content"
          >
            Conteúdo
          </label>
          <textarea
            id="note-content"
            className="notes-editor themed-input rounded px-3 py-3 w-full min-h-80 resize-y"
            value={form.content}
            onChange={(event) =>
              setForm((prev) => ({ ...prev, content: event.target.value }))
            }
          />

          <button
            type="submit"
            disabled={saving}
            className="mt-4 inline-flex items-center justify-center gap-2 bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-700 disabled:opacity-60"
          >
            <Save size={18} />
            {saving ? "Salvando..." : "Salvar"}
          </button>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {notes.length === 0 ? (
            <div className="themed-card themed-border border rounded-lg p-6 themed-muted">
              Nenhuma anotação criada.
            </div>
          ) : (
            notes.map((note, index) => (
              <article
                key={note.id}
                className={`note-sheet themed-border border shadow-sm ${
                  index % 3 === 1
                    ? "note-sheet-blue"
                    : index % 3 === 2
                      ? "note-sheet-sky"
                      : "note-sheet-coral"
                }`}
              >
                <div className="note-sheet-header">
                  <h2 className="text-lg font-semibold truncate">
                    {note.title}
                  </h2>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => handleEdit(note)}
                      className="rounded p-2 hover:bg-black/10"
                      aria-label="Editar anotação"
                      title="Editar anotação"
                    >
                      <Pencil size={17} />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(note.id)}
                      className="rounded p-2 hover:bg-black/10"
                      aria-label="Excluir anotação"
                      title="Excluir anotação"
                    >
                      <Trash2 size={17} />
                    </button>
                  </div>
                </div>
                <div className="note-sheet-body">
                  <p className="whitespace-pre-wrap">{note.content}</p>
                </div>
                <div className="text-xs themed-muted px-4 pb-4">
                  Atualizada em {formatDate(note.updatedAt || note.createdAt)}
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

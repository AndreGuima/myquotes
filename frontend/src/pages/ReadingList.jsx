import { useEffect, useState } from "react";
import readingListService from "../services/readingListService";
import { notify, confirm } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const statusOptions = [
  { value: "to_read", label: "Quero ler" },
  { value: "reading", label: "Lendo" },
  { value: "read", label: "Lido" },
];

export default function ReadingList() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);
  const [logInputs, setLogInputs] = useState({});
  const [logsByBook, setLogsByBook] = useState({});

  const [newBook, setNewBook] = useState({
    title: "",
    author: "",
    status: "to_read",
    rating: "",
  });

  useEffect(() => {
    async function loadInitialBooks() {
      try {
        const data = await readingListService.list();
        setBooks(data);
      } catch (err) {
        notify.error(getApiErrorMessage(err, "Erro ao carregar livros"));
      } finally {
        setLoading(false);
      }
    }

    loadInitialBooks();
  }, []);

  const updateBookInState = (updated) => {
    setBooks((prev) => prev.map((b) => (b.id === updated.id ? updated : b)));
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newBook.title.trim()) {
      notify.error("Informe o título do livro");
      return;
    }

    const payload = {
      title: newBook.title.trim(),
      author: newBook.author.trim() || null,
      status: newBook.status,
      rating:
        newBook.status !== "to_read" && newBook.rating
          ? Number(newBook.rating)
          : null,
    };

    try {
      const created = await readingListService.create(payload);
      setBooks((prev) => [created, ...prev]);
      setNewBook({ title: "", author: "", status: "to_read", rating: "" });
      notify.success("Livro adicionado");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao adicionar livro"));
    }
  };

  const handleStatusChange = async (book, status) => {
    setSavingId(book.id);
    try {
      const updated = await readingListService.update(book.id, { status });
      updateBookInState(updated);
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao atualizar status"));
    } finally {
      setSavingId(null);
    }
  };

  const handleRatingChange = (bookId, value) => {
    setBooks((prev) =>
      prev.map((b) => (b.id === bookId ? { ...b, rating: value } : b)),
    );
  };

  const handleRatingSave = async (book, ratingValue) => {
    if (book.status === "to_read") return;

    setSavingId(book.id);
    try {
      const updated = await readingListService.update(book.id, {
        rating: ratingValue,
      });
      updateBookInState(updated);
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao atualizar avaliação"));
    } finally {
      setSavingId(null);
    }
  };

  const handleDelete = (bookId) => {
    confirm({
      message: "Remover este livro da sua lista?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        try {
          await readingListService.remove(bookId);
          setBooks((prev) => prev.filter((b) => b.id !== bookId));
          notify.success("Livro removido");
        } catch (err) {
          notify.error(getApiErrorMessage(err, "Erro ao remover livro"));
        }
      },
    });
  };

  const handleLogChange = (bookId, value) => {
    setLogInputs((prev) => ({ ...prev, [bookId]: value }));
  };

  const handleAddLog = async (bookId) => {
    const comment = (logInputs[bookId] || "").trim();
    if (!comment) {
      notify.error("Escreva um comentário");
      return;
    }

    try {
      const log = await readingListService.upsertLog(bookId, { comment });
      setLogsByBook((prev) => ({
        ...prev,
        [bookId]: [log, ...(prev[bookId] || []).filter((l) => l.id !== log.id)],
      }));
      setLogInputs((prev) => ({ ...prev, [bookId]: "" }));
      notify.success("Comentário salvo");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao salvar comentário"));
    }
  };

  const handleLoadLogs = async (bookId) => {
    try {
      const logs = await readingListService.listLogs(bookId, 7);
      setLogsByBook((prev) => ({ ...prev, [bookId]: logs }));
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao carregar comentários"));
    }
  };

  if (loading) {
    return <p className="p-4 themed-muted">Carregando lista...</p>;
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Lista de Leitura</h1>

      <form
        onSubmit={handleCreate}
        className="themed-card themed-border border rounded-lg shadow p-4 mb-8 grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <input
          type="text"
          placeholder="Título"
          className="themed-input rounded px-3 py-2"
          value={newBook.title}
          onChange={(e) =>
            setNewBook((prev) => ({ ...prev, title: e.target.value }))
          }
        />
        <input
          type="text"
          placeholder="Autor (opcional)"
          className="themed-input rounded px-3 py-2"
          value={newBook.author}
          onChange={(e) =>
            setNewBook((prev) => ({ ...prev, author: e.target.value }))
          }
        />
        <select
          className="themed-input rounded px-3 py-2"
          value={newBook.status}
          onChange={(e) =>
            setNewBook((prev) => ({ ...prev, status: e.target.value }))
          }
        >
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <div className="flex gap-2">
          <div className="flex items-center gap-1 px-2 border themed-border rounded">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                type="button"
                key={star}
                onClick={() =>
                  setNewBook((prev) => ({ ...prev, rating: String(star) }))
                }
                className={`text-lg ${
                  Number(newBook.rating) >= star
                    ? "text-yellow-400"
                    : "themed-muted"
                }`}
                disabled={newBook.status === "to_read"}
                aria-label={`Nota ${star}`}
              >
                ★
              </button>
            ))}
          </div>
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Adicionar
          </button>
        </div>
      </form>

      {books.length === 0 ? (
        <p className="themed-muted">Sua lista está vazia.</p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {books.map((book) => (
            <div
              key={book.id}
              className="themed-card themed-border border rounded-lg p-4 shadow-sm"
            >
              <div className="flex justify-between items-start gap-4">
                <div>
                  <h2 className="text-lg font-semibold">{book.title}</h2>
                  <p className="text-sm themed-muted">
                    {book.author || "Autor desconhecido"}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(book.id)}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  Remover
                </button>
              </div>

              <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
                <select
                  className="themed-input rounded px-3 py-2"
                  value={book.status}
                  onChange={(e) => handleStatusChange(book, e.target.value)}
                  disabled={savingId === book.id}
                >
                  {statusOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>

                <div className="flex items-center gap-1 border themed-border rounded px-2 py-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      type="button"
                      key={star}
                      onClick={() => {
                        handleRatingChange(book.id, String(star));
                        handleRatingSave(book, star);
                      }}
                      className={`text-lg ${
                        Number(book.rating) >= star
                          ? "text-yellow-400"
                          : "themed-muted"
                      }`}
                      disabled={
                        book.status === "to_read" || savingId === book.id
                      }
                      aria-label={`Nota ${star}`}
                    >
                      ★
                    </button>
                  ))}
                </div>

                <div className="text-sm themed-muted flex items-center">
                  {savingId === book.id ? "Salvando..." : " "}
                </div>
              </div>

              <div className="mt-4">
                <textarea
                  className="themed-input rounded px-3 py-2 w-full"
                  rows={2}
                  placeholder="Comentário do dia..."
                  value={logInputs[book.id] || ""}
                  onChange={(e) => handleLogChange(book.id, e.target.value)}
                />
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => handleAddLog(book.id)}
                    className="bg-emerald-600 text-white px-3 py-1 rounded text-sm"
                  >
                    Salvar comentário
                  </button>
                  <button
                    onClick={() => handleLoadLogs(book.id)}
                    className="text-sm themed-link"
                  >
                    Ver últimos comentários
                  </button>
                </div>
              </div>

              {logsByBook[book.id]?.length > 0 && (
                <div className="mt-3 text-sm themed-muted">
                  {logsByBook[book.id].slice(0, 3).map((log) => (
                    <div key={log.id} className="border-t themed-border py-2">
                      <span className="font-medium">{log.log_date}</span> —{" "}
                      {log.comment}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { useState, useMemo } from "react";

export default function DataTable({
  title,
  createLabel,
  createLink,
  columns,
  data,
  renderRow,
  pageSize = 10, // quantidade padrão por página
}) {
  const [page, setPage] = useState(1);

  // Total de páginas calculado automaticamente
  const totalPages = Math.max(1, Math.ceil(data.length / pageSize));

  // Garante que a página atual existe
  const currentPage = Math.min(page, totalPages);

  // Dados visíveis na página
  const pageData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return data.slice(start, start + pageSize);
  }, [data, currentPage, pageSize]);

  // Handlers
  const goPrev = () => setPage((p) => Math.max(1, p - 1));
  const goNext = () => setPage((p) => Math.min(totalPages, p + 1));
  const goTo = (p) => setPage(p);

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{title}</h1>

        {createLink && (
          <a
            href={createLink}
            className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {createLabel}
          </a>
        )}
      </div>

      {/* Tabela */}
      <div className="overflow-x-auto">
        <table className="w-full border text-left">
          <thead className="bg-gray-100">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="p-2 border"
                  style={col.width ? { width: col.width } : {}}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {pageData.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length}
                  className="p-4 text-center text-gray-500"
                >
                  Nenhum registro encontrado.
                </td>
              </tr>
            )}

            {pageData.map((row, idx) => renderRow(row, idx))}
          </tbody>
        </table>
      </div>

      {/* Paginação */}
      <div className="flex items-center justify-between mt-4">
        {/* Info */}
        <span className="text-gray-600">
          Página {currentPage} de {totalPages} — Total: {data.length}
        </span>

        {/* Controles */}
        <div className="flex gap-2">
          <button
            onClick={goPrev}
            disabled={currentPage === 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            ◀
          </button>

          {[...Array(totalPages)].map((_, i) => {
            const p = i + 1;
            return (
              <button
                key={p}
                onClick={() => goTo(p)}
                className={`px-3 py-1 border rounded ${
                  p === currentPage
                    ? "bg-blue-600 text-white"
                    : "hover:bg-gray-200"
                }`}
              >
                {p}
              </button>
            );
          })}

          <button
            onClick={goNext}
            disabled={currentPage === totalPages}
            className="px-3 py-1 border rounded disabled:opacity-50"
          >
            ▶
          </button>
        </div>
      </div>
    </div>
  );
}

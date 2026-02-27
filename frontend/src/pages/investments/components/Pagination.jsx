export default function Pagination({
  currentPage,
  totalPages,
  totalItems,
  visiblePageNumbers,
  onPrev,
  onNext,
  onGoToPage,
}) {
  return (
    <div className="flex items-center justify-between p-4 border-t themed-border">
      <span className="text-sm themed-muted">
        Página {currentPage} de {totalPages} - Total filtrado: {totalItems}
      </span>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={onPrev}
          disabled={currentPage === 1}
          className="px-3 py-1 border themed-border rounded disabled:opacity-50 hover:opacity-90"
        >
          ◀
        </button>
        {visiblePageNumbers.map((targetPage) => (
          <button
            key={targetPage}
            type="button"
            onClick={() => onGoToPage(targetPage)}
            className={`px-3 py-1 border themed-border rounded ${
              targetPage === currentPage
                ? "bg-blue-600 text-white"
                : "themed-subtle hover:opacity-90"
            }`}
          >
            {targetPage}
          </button>
        ))}
        <button
          type="button"
          onClick={onNext}
          disabled={currentPage === totalPages}
          className="px-3 py-1 border themed-border rounded disabled:opacity-50 hover:opacity-90"
        >
          ▶
        </button>
      </div>
    </div>
  );
}

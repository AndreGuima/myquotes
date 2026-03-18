import Pagination from "./Pagination";

function SortableHeader({
  label,
  sortKey,
  sortConfig,
  onSort,
  alignRight = false,
}) {
  const isActive = sortConfig.key === sortKey;
  const indicator = isActive
    ? sortConfig.direction === "asc"
      ? "↑"
      : "↓"
    : "↕";

  return (
    <th className={`py-3 px-4 ${alignRight ? "text-right" : ""}`}>
      <button
        type="button"
        onClick={() => onSort(sortKey)}
        className={alignRight ? "w-full text-right" : ""}
      >
        {label} {indicator}
      </button>
    </th>
  );
}

export default function InvestmentTable({
  loading,
  sortedInvestments,
  paginatedInvestments,
  sortConfig,
  onSort,
  onEdit,
  onRemove,
  removingId,
  formatCurrency,
  currentPage,
  totalPages,
  visiblePageNumbers,
  onPrevPage,
  onNextPage,
  onGoToPage,
  formatDateTime,
}) {
  return (
    <div className="themed-card themed-border border rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="themed-subtle">
            <tr>
              <SortableHeader
                label="Tipo"
                sortKey="asset_type"
                sortConfig={sortConfig}
                onSort={onSort}
              />
              <SortableHeader
                label="Setor"
                sortKey="sector"
                sortConfig={sortConfig}
                onSort={onSort}
              />
              <SortableHeader
                label="Ticker"
                sortKey="ticker"
                sortConfig={sortConfig}
                onSort={onSort}
              />
              <SortableHeader
                label="Nome"
                sortKey="name"
                sortConfig={sortConfig}
                onSort={onSort}
              />
              <SortableHeader
                label="Qtd"
                sortKey="quantity"
                sortConfig={sortConfig}
                onSort={onSort}
                alignRight
              />
              <SortableHeader
                label="Preço Médio"
                sortKey="average_price"
                sortConfig={sortConfig}
                onSort={onSort}
                alignRight
              />
              <SortableHeader
                label="Preço Atual"
                sortKey="current_price"
                sortConfig={sortConfig}
                onSort={onSort}
                alignRight
              />
              <SortableHeader
                label="Investido"
                sortKey="invested"
                sortConfig={sortConfig}
                onSort={onSort}
                alignRight
              />
              <SortableHeader
                label="Atual"
                sortKey="current"
                sortConfig={sortConfig}
                onSort={onSort}
                alignRight
              />
              <SortableHeader
                label="Resultado"
                sortKey="result"
                sortConfig={sortConfig}
                onSort={onSort}
                alignRight
              />
              <th className="py-3 px-4 text-right">Ações</th>
            </tr>
          </thead>

          <tbody>
            {!loading && sortedInvestments.length === 0 && (
              <tr>
                <td colSpan={11} className="py-6 text-center themed-muted">
                  Nenhum investimento cadastrado.
                </td>
              </tr>
            )}

            {paginatedInvestments.map((item) => (
              <tr key={item.id} className="border-t themed-border">
                <td className="py-3 px-4">{item.assetTypeLabel}</td>
                <td className="py-3 px-4">{item.sector || "-"}</td>
                <td className="py-3 px-4 font-semibold">{item.ticker}</td>
                <td className="py-3 px-4">{item.name || "-"}</td>
                <td className="py-3 px-4 text-right">{item.quantityNumber}</td>
                <td className="py-3 px-4 text-right">
                  {formatCurrency(item.averagePriceNumber)}
                </td>
                <td className="py-3 px-4 text-right">
                  {formatCurrency(item.currentPriceNumber)}
                  <div className="themed-muted text-xs mt-1">
                    {item.price_updated_at
                      ? formatDateTime(item.price_updated_at)
                      : "Aguardando sync"}
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  {formatCurrency(item.invested)}
                </td>
                <td className="py-3 px-4 text-right">
                  {formatCurrency(item.current)}
                </td>
                <td
                  className={`py-3 px-4 text-right font-semibold ${
                    item.result >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {formatCurrency(item.result)}
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="inline-flex gap-2">
                    <button
                      type="button"
                      onClick={() => onEdit(item)}
                      className="themed-card themed-border border px-3 py-1 rounded hover:opacity-90"
                    >
                      Editar
                    </button>
                    <button
                      type="button"
                      onClick={() => onRemove(item.id)}
                      className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded disabled:opacity-60"
                      disabled={removingId === item.id}
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

      {!loading && sortedInvestments.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={sortedInvestments.length}
          visiblePageNumbers={visiblePageNumbers}
          onPrev={onPrevPage}
          onNext={onNextPage}
          onGoToPage={onGoToPage}
        />
      )}
    </div>
  );
}

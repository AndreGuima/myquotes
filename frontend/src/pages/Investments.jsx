import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import investmentsService from "../services/investmentsService";
import { confirm, notify } from "../core/toast";
import { normalizeInvestmentSector } from "../constants/investmentSectors";
import InvestmentSummary from "./investments/components/InvestmentSummary";
import InvestmentForm from "./investments/components/InvestmentForm";
import InvestmentFilters from "./investments/components/InvestmentFilters";
import InvestmentTable from "./investments/components/InvestmentTable";

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function getInitialForm() {
  return {
    assetType: "stock",
    sector: "",
    ticker: "",
    name: "",
    quantity: "",
    averagePrice: "",
    currentPrice: "",
  };
}

function getAssetTypeLabel(type) {
  if (type === "fii") return "FII";
  return "Ação";
}

const SORT_MAP = {
  asset_type: (item) => item.assetTypeLabel,
  sector: (item) => item.sector || "",
  ticker: (item) => item.ticker || "",
  name: (item) => item.name || "",
  quantity: (item) => item.quantityNumber,
  average_price: (item) => item.averagePriceNumber,
  current_price: (item) => item.currentPriceNumber,
  invested: (item) => item.invested,
  current: (item) => item.current,
  result: (item) => item.result,
};

export default function Investments() {
  const PAGE_SIZE = 10;
  const [investments, setInvestments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [page, setPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({
    key: "ticker",
    direction: "asc",
  });

  const [form, setForm] = useState(getInitialForm);
  const [filters, setFilters] = useState({
    query: "",
    assetType: "",
  });

  const normalizedInvestments = useMemo(
    () =>
      investments.map((item) => {
        const quantity = Number(item.quantity || 0);
        const averagePrice = Number(item.average_price || 0);
        const currentPrice = Number(item.current_price || 0);
        const invested = quantity * averagePrice;
        const current = quantity * currentPrice;
        const result = current - invested;

        return {
          ...item,
          quantityNumber: quantity,
          averagePriceNumber: averagePrice,
          currentPriceNumber: currentPrice,
          invested,
          current,
          result,
          assetTypeLabel: getAssetTypeLabel(item.asset_type),
        };
      }),
    [investments],
  );

  useEffect(() => {
    async function loadData() {
      try {
        const data = await investmentsService.list();
        setInvestments(Array.isArray(data) ? data : []);
      } catch {
        notify.error("Erro ao carregar investimentos");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const totalInvested = useMemo(
    () => normalizedInvestments.reduce((acc, item) => acc + item.invested, 0),
    [normalizedInvestments],
  );

  const totalCurrent = useMemo(
    () => normalizedInvestments.reduce((acc, item) => acc + item.current, 0),
    [normalizedInvestments],
  );

  const profitability = useMemo(() => {
    if (totalInvested <= 0) return 0;
    return ((totalCurrent - totalInvested) / totalInvested) * 100;
  }, [totalCurrent, totalInvested]);

  const filteredInvestments = useMemo(() => {
    const normalizedQuery = filters.query.trim().toLowerCase();

    return normalizedInvestments.filter((item) => {
      const matchesType = filters.assetType
        ? item.asset_type === filters.assetType
        : true;

      const matchesQuery = normalizedQuery
        ? [item.ticker, item.name, item.sector]
            .filter(Boolean)
            .join(" ")
            .toLowerCase()
            .includes(normalizedQuery)
        : true;

      return matchesType && matchesQuery;
    });
  }, [normalizedInvestments, filters]);

  const sortedInvestments = useMemo(() => {
    const directionFactor = sortConfig.direction === "asc" ? 1 : -1;
    const getSortValue = SORT_MAP[sortConfig.key] || (() => "");

    return [...filteredInvestments].sort((a, b) => {
      const aValue = getSortValue(a);
      const bValue = getSortValue(b);

      if (typeof aValue === "number" && typeof bValue === "number") {
        return (aValue - bValue) * directionFactor;
      }

      return (
        String(aValue).localeCompare(String(bValue), "pt-BR", {
          sensitivity: "base",
        }) * directionFactor
      );
    });
  }, [filteredInvestments, sortConfig]);

  const totalPages = Math.max(
    1,
    Math.ceil(sortedInvestments.length / PAGE_SIZE),
  );
  const currentPage = Math.min(page, totalPages);

  useEffect(() => {
    setPage((prev) => Math.min(Math.max(prev, 1), totalPages));
  }, [totalPages]);

  const paginatedInvestments = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return sortedInvestments.slice(start, start + PAGE_SIZE);
  }, [currentPage, sortedInvestments]);

  const visiblePageNumbers = useMemo(() => {
    const start = Math.max(1, currentPage - 2);
    const end = Math.min(totalPages, currentPage + 2);
    const pages = [];

    for (let p = start; p <= end; p += 1) {
      pages.push(p);
    }

    return pages;
  }, [currentPage, totalPages]);

  useEffect(() => {
    setPage(1);
  }, [filters]);

  function handleSort(columnKey) {
    setSortConfig((prev) => {
      if (prev.key === columnKey) {
        return {
          key: columnKey,
          direction: prev.direction === "asc" ? "desc" : "asc",
        };
      }

      return {
        key: columnKey,
        direction: "asc",
      };
    });
    setPage(1);
  }

  function resetForm() {
    setForm(getInitialForm());
    setEditingId(null);
  }

  function startEditing(item) {
    setEditingId(item.id);
    setForm({
      assetType: item.asset_type || "stock",
      sector: normalizeInvestmentSector(item.asset_type, item.sector),
      ticker: String(item.ticker || ""),
      name: String(item.name || ""),
      quantity: String(item.quantity || ""),
      averagePrice: String(item.average_price || ""),
      currentPrice: String(item.current_price || ""),
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();

    const quantity = Number(form.quantity);
    const averagePrice = Number(form.averagePrice);
    const currentPrice = Number(form.currentPrice);
    const ticker = form.ticker.trim().toUpperCase();

    if (!ticker) {
      notify.error("Informe o ticker do ativo");
      return;
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      notify.error("Informe uma quantidade válida");
      return;
    }

    if (!Number.isFinite(averagePrice) || averagePrice < 0) {
      notify.error("Informe um preço médio válido");
      return;
    }

    if (!Number.isFinite(currentPrice) || currentPrice < 0) {
      notify.error("Informe um preço atual válido");
      return;
    }

    const payload = {
      asset_type: form.assetType,
      sector: normalizeInvestmentSector(form.assetType, form.sector),
      ticker,
      name: form.name,
      quantity,
      average_price: averagePrice,
      current_price: currentPrice,
    };

    setSaving(true);
    try {
      if (editingId) {
        const updated = await investmentsService.update(editingId, payload);
        setInvestments((prev) =>
          prev.map((item) => (item.id === editingId ? updated : item)),
        );
        notify.success("Investimento atualizado");
      } else {
        const created = await investmentsService.create(payload);
        setInvestments((prev) => [...prev, created]);
        notify.success("Investimento cadastrado");
      }

      resetForm();
    } catch {
      notify.error("Erro ao salvar investimento");
    } finally {
      setSaving(false);
    }
  }

  function handleRemove(id) {
    confirm({
      message: "Deseja remover este investimento?",
      confirmText: "Remover",
      cancelText: "Cancelar",
      variant: "danger",
      onConfirm: async () => {
        setRemovingId(id);
        try {
          await investmentsService.remove(id);
          setInvestments((prev) => prev.filter((item) => item.id !== id));
          if (editingId === id) resetForm();
          notify.success("Investimento removido");
        } catch {
          notify.error("Erro ao remover investimento");
        } finally {
          setRemovingId(null);
        }
      },
    });
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Investimentos</h1>
        <Link
          to="/finances"
          className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
        >
          Voltar para Finanças
        </Link>
      </div>

      <p className="themed-muted mb-6">
        Cadastre suas ações e FIIs para acompanhar posição e rentabilidade.
      </p>

      <InvestmentSummary
        totalInvested={totalInvested}
        totalCurrent={totalCurrent}
        profitability={profitability}
        formatCurrency={formatCurrency}
      />

      <InvestmentForm
        editingId={editingId}
        form={form}
        setForm={setForm}
        saving={saving}
        onSubmit={handleSubmit}
        onCancelEdit={resetForm}
      />

      <InvestmentFilters filters={filters} setFilters={setFilters} />

      <InvestmentTable
        loading={loading}
        sortedInvestments={sortedInvestments}
        paginatedInvestments={paginatedInvestments}
        sortConfig={sortConfig}
        onSort={handleSort}
        onEdit={startEditing}
        onRemove={handleRemove}
        removingId={removingId}
        formatCurrency={formatCurrency}
        currentPage={currentPage}
        totalPages={totalPages}
        visiblePageNumbers={visiblePageNumbers}
        onPrevPage={() => setPage((prev) => Math.max(1, prev - 1))}
        onNextPage={() => setPage((prev) => Math.min(totalPages, prev + 1))}
        onGoToPage={setPage}
      />
    </div>
  );
}

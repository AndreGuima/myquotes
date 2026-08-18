import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import reportsService from "../services/reportsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

function toDateInputValue(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}

export default function EntriesVsExpenses() {
  const [rows, setRows] = useState([]);
  const [fromDate, setFromDate] = useState(() => {
    const now = new Date();
    const early = new Date(now.getTime() - 29 * 24 * 60 * 60 * 1000);
    return toDateInputValue(early);
  });
  const [toDate, setToDate] = useState(() => toDateInputValue(new Date()));
  const [loading, setLoading] = useState(false);

  async function loadData() {
    setLoading(true);
    try {
      const data = await reportsService.dailyCashflow({
        from: fromDate,
        to: toDate,
      });
      setRows(Array.isArray(data) ? data : []);
    } catch (err) {
      notify.error(
        getApiErrorMessage(err, "Erro ao carregar entradas e saídas"),
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const run = async () => {
      await loadData();
    };

    // A carga inicial é intencional e depende do servidor; o efeito só dispara
    // uma vez para popular a tela sem re-render em cascata.
    void run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totals = useMemo(() => {
    return rows.reduce(
      (acc, r) => {
        acc.incomings += Number(r.incomings || 0);
        acc.outgoings += Number(r.outgoings || 0);
        return acc;
      },
      { incomings: 0, outgoings: 0 },
    );
  }, [rows]);

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Entrada x Saídas</h1>
        <div className="flex items-center gap-2">
          <Link
            to="/finances"
            className="themed-card themed-border border px-3 py-2 rounded hover:opacity-90 transition"
          >
            Voltar para Finanças
          </Link>
        </div>
      </div>

      <p className="themed-muted mb-6">
        Balanço diário entre entradas e saídas.
      </p>

      <div className="themed-card themed-border border rounded-xl p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          <input
            type="date"
            className="themed-input rounded px-3 py-2"
            value={fromDate}
            onChange={(e) => setFromDate(e.target.value)}
          />
          <input
            type="date"
            className="themed-input rounded px-3 py-2"
            value={toDate}
            onChange={(e) => setToDate(e.target.value)}
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={loadData}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? "Carregando..." : "Filtrar"}
            </button>
          </div>
        </div>
      </div>

      <div className="themed-card themed-border border rounded-xl p-4 mb-4">
        <h2 className="text-lg font-semibold mb-2">Totais</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="themed-muted text-sm">Entradas</div>
            <div className="text-2xl font-bold">
              {totals.incomings.toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL",
              })}
            </div>
          </div>
          <div>
            <div className="themed-muted text-sm">Saídas</div>
            <div className="text-2xl font-bold">
              {totals.outgoings.toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL",
              })}
            </div>
          </div>
          <div>
            <div className="themed-muted text-sm">Diferença</div>
            <div className="text-2xl font-bold">
              {(totals.incomings - totals.outgoings).toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL",
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="themed-card themed-border border rounded-xl p-4">
        <h2 className="text-lg font-semibold mb-2">Por Dia</h2>
        {rows.length === 0 ? (
          <p className="themed-muted">
            Nenhum registro encontrado para o período.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b themed-border">
                  <th className="py-2 pr-2">Data</th>
                  <th className="py-2 pr-2">Entradas</th>
                  <th className="py-2 pr-2">Saídas</th>
                  <th className="py-2 pr-2">Diferença</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.date} className="border-b themed-border">
                    <td className="py-2 pr-2">{r.date}</td>
                    <td className="py-2 pr-2">
                      {Number(r.incomings || 0).toLocaleString("pt-BR", {
                        style: "currency",
                        currency: "BRL",
                      })}
                    </td>
                    <td className="py-2 pr-2">
                      {Number(r.outgoings || 0).toLocaleString("pt-BR", {
                        style: "currency",
                        currency: "BRL",
                      })}
                    </td>
                    <td className="py-2 pr-2">
                      {(
                        Number(r.incomings || 0) - Number(r.outgoings || 0)
                      ).toLocaleString("pt-BR", {
                        style: "currency",
                        currency: "BRL",
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

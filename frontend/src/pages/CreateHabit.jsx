import { useState } from "react";
import { useNavigate } from "react-router-dom";
import habitsService from "../services/habitsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

const weekdayOptions = [
  { value: 0, short: "D", label: "Domingo" },
  { value: 1, short: "S", label: "Segunda" },
  { value: 2, short: "T", label: "Terça" },
  { value: 3, short: "Q", label: "Quarta" },
  { value: 4, short: "Q", label: "Quinta" },
  { value: 5, short: "S", label: "Sexta" },
  { value: 6, short: "S", label: "Sábado" },
];

export default function CreateHabit() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [frequencyType, setFrequencyType] = useState("daily");
  const [weekdays, setWeekdays] = useState([]);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [loading, setLoading] = useState(false);

  function toggleWeekday(day) {
    setWeekdays((prev) => {
      if (prev.includes(day)) {
        return prev.filter((item) => item !== day);
      }
      return [...prev, day].sort((a, b) => a - b);
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (endTime && !startTime) {
      notify.error("Defina o horário de início antes do fim");
      return;
    }
    if (frequencyType === "weekly" && weekdays.length === 0) {
      notify.error("Selecione pelo menos um dia da semana");
      return;
    }
    setLoading(true);

    try {
      const payload = {
        title,
        frequency_type: frequencyType,
      };

      if (startTime) {
        payload.start_time = startTime;
      }

      if (endTime) {
        payload.end_time = endTime;
      }

      if (frequencyType === "weekly") {
        payload.weekdays = weekdays;
      }

      await habitsService.create(payload);
      navigate("/habits");
    } catch (err) {
      notify.error(getApiErrorMessage(err, "Erro ao criar hábito"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Criar Hábito</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Título */}
        <div>
          <label className="block mb-1 font-medium">Título</label>
          <input
            className="w-full border p-2 rounded"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="Ex.: Beber água"
          />
        </div>

        {/* Frequência */}
        <div>
          <label className="block mb-1 font-medium">Frequência</label>
          <select
            className="w-full border p-2 rounded"
            value={frequencyType}
            onChange={(e) => setFrequencyType(e.target.value)}
          >
            <option value="daily">Diário</option>
            <option value="weekly">Semanal</option>
          </select>
        </div>

        {/* Horário */}
        <div>
          <label className="block mb-1 font-medium">Horário</label>
          <div className="flex gap-3">
            <input
              type="time"
              className="w-full border p-2 rounded"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
            />
            <input
              type="time"
              className="w-full border p-2 rounded"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              placeholder="Fim (opcional)"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Defina um intervalo se quiser, inclusive atravessando a meia-noite.
          </p>
        </div>

        {/* Configuração semanal */}
        {frequencyType === "weekly" && (
          <div>
            <label className="block mb-2 font-medium">Dias da semana</label>
            <div className="flex flex-wrap gap-2">
              {weekdayOptions.map((day) => {
                const active = weekdays.includes(day.value);
                return (
                  <button
                    key={day.value}
                    type="button"
                    onClick={() => toggleWeekday(day.value)}
                    title={day.label}
                    aria-pressed={active}
                    className={`h-10 w-10 rounded-full border text-sm font-semibold transition ${
                      active
                        ? "bg-blue-600 text-white border-blue-600"
                        : "bg-white text-gray-700 border-gray-300 hover:border-blue-400"
                    }`}
                  >
                    {day.short}
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Selecione em quais dias esse hábito deve aparecer.
            </p>
          </div>
        )}

        <button
          disabled={
            loading ||
            !title.trim() ||
            (frequencyType === "weekly" && weekdays.length === 0)
          }
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Salvando..." : "Criar hábito"}
        </button>
      </form>
    </div>
  );
}

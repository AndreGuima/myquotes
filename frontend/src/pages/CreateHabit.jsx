import { useState } from "react";
import { useNavigate } from "react-router-dom";
import habitsService from "../services/habitsService";
import { notify } from "../core/toast";
import { getApiErrorMessage } from "../core/apiError";

export default function CreateHabit() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [frequencyType, setFrequencyType] = useState("daily");
  const [weeklyTarget, setWeeklyTarget] = useState(3);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        title,
        frequency_type: frequencyType,
      };

      if (frequencyType === "weekly") {
        payload.target_per_week = weeklyTarget;
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

        {/* Meta semanal */}
        {frequencyType === "weekly" && (
          <div>
            <label className="block mb-1 font-medium">
              Meta semanal (vezes)
            </label>
            <input
              type="number"
              min={1}
              max={7}
              className="w-full border p-2 rounded"
              value={weeklyTarget}
              onChange={(e) => setWeeklyTarget(Number(e.target.value))}
              required
            />
          </div>
        )}

        <button
          disabled={loading || !title.trim()}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Salvando..." : "Criar hábito"}
        </button>
      </form>
    </div>
  );
}

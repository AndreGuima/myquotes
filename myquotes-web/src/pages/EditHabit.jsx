import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import habitsService from "../services/habitsService";

export default function EditHabit() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [frequencyType, setFrequencyType] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // ============================
  // 📥 Carregar hábito
  // ============================
  useEffect(() => {
    habitsService
      .list()
      .then((habits) => {
        const habit = habits.find((h) => h.id === Number(id));

        if (!habit) {
          setError("Hábito não encontrado");
          return;
        }

        setTitle(habit.title);
        setFrequencyType(habit.frequency_type);
      })
      .catch(() => {
        setError("Erro ao carregar hábito");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  // ============================
  // 💾 Salvar alteração
  // ============================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      await habitsService.update(id, { title });
      navigate("/habits");
    } catch {
      setError("Erro ao atualizar hábito");
    } finally {
      setSaving(false);
    }
  };

  // ============================
  // ⏳ Loading
  // ============================
  if (loading) {
    return (
      <div className="p-6 max-w-xl mx-auto text-gray-600">
        Carregando hábito...
      </div>
    );
  }

  // ============================
  // ❌ Erro
  // ============================
  if (error) {
    return (
      <div className="p-6 max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Editar Hábito</h1>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  // ============================
  // ✏️ Formulário
  // ============================
  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Editar Hábito</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Título */}
        <div>
          <label className="block text-sm font-medium mb-1">
            Nome do hábito
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>

        {/* Frequência (somente leitura) */}
        <div>
          <label className="block text-sm font-medium mb-1">Frequência</label>
          <input
            type="text"
            value={
              frequencyType === "daily"
                ? "Diário"
                : frequencyType === "weekly"
                  ? "Semanal"
                  : ""
            }
            disabled
            className="w-full border rounded px-3 py-2 bg-gray-100 text-gray-600"
          />
        </div>

        {/* Ações */}
        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={() => navigate("/habits")}
            className="px-4 py-2 border rounded"
            disabled={saving}
          >
            Cancelar
          </button>

          <button
            type="submit"
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          >
            {saving ? "Salvando..." : "Salvar"}
          </button>
        </div>
      </form>
    </div>
  );
}

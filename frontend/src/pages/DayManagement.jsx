import { Link } from "react-router-dom";

export default function DayManagement() {
  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">Gestão do Dia</h1>
      <p className="themed-muted mb-8">
        Acesse os módulos do seu planejamento diário.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Link
          to="/habits"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition"
        >
          <div className="text-lg font-semibold mb-1">Hábitos</div>
          <div className="themed-muted text-sm">
            Gerencie seus hábitos, frequência e progresso.
          </div>
        </Link>

        <Link
          to="/daily-routine"
          className="themed-card themed-border border rounded-xl p-5 hover:shadow-md transition"
        >
          <div className="text-lg font-semibold mb-1">Rotina do Dia</div>
          <div className="themed-muted text-sm">
            Visualize e acompanhe seus hábitos ao longo da rotina diária.
          </div>
        </Link>
      </div>
    </div>
  );
}

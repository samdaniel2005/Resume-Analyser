import { Link, useNavigate } from "react-router-dom";
import StatusBadge from "@/components/StatusBadge";

export default function CandidateTable({ items, loading }) {
  const navigate = useNavigate();

  return (
    <div className="bg-white border border-black/5 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full" data-testid="candidates-table">
          <thead>
            <tr className="text-left text-[10.5px] tracking-[0.18em] uppercase font-bold text-slate-500 border-b border-black/5 bg-slate-50/60">
              <th className="px-4 py-3 w-12">#</th>
              <th className="px-4 py-3">Candidate</th>
              <th className="px-4 py-3 hidden md:table-cell">Email</th>
              <th className="px-4 py-3 hidden lg:table-cell">Filename</th>
              <th className="px-4 py-3 hidden sm:table-cell">Status</th>
              <th className="px-4 py-3 text-right">Score</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-4 py-12 text-center text-sm text-slate-500">Loading…</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-14 text-center" data-testid="candidates-empty">
                <div className="font-display text-lg font-bold text-slate-900">No candidates match.</div>
                <div className="text-sm text-slate-500 mt-1">Try adjusting filters or upload new resumes.</div>
              </td></tr>
            ) : items.map((c, i) => (
              <tr
                key={c.id}
                data-testid={`candidate-row-${i}`}
                onClick={() => navigate(`/candidates/${c.id}`)}
                className="border-b border-black/5 hover:bg-slate-50/70 transition-colors cursor-pointer"
              >
                <td className="px-4 py-3.5 text-[12px] text-slate-400 font-bold tabular-nums">{i + 1}</td>
                <td className="px-4 py-3.5">
                  <Link
                    to={`/candidates/${c.id}`}
                    onClick={(e) => e.stopPropagation()}
                    className="font-semibold text-slate-950 hover:text-[#002FA7]"
                  >
                    {c.name}
                  </Link>
                </td>
                <td className="px-4 py-3.5 hidden md:table-cell text-[13px] text-slate-600">{c.email || <span className="text-slate-300">—</span>}</td>
                <td className="px-4 py-3.5 hidden lg:table-cell text-[12.5px] text-slate-500 truncate max-w-[220px]">{c.filename}</td>
                <td className="px-4 py-3.5 hidden sm:table-cell"><StatusBadge status={c.status} /></td>
                <td className="px-4 py-3.5 text-right">
                  <span className="font-display text-lg font-black tracking-tight text-slate-950 tabular-nums">{c.final_score}</span>
                  <span className="text-[11px] text-slate-400 ml-1">/125</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

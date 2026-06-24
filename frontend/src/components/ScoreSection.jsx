import { Mail, Phone, FileText, CheckCircle2, XCircle, Clock } from "lucide-react";
import StatusBadge from "@/components/StatusBadge";

const DECISIONS = [
  { value: "selected", label: "Select", icon: CheckCircle2, cls: "border-emerald-200 text-emerald-700 hover:bg-emerald-50 data-[active=true]:bg-emerald-600 data-[active=true]:text-white data-[active=true]:border-emerald-600" },
  { value: "hold", label: "Hold", icon: Clock, cls: "border-amber-200 text-amber-700 hover:bg-amber-50 data-[active=true]:bg-amber-500 data-[active=true]:text-white data-[active=true]:border-amber-500" },
  { value: "rejected", label: "Reject", icon: XCircle, cls: "border-rose-200 text-rose-700 hover:bg-rose-50 data-[active=true]:bg-rose-600 data-[active=true]:text-white data-[active=true]:border-rose-600" },
];

export default function ScoreSection({ candidate, onDecision }) {
  return (
    <div className="bg-white border border-black/5 p-8" data-testid="candidate-score-card">
      <div className="text-[10.5px] tracking-[0.22em] uppercase font-bold text-slate-500">Composite score</div>
      <div className="flex items-baseline gap-2 mt-3">
        <div className="font-display text-7xl font-black tracking-tight text-slate-950 tabular-nums leading-none">
          {candidate.final_score}
        </div>
        <div className="text-slate-400 text-lg">/ 125</div>
      </div>
      <div className="mt-5">
        <StatusBadge status={candidate.status} testId="candidate-status-badge" />
      </div>

      <div className="mt-8 pt-6 border-t border-black/5">
        <div className="text-[10.5px] tracking-[0.22em] uppercase font-bold text-slate-500 mb-3">Recruiter decision</div>
        <div className="flex flex-col gap-2">
          {DECISIONS.map(({ value, label, icon: Icon, cls }) => (
            <button
              key={value}
              onClick={() => onDecision(value)}
              data-active={candidate.decision === value}
              data-testid={`decision-${value}`}
              className={`inline-flex items-center justify-center gap-2 px-3 py-2.5 text-sm font-semibold border bg-white transition-colors ${cls}`}
            >
              <Icon className="w-4 h-4" strokeWidth={1.75} /> {label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-8 pt-6 border-t border-black/5 space-y-2.5">
        {candidate.email && (
          <div className="flex items-center gap-2 text-[13px] text-slate-700">
            <Mail className="w-4 h-4 text-slate-400" strokeWidth={1.75} /> {candidate.email}
          </div>
        )}
        {candidate.phone && (
          <div className="flex items-center gap-2 text-[13px] text-slate-700">
            <Phone className="w-4 h-4 text-slate-400" strokeWidth={1.75} /> {candidate.phone}
          </div>
        )}
        <div className="flex items-center gap-2 text-[13px] text-slate-700">
          <FileText className="w-4 h-4 text-slate-400" strokeWidth={1.75} /> {candidate.filename}
        </div>
      </div>
    </div>
  );
}

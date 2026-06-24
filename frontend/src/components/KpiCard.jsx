const KpiCard = ({ label, value, hint, accent, testId }) => (
  <div
    data-testid={testId}
    className="bg-white border border-black/5 p-6 hover:-translate-y-0.5 hover:shadow-sm transition-all"
  >
    <div className="text-[10.5px] tracking-[0.22em] uppercase font-bold text-slate-500">{label}</div>
    <div className="mt-3 flex items-baseline gap-2">
      <div className="font-display text-4xl font-black tracking-tight text-slate-950 tabular-nums">{value}</div>
      {accent && <div className="text-xs text-slate-500">{accent}</div>}
    </div>
    {hint && <div className="text-[12px] text-slate-500 mt-2 leading-relaxed">{hint}</div>}
  </div>
);

export default KpiCard;

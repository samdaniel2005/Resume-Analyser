export default function ScoreBar({ label, value, max, testId }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div data-testid={testId}>
      <div className="flex items-baseline justify-between mb-1.5">
        <div className="text-[12.5px] text-slate-700 font-medium">{label}</div>
        <div className="text-[12px] text-slate-500 tabular-nums">
          <span className="font-semibold text-slate-900">{value}</span>
          <span className="text-slate-400"> / {max}</span>
        </div>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

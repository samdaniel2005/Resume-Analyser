import ScoreBar from "@/components/ScoreBar";
import { CATEGORY_LABELS, CATEGORY_ORDER } from "@/lib/api";

export default function BreakdownSection({ breakdown, weights }) {
  return (
    <div className="lg:col-span-2 bg-white border border-black/5 p-8" data-testid="score-breakdown-card">
      <div className="flex items-baseline justify-between mb-6">
        <div>
          <div className="text-[10.5px] tracking-[0.22em] uppercase font-bold text-slate-500">Score breakdown</div>
          <h3 className="font-display text-xl font-bold text-slate-950 mt-1">8 weighted categories</h3>
        </div>
        {breakdown.penalty < 0 && (
          <div className="text-[12px] text-rose-600 font-semibold">Penalty: {breakdown.penalty}</div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
        {CATEGORY_ORDER.map((key) => (
          <ScoreBar
            key={key}
            testId={`category-${key}`}
            label={CATEGORY_LABELS[key]}
            value={breakdown[key] || 0}
            max={weights[key]}
          />
        ))}
      </div>
    </div>
  );
}

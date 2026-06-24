import { useState } from "react";
import { Plus, X } from "lucide-react";
import { KEYWORD_GROUP_LABELS } from "@/lib/api";

function KeywordGroup({ group, values, onChange }) {
  const [input, setInput] = useState("");

  const add = () => {
    const v = input.trim().toLowerCase();
    if (!v) return;
    if (values.includes(v)) { setInput(""); return; }
    onChange([...values, v]);
    setInput("");
  };
  const remove = (kw) => onChange(values.filter((k) => k !== kw));

  return (
    <div className="bg-white border border-black/5 p-6" data-testid={`keyword-group-${group}`}>
      <div className="flex items-baseline justify-between mb-4">
        <div>
          <div className="text-[10.5px] tracking-[0.22em] uppercase font-bold text-slate-500">{group}</div>
          <h4 className="font-display text-lg font-bold text-slate-950 mt-0.5">{KEYWORD_GROUP_LABELS[group] || group}</h4>
        </div>
        <div className="text-[12px] text-slate-500">{values.length} terms</div>
      </div>
      <div className="flex flex-wrap gap-2 mb-3">
        {values.map((kw) => (
          <span
            key={kw}
            data-testid={`keyword-chip-${group}-${kw}`}
            className="inline-flex items-center gap-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 px-2.5 py-1 text-[12.5px] font-medium transition-colors"
          >
            {kw}
            <button onClick={() => remove(kw)} aria-label={`Remove ${kw}`} className="text-slate-500 hover:text-rose-600">
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
        {values.length === 0 && <div className="text-xs text-slate-400 italic">No terms — add one to start.</div>}
      </div>
      <div className="flex items-center gap-2 max-w-md">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); add(); } }}
          placeholder="Add a keyword and press Enter…"
          data-testid={`keyword-input-${group}`}
          className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 text-sm placeholder:text-slate-400 focus:outline-none focus:border-[#002FA7]"
        />
        <button
          onClick={add}
          data-testid={`keyword-add-${group}`}
          className="inline-flex items-center gap-1 bg-slate-900 hover:bg-slate-800 text-white px-3 py-2 text-sm font-semibold"
        >
          <Plus className="w-3.5 h-3.5" /> Add
        </button>
      </div>
    </div>
  );
}

export default function KeywordManager({ keywords, onChange }) {
  const groups = Object.keys(keywords);
  return (
    <div className="space-y-5" data-testid="keywords-panel">
      {groups.map((g) => (
        <KeywordGroup
          key={g}
          group={g}
          values={keywords[g]}
          onChange={(next) => onChange({ ...keywords, [g]: next })}
        />
      ))}
    </div>
  );
}

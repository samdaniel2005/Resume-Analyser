import { FileText, X, Loader2 } from "lucide-react";

export default function FileList({ entries, busy, onSubmit, onRemove }) {
  return (
    <div className="bg-white border border-black/5 mt-6" data-testid="selected-files">
      <div className="px-6 py-4 border-b border-black/5 flex items-center justify-between">
        <div>
          <div className="text-[10.5px] tracking-[0.22em] uppercase font-bold text-slate-500">Ready to score</div>
          <div className="font-display text-lg font-bold text-slate-950 mt-1">
            {entries.length} file{entries.length > 1 ? "s" : ""} queued
          </div>
        </div>
        <button
          onClick={onSubmit}
          disabled={busy}
          data-testid="start-scoring-button"
          className="inline-flex items-center gap-2 bg-[#002FA7] hover:bg-[#00227A] text-white px-5 py-2.5 text-sm font-semibold transition-colors disabled:opacity-60"
        >
          {busy ? <><Loader2 className="w-4 h-4 animate-spin" /> Scoring…</> : "Start scoring"}
        </button>
      </div>
      <div className="divide-y divide-black/5">
        {entries.map(({ id, file }) => (
          <div key={id} className="flex items-center gap-3 px-6 py-3" data-testid={`file-row-${id}`}>
            <FileText className="w-4 h-4 text-slate-400" strokeWidth={1.5} />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-slate-900 truncate">{file.name}</div>
              <div className="text-[11.5px] text-slate-500">{(file.size / 1024).toFixed(1)} KB</div>
            </div>
            <button
              onClick={() => onRemove(id)}
              data-testid={`remove-file-${id}`}
              className="text-slate-400 hover:text-rose-600 transition-colors"
              aria-label="Remove file"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

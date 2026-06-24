export default function PageHeader({ overline, title, description, actions, testId }) {
  return (
    <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8" data-testid={testId}>
      <div>
        {overline && (
          <div className="text-[11px] tracking-[0.22em] uppercase font-bold text-slate-500 mb-3">{overline}</div>
        )}
        <h1 className="font-display text-3xl sm:text-4xl tracking-tight font-black text-slate-950 leading-[1.05]">{title}</h1>
        {description && (
          <p className="text-[14.5px] text-slate-600 mt-2.5 max-w-2xl leading-relaxed">{description}</p>
        )}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

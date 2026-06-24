import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Users, Upload, Settings as SettingsIcon, Activity } from "lucide-react";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, testId: "nav-dashboard" },
  { to: "/candidates", label: "Candidates", icon: Users, testId: "nav-candidates" },
  { to: "/upload", label: "Upload", icon: Upload, testId: "nav-upload" },
  { to: "/settings", label: "Settings", icon: SettingsIcon, testId: "nav-settings" },
];

export default function AppLayout() {
  return (
    <div className="min-h-screen flex" data-testid="app-shell">
      {/* Sidebar */}
      <aside
        className="hidden md:flex md:flex-col w-60 shrink-0 bg-white border-r border-black/5"
        data-testid="sidebar"
      >
        <div className="px-6 pt-7 pb-8">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-[#002FA7] flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <div className="font-display font-black tracking-tight text-[17px] leading-none text-slate-950">SignalRank</div>
              <div className="text-[10px] tracking-[0.18em] uppercase font-bold text-slate-400 mt-1">Resume Intelligence</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 px-3 space-y-0.5">
          {navItems.map(({ to, label, icon: Icon, testId }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              data-testid={testId}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 text-[13.5px] font-medium transition-colors ${
                  isActive
                    ? "bg-[#002FA7] text-white"
                    : "text-slate-600 hover:text-slate-950 hover:bg-slate-50"
                }`
              }
            >
              <Icon className="w-4 h-4" strokeWidth={1.75} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="px-6 py-5 border-t border-black/5">
          <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400 font-bold">v1.0 · OCR Engine</div>
          <div className="text-xs text-slate-500 mt-1.5 leading-relaxed">Tesseract + weighted heuristics across 8 categories.</div>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        {/* Mobile top bar */}
        <div className="md:hidden bg-white border-b border-black/5 px-4 py-3 flex items-center gap-2">
          <div className="w-7 h-7 bg-[#002FA7] flex items-center justify-center">
            <Activity className="w-3.5 h-3.5 text-white" strokeWidth={2.5} />
          </div>
          <div className="font-display font-black tracking-tight text-base text-slate-950">SignalRank</div>
        </div>
        <Outlet />
      </main>
    </div>
  );
}

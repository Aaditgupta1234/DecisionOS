import React from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Brain,
  FileCheck2,
  GitFork,
  HelpCircle,
  Layers,
  Lightbulb,
  LineChart,
  MessageSquare,
  Sparkles,
} from 'lucide-react';
import { WorkspaceStatistics } from '../../../types/dashboard';

interface SectionNavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  count?: number;
  badgeColor?: string;
}

interface DashboardSidebarProps {
  activeSection: string;
  onSelectSection: (sectionId: string) => void;
  stats?: WorkspaceStatistics;
}

export const DashboardSidebar: React.FC<DashboardSidebarProps> = ({
  activeSection,
  onSelectSection,
  stats,
}) => {
  const sections: SectionNavItem[] = [
    { id: 'overview', label: 'Executive Scorecard', icon: Activity },
    { id: 'kpis', label: 'Key Performance Indicators', icon: BarChart3, count: stats?.metrics_count },
    { id: 'findings', label: 'Diagnostic Findings', icon: AlertTriangle, count: stats?.findings_count, badgeColor: 'bg-rose-500/20 text-rose-300' },
    { id: 'root_causes', label: 'Root Cause Chains', icon: GitFork, count: stats?.root_causes_count, badgeColor: 'bg-amber-500/20 text-amber-300' },
    { id: 'recommendations', label: 'Strategic Matrix', icon: Lightbulb, count: stats?.recommendations_count, badgeColor: 'bg-emerald-500/20 text-emerald-300' },
    { id: 'forecasts', label: 'Predictive Forecasts', icon: LineChart, count: stats?.forecasts_count },
    { id: 'scenarios', label: 'Scenario Simulations', icon: Layers, count: stats?.scenarios_count },
    { id: 'narratives', label: 'AI Executive Briefings', icon: Sparkles },
    { id: 'insights', label: 'Strategic Themes', icon: Brain },
    { id: 'reports', label: 'Boardroom Reports', icon: FileCheck2, count: stats?.reports_count },
    { id: 'chat', label: 'AI Decision Copilot', icon: MessageSquare },
  ];

  return (
    <aside className="w-64 shrink-0 hidden lg:block sticky top-24 h-[calc(100vh-7rem)] overflow-y-auto pr-3 scrollbar-thin scrollbar-thumb-slate-800">
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800/80 rounded-2xl p-3 shadow-lg">
        <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Executive Navigator
        </div>
        <nav className="mt-1 space-y-1">
          {sections.map((sec) => {
            const Icon = sec.icon;
            const isActive = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => onSelectSection(sec.id)}
                className={`w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon
                    className={`w-4 h-4 shrink-0 ${
                      isActive ? 'text-cyan-400' : 'text-slate-500'
                    }`}
                  />
                  <span className="truncate">{sec.label}</span>
                </div>
                {sec.count !== undefined && sec.count > 0 && (
                  <span
                    className={`px-1.5 py-0.5 text-[10px] font-semibold rounded-md ${
                      sec.badgeColor || 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {sec.count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
};

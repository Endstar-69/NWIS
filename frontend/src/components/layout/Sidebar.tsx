import React from 'react';
import {
  LayoutDashboard, Activity, Map, Columns, BookOpen, Bot,
  FileText, LineChart, BellRing, Server
} from 'lucide-react';
import { useTheme } from '../../store/themeContext';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

interface NavSection {
  title: string;
  items: {
    id: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: string | null;
  }[];
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const navSections: NavSection[] = [
    {
      title: 'OVERVIEW',
      items: [
        { id: 'dashboard', label: 'Main Dashboard', icon: LayoutDashboard, badge: null }
      ]
    },
    {
      title: 'OPERATIONS',
      items: [
        { id: 'active-well', label: 'Active Well', icon: Activity, badge: 'LIVE' },
        { id: 'map', label: 'Nearby Wells Map', icon: Map, badge: null },
        { id: 'comparison', label: 'Well Comparison', icon: Columns, badge: null }
      ]
    },
    {
      title: 'KNOWLEDGE BASE',
      items: [
        { id: 'knowledge-repo', label: 'Event Knowledge Base', icon: BookOpen, badge: null },
        { id: 'assistant', label: 'AI Search / Assistant', icon: Bot, badge: 'RAG' },
        { id: 'documents', label: 'Document Intelligence', icon: FileText, badge: 'OCR/NLP' }
      ]
    },
    {
      title: 'ANALYTICS & SAFETY',
      items: [
        { id: 'risk-analytics', label: 'ML Risk Analytics', icon: LineChart, badge: '3 MODELS' },
        { id: 'alerts', label: 'Alerts Center', icon: BellRing, badge: null }
      ]
    },
    {
      title: 'SYSTEM',
      items: [
        { id: 'system-status', label: 'System Status', icon: Server, badge: null }
      ]
    }
  ];

  return (
    <aside className={`w-64 h-full ${
      isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200'
    } border-r flex flex-col justify-between py-3 shrink-0 select-none transition-colors overflow-y-auto`}>
      <div className="space-y-4 px-2.5">
        {navSections.map((section) => (
          <div key={section.title} className="space-y-0.5">
            <div className={`px-3 py-1 text-[10px] font-sans font-semibold uppercase tracking-wider ${
              isDark ? 'text-slate-500' : 'text-slate-400'
            }`}>
              {section.title}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-sans font-medium transition-all group ${
                    isActive
                      ? (isDark
                          ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 font-semibold'
                          : 'bg-sky-50 text-sky-700 border border-sky-200 font-semibold shadow-xs')
                      : (isDark
                          ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 border border-transparent')
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className={`w-4 h-4 shrink-0 transition-colors ${
                      isActive
                        ? (isDark ? 'text-sky-400' : 'text-sky-600')
                        : (isDark ? 'text-slate-500 group-hover:text-slate-300' : 'text-slate-400 group-hover:text-slate-600')
                    }`} />
                    <span className="truncate">{item.label}</span>
                  </div>

                  {item.badge && (
                    item.badge === 'LIVE' ? (
                      <span className="flex items-center gap-1 text-[9px] px-1.5 py-0.2 rounded font-sans font-bold tracking-tight bg-rose-500/15 text-rose-500 dark:text-rose-400 border border-rose-500/30">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-500 inline-block animate-pulse" />
                        LIVE
                      </span>
                    ) : (
                      <span className={`text-[9px] px-1.5 py-0.2 rounded font-sans font-semibold tracking-tight ${
                        isActive
                          ? (isDark ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30' : 'bg-sky-100 text-sky-700 border border-sky-300')
                          : (isDark ? 'bg-slate-800/80 text-slate-400 border border-slate-700/50' : 'bg-slate-100 text-slate-600 border border-slate-200')
                      }`}>
                        {item.badge}
                      </span>
                    )
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer / Rig Context Indicator */}
      <div className={`mx-2.5 mt-4 px-3 py-2.5 rounded-lg ${
        isDark ? 'bg-slate-900/50 border border-slate-800/80 text-slate-400' : 'bg-slate-50 border border-slate-200 text-slate-600'
      } text-[11px] font-sans space-y-1`}>
        <div className="flex items-center justify-between">
          <span className="font-semibold text-xs text-slate-300 dark:text-slate-300">eRTMAC System</span>
          <span className="inline-flex items-center gap-1 text-[10px] text-emerald-500 font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
            ONLINE
          </span>
        </div>
        <p className={`text-[10px] ${isDark ? 'text-slate-500' : 'text-slate-400'} leading-tight`}>
          Assam-Arakan Basin Drilling Support
        </p>
      </div>
    </aside>
  );
};

import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useTheme } from '../store/themeContext';
import { DrillingEvent, Formation } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import { BookOpen, Search, Filter, Layers, FileText, ChevronRight, X } from 'lucide-react';

export const KnowledgeRepoPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [events, setEvents] = useState<DrillingEvent[]>([]);
  const [formations, setFormations] = useState<Formation[]>([]);
  const [selectedFormation, setSelectedFormation] = useState<string>('');
  const [selectedEventType, setSelectedEventType] = useState<string>('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [activeModalEvent, setActiveModalEvent] = useState<DrillingEvent | null>(null);

  useEffect(() => {
    api.getFormations().then(setFormations).catch(console.error);
    fetchEvents();
  }, [selectedFormation, selectedEventType, selectedSeverity]);

  const fetchEvents = () => {
    api.getEvents({
      formation: selectedFormation || undefined,
      event_type: selectedEventType || undefined,
      severity: selectedSeverity || undefined
    }).then(setEvents).catch(console.error);
  };

  const filteredEvents = events.filter((ev) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      ev.cause.toLowerCase().includes(q) ||
      ev.mitigation.toLowerCase().includes(q) ||
      ev.lesson_learned.toLowerCase().includes(q) ||
      ev.event_type.toLowerCase().includes(q) ||
      ev.formation.toLowerCase().includes(q) ||
      (ev.well_name && ev.well_name.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-4 pb-10">
      {/* Header & Stats */}
      <div className={`p-4 rounded-lg border transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <BookOpen className="w-3.5 h-3.5 text-sky-500" />
            <span className="text-[11px] font-sans text-sky-600 dark:text-sky-400 font-semibold uppercase tracking-wider">
              Institutional Memory Knowledge Base
            </span>
          </div>
          <h1 className="text-xl font-bold font-sans text-slate-900 dark:text-white tracking-tight">
            Drilling Event Knowledge Repository
          </h1>
        </div>

        <div className="flex items-center gap-2 font-sans text-xs">
          <Badge variant="primary" size="md">{filteredEvents.length} Structured Records</Badge>
          <Badge variant="warning" size="md">Assam-Arakan Basin</Badge>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className={`p-3 rounded-lg border grid grid-cols-1 md:grid-cols-4 gap-2.5 font-sans text-xs ${
        isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200 shadow-xs'
      }`}>
        {/* Search Input */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search cause, mitigation, lesson..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={`w-full rounded-md pl-8 pr-3 py-1.5 text-xs transition border focus:outline-none focus:border-sky-500 ${
              isDark
                ? 'bg-slate-900/80 border-slate-700/80 text-white placeholder-slate-500'
                : 'bg-slate-50 border-slate-200 text-slate-900 placeholder-slate-400'
            }`}
          />
        </div>

        {/* Formation Filter */}
        <select
          value={selectedFormation}
          onChange={(e) => setSelectedFormation(e.target.value)}
          className={`rounded-md px-2.5 py-1.5 text-xs transition border focus:outline-none focus:border-sky-500 ${
            isDark
              ? 'bg-slate-900/80 border-slate-700/80 text-slate-200'
              : 'bg-slate-50 border-slate-200 text-slate-700'
          }`}
        >
          <option value="">All Geological Horizons</option>
          {formations.map((f) => (
            <option key={f.formation_id} value={f.formation_name}>{f.formation_name}</option>
          ))}
        </select>

        {/* Event Type Filter */}
        <select
          value={selectedEventType}
          onChange={(e) => setSelectedEventType(e.target.value)}
          className={`rounded-md px-2.5 py-1.5 text-xs transition border focus:outline-none focus:border-sky-500 ${
            isDark
              ? 'bg-slate-900/80 border-slate-700/80 text-slate-200'
              : 'bg-slate-50 border-slate-200 text-slate-700'
          }`}
        >
          <option value="">All Incident Types</option>
          <option value="MUD_LOSS">Mud Loss / Lost Circulation</option>
          <option value="STUCK_PIPE">Stuck Pipe / Differential</option>
          <option value="KICK">Kick / Gas Influx</option>
          <option value="TORQUE_SPIKE">Torque Spike / Tight Hole</option>
          <option value="PACK_OFF">Pack-Off / Bridging</option>
          <option value="CEMENTING_ISSUE">Cementing & Zonal Isolation</option>
        </select>

        {/* Severity Filter */}
        <select
          value={selectedSeverity}
          onChange={(e) => setSelectedSeverity(e.target.value)}
          className={`rounded-md px-2.5 py-1.5 text-xs transition border focus:outline-none focus:border-sky-500 ${
            isDark
              ? 'bg-slate-900/80 border-slate-700/80 text-slate-200'
              : 'bg-slate-50 border-slate-200 text-slate-700'
          }`}
        >
          <option value="">All Severity Levels</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {/* Events Card Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {filteredEvents.map((ev) => (
          <div
            key={ev.event_id}
            onClick={() => setActiveModalEvent(ev)}
            className={`p-4 rounded-lg border transition cursor-pointer flex flex-col justify-between ${
              isDark
                ? 'bg-[#0B111E] border-slate-800 hover:border-slate-700 hover:bg-slate-900/40'
                : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50 shadow-xs'
            }`}
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className="font-semibold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-500"></span>
                  {ev.well_name || ev.well_id}
                </span>
                <RiskPill level={ev.severity} />
              </div>

              <div className="text-xs font-medium text-amber-600 dark:text-amber-400 mb-0.5">
                {ev.event_type.replace('_', ' ')} @ <span className="font-mono">{ev.start_depth} m</span>
              </div>

              <div className="text-[11px] text-slate-500 dark:text-slate-400 mb-1.5">
                Horizon: <span className="text-slate-700 dark:text-slate-300 font-medium">{ev.formation}</span>
              </div>

              <p className="text-xs text-slate-600 dark:text-slate-300 font-sans line-clamp-2 leading-relaxed">
                {ev.cause}
              </p>
            </div>

            <div className={`mt-3 pt-2.5 border-t ${isDark ? 'border-slate-800/80' : 'border-slate-100'} flex items-center justify-between text-[11px] text-slate-400`}>
              <span className="truncate max-w-[150px]">Doc: {ev.source_document}</span>
              <span className="text-sky-600 dark:text-sky-400 font-medium">Details &bull; p.{ev.source_page}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Detail Modal */}
      {activeModalEvent && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className={`max-w-2xl w-full rounded-lg p-5 shadow-xl space-y-3.5 max-h-[90vh] overflow-y-auto font-sans text-xs border ${
            isDark ? 'bg-[#0F172A] border-slate-700 text-slate-200' : 'bg-white border-slate-200 text-slate-800'
          }`}>
            <div className={`flex items-center justify-between border-b pb-2.5 ${isDark ? 'border-slate-800' : 'border-slate-100'}`}>
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span>{activeModalEvent.well_name || activeModalEvent.well_id}</span>
                  <RiskPill level={activeModalEvent.severity} />
                </h3>
                <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
                  {activeModalEvent.event_type} &bull; Depth: <span className="font-mono">{activeModalEvent.start_depth} m</span> ({activeModalEvent.formation})
                </p>
              </div>
              <button
                onClick={() => setActiveModalEvent(null)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="space-y-2.5 text-xs">
              <div>
                <div className="text-[10px] font-semibold text-amber-600 dark:text-amber-400 uppercase mb-1">Observed Cause:</div>
                <div className={`p-2.5 rounded-md border leading-relaxed ${
                  isDark ? 'bg-slate-900 border-slate-800 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'
                }`}>
                  {activeModalEvent.cause}
                </div>
              </div>

              <div>
                <div className="text-[10px] font-semibold text-sky-600 dark:text-sky-400 uppercase mb-1">Operational Impact:</div>
                <div className={`p-2.5 rounded-md border leading-relaxed ${
                  isDark ? 'bg-slate-900 border-slate-800 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'
                }`}>
                  {activeModalEvent.impact}
                </div>
              </div>

              <div>
                <div className="text-[10px] font-semibold text-emerald-600 dark:text-emerald-400 uppercase mb-1">Recorded Mitigation:</div>
                <div className={`p-2.5 rounded-md border leading-relaxed ${
                  isDark ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300' : 'bg-emerald-50 border-emerald-200 text-emerald-900'
                }`}>
                  {activeModalEvent.mitigation}
                </div>
              </div>

              <div>
                <div className="text-[10px] font-semibold text-purple-600 dark:text-purple-400 uppercase mb-1">Institutional Lesson Learned:</div>
                <div className={`p-2.5 rounded-md border leading-relaxed ${
                  isDark ? 'bg-purple-950/20 border-purple-800/40 text-purple-300' : 'bg-purple-50 border-purple-200 text-purple-900'
                }`}>
                  {activeModalEvent.lesson_learned}
                </div>
              </div>

              <div className={`text-[11px] text-slate-400 pt-2 border-t flex items-center justify-between ${
                isDark ? 'border-slate-800' : 'border-slate-100'
              }`}>
                <span>Source Document: <b className="text-slate-700 dark:text-slate-300">{activeModalEvent.source_document}</b> (p.{activeModalEvent.source_page})</span>
                <span>Confidence: <b className="font-mono text-emerald-600 dark:text-emerald-400">{(activeModalEvent.confidence * 100).toFixed(0)}%</b></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

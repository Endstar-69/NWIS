import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useTheme } from '../store/themeContext';
import { Well } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import { Columns, Plus, X, Layers, Check, ShieldAlert } from 'lucide-react';

export const WellComparisonPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [allWells, setAllWells] = useState<Well[]>([]);
  const [selectedWellIds, setSelectedWellIds] = useState<string[]>(['WELL-001', 'WELL-002', 'WELL-003']);
  const [comparisonData, setComparisonData] = useState<any[]>([]);

  useEffect(() => {
    api.getWells().then(setAllWells).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedWellIds.length > 0) {
      api.compareWells(selectedWellIds).then(setComparisonData).catch(console.error);
    }
  }, [selectedWellIds]);

  const toggleWellSelection = (id: string) => {
    if (selectedWellIds.includes(id)) {
      if (selectedWellIds.length > 1) {
        setSelectedWellIds(selectedWellIds.filter((w) => w !== id));
      }
    } else {
      if (selectedWellIds.length < 4) {
        setSelectedWellIds([...selectedWellIds, id]);
      }
    }
  };

  return (
    <div className="space-y-4 pb-10">
      {/* Top Header & Selector Chips */}
      <div className={`p-4 rounded-lg border transition-colors space-y-3 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-1.5 mb-0.5">
              <Columns className="w-3.5 h-3.5 text-sky-500" />
              <span className="text-[11px] font-sans text-sky-600 dark:text-sky-400 font-semibold uppercase tracking-wider">
                Multi-Well Correlation Module
              </span>
            </div>
            <h1 className="text-xl font-bold font-sans text-slate-900 dark:text-white tracking-tight">
              Stratigraphic & Offset Well Comparison
            </h1>
          </div>

          <div className="text-xs font-sans text-slate-500 dark:text-slate-400">
            Comparing <span className="font-mono font-bold text-sky-600 dark:text-sky-400">{selectedWellIds.length}</span> of 4 wells
          </div>
        </div>

        {/* Well Selection Pills */}
        <div className={`flex flex-wrap gap-1.5 pt-2.5 border-t ${isDark ? 'border-slate-800' : 'border-slate-100'}`}>
          {allWells.slice(0, 12).map((w) => {
            const isSelected = selectedWellIds.includes(w.well_id);
            return (
              <button
                key={w.well_id}
                onClick={() => toggleWellSelection(w.well_id)}
                className={`px-2.5 py-1 rounded text-xs font-sans transition flex items-center gap-1.5 border ${
                  isSelected
                    ? 'bg-sky-500/10 border-sky-500 text-sky-600 dark:text-sky-300 font-semibold'
                    : (isDark
                        ? 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700'
                        : 'bg-slate-50 border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-100')
                }`}
              >
                {isSelected ? <Check className="w-3.5 h-3.5 text-sky-500" /> : <Plus className="w-3.5 h-3.5 text-slate-400" />}
                <span>{w.well_name}</span>
                {w.is_active_well && <span className="text-[9px] font-mono bg-sky-500/20 px-1 py-0.2 rounded text-sky-600 dark:text-sky-400">ACTIVE</span>}
              </button>
            );
          })}
        </div>
      </div>

      {/* Side-by-Side Stratigraphic & Drilling Program Columns */}
      <div className={`grid grid-cols-1 md:grid-cols-${Math.max(1, Array.isArray(comparisonData) ? comparisonData.length : 1)} gap-4`}>
        {Array.isArray(comparisonData) && comparisonData.map((item, idx) => {
          const w = item.well || item;
          const wellId = w.well_id || `comp-${idx}`;
          const wellName = w.well_name || wellId;
          const casings = Array.isArray(item.casing) ? item.casing : [];
          const events = Array.isArray(item.events_summary) ? item.events_summary : [];

          return (
            <Card
              key={wellId}
              className={`border-t-2 ${w.is_active_well ? 'border-t-sky-500' : 'border-t-slate-400 dark:border-t-slate-700'}`}
              title={wellName}
              subtitle={`${w.field || 'Assam'} Field (${w.well_type || 'Development'})`}
              headerAction={
                w.is_active_well ? (
                  <Badge variant="primary">ACTIVE RIG</Badge>
                ) : (
                  <button
                    onClick={() => toggleWellSelection(wellId)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-0.5"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )
              }
            >
              <div className="space-y-3 font-sans text-xs">
                {/* General KPI stats */}
                <div className={`grid grid-cols-2 gap-2 p-2.5 rounded-md border text-[11px] ${
                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <div>Target Depth: <b className="font-mono text-slate-900 dark:text-white">{w.target_depth ?? 'N/A'} m</b></div>
                  <div>Current: <b className="font-mono text-emerald-600 dark:text-emerald-400">{w.current_depth ?? 'N/A'} m</b></div>
                  <div>Status: <b className="text-slate-700 dark:text-slate-300">{w.status || 'Completed'}</b></div>
                  <div>NPT Recorded: <b className="font-mono text-amber-600 dark:text-amber-400">{item.total_npt_hours ?? 0} hrs</b></div>
                </div>

                {/* Casing Program Summary */}
                <div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold tracking-wider mb-1.5 flex items-center gap-1.5">
                    <Layers className="w-3 h-3 text-sky-500" /> Casing Strings
                  </div>
                  <div className="space-y-1">
                    {casings.map((cs: any, cIdx: number) => (
                      <div key={cs.id || cIdx} className={`p-2 rounded-md border flex items-center justify-between text-[11px] ${
                        isDark ? 'bg-slate-900/40 border-slate-800' : 'bg-white border-slate-200 shadow-xs'
                      }`}>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">{cs.casing_type}</span>
                        <span className="text-slate-500 dark:text-slate-400">{cs.casing_size}" @ <b className="font-mono text-sky-600 dark:text-sky-400">{cs.shoe_depth} m</b></span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Historical Events & Mitigations */}
                <div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase font-semibold tracking-wider mb-1.5 flex items-center gap-1.5">
                    <ShieldAlert className="w-3 h-3 text-amber-500" /> Historical Incidents ({events.length})
                  </div>
                  <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
                    {events.map((ev: any, i: number) => (
                      <div key={i} className={`p-2 rounded-md border text-[11px] ${
                        isDark ? 'bg-slate-900/40 border-slate-800' : 'bg-white border-slate-200 shadow-xs'
                      }`}>
                        <div className="flex items-center justify-between font-semibold text-slate-900 dark:text-white mb-0.5">
                          <span className="text-amber-600 dark:text-amber-400">{ev.event_type}</span>
                          <span className="font-mono text-sky-600 dark:text-sky-400">{ev.depth} m</span>
                        </div>
                        <p className="text-[10px] text-slate-600 dark:text-slate-400 truncate">{ev.mitigation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

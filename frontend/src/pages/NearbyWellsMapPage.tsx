import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWell } from '../store/wellContext';
import { useTheme } from '../store/themeContext';
import { NearbyWell } from '../types';
import { WellMap } from '../components/map/WellMap';
import { Card } from '../components/common/Card';
import { RiskPill } from '../components/common/RiskPill';
import { Sliders, Compass, Maximize2, Minimize2, X, ChevronRight } from 'lucide-react';

export const NearbyWellsMapPage: React.FC = () => {
  const { activeWell } = useWell();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [radiusKm, setRadiusKm] = useState<number>(25);
  const [nearbyWells, setNearbyWells] = useState<NearbyWell[]>([]);
  const [selectedWell, setSelectedWell] = useState<NearbyWell | null>(null);
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [isFullMap, setIsFullMap] = useState<boolean>(false);
  const [showDrawer, setShowDrawer] = useState<boolean>(true);

  useEffect(() => {
    if (activeWell) {
      api.getNearbyWells(activeWell.well_id, radiusKm).then((res) => {
        setNearbyWells(res);
        if (res.length > 0 && !selectedWell) {
          setSelectedWell(res[0]);
        }
      }).catch(console.error);
    }
  }, [activeWell, radiusKm]);

  const filteredWells = nearbyWells.filter((item) => {
    if (riskFilter === 'ALL') return true;
    return item.risk_level === riskFilter;
  });

  return (
    <div className="space-y-4 pb-8 max-w-[1700px] mx-auto">
      {/* Top Header & Geospatial Control Bar */}
      <div className={`p-4 rounded-lg border transition-colors flex flex-col lg:flex-row lg:items-center justify-between gap-4 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <Compass className="w-3.5 h-3.5 text-sky-500" />
            <span className="text-[11px] font-sans text-sky-600 dark:text-sky-400 font-semibold uppercase tracking-wider">
              Geospatial Offset Correlation Engine
            </span>
          </div>
          <h1 className="text-xl font-bold font-sans text-slate-900 dark:text-white tracking-tight">
            Nearby Wells Intelligence Map
          </h1>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Radius Selector Pills */}
          <div className={`flex items-center gap-1 p-1 rounded-md border text-xs font-sans ${
            isDark ? 'bg-slate-900/80 border-slate-700/80' : 'bg-slate-50 border-slate-200'
          }`}>
            <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 px-1.5 uppercase">Radius:</span>
            {[1, 5, 10, 25, 50, 75].map((r) => (
              <button
                key={r}
                onClick={() => setRadiusKm(r)}
                className={`px-2 py-1 rounded text-xs font-sans transition ${
                  radiusKm === r
                    ? 'bg-sky-600 text-white font-semibold shadow-xs'
                    : (isDark ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200')
                }`}
              >
                {r} km
              </button>
            ))}
          </div>

          {/* Expand Full Map Toggle */}
          <button
            onClick={() => setIsFullMap(!isFullMap)}
            className={`px-3 py-1.5 rounded-md border font-sans text-xs font-medium flex items-center gap-1.5 transition ${
              isFullMap
                ? 'bg-amber-600 text-white border-amber-500'
                : (isDark
                    ? 'bg-slate-900 text-slate-300 border-slate-700 hover:text-white hover:bg-slate-800'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:text-slate-900 hover:bg-slate-100')
            }`}
          >
            {isFullMap ? (
              <>
                <Minimize2 className="w-3.5 h-3.5" />
                <span>Standard View</span>
              </>
            ) : (
              <>
                <Maximize2 className="w-3.5 h-3.5" />
                <span>Full Map</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Layout: Responsive Grid */}
      <div className={`grid gap-4 transition-all duration-300 ${
        isFullMap ? 'grid-cols-1' : 'grid-cols-1 xl:grid-cols-4'
      }`}>
        {/* Map Area */}
        <div className={`relative ${isFullMap ? 'w-full' : 'xl:col-span-3'} space-y-3`}>
          <div className={`${isFullMap ? 'h-[calc(100vh-200px)] min-h-[650px]' : 'h-[650px]'} w-full rounded-lg overflow-hidden border ${
            isDark ? 'border-slate-800' : 'border-slate-200'
          }`}>
            <WellMap
              activeWell={activeWell}
              nearbyWells={filteredWells}
              radiusKm={radiusKm}
              onSelectWell={(w) => {
                const found = nearbyWells.find((n) => n.well.well_id === w.well_id);
                if (found) {
                  setSelectedWell(found);
                  setShowDrawer(true);
                }
              }}
            />
          </div>

          {/* Floating Inspector Drawer in Full-Screen Mode */}
          {isFullMap && showDrawer && selectedWell && (
            <div className={`absolute top-3 right-3 z-[1000] w-80 max-h-[85%] ${
              isDark ? 'bg-[#0B111E]/95 border-slate-700 text-slate-200' : 'bg-white/95 border-slate-200 text-slate-800'
            } border rounded-lg shadow-xl backdrop-blur-md p-4 font-sans text-xs overflow-y-auto space-y-3 pointer-events-auto`}>
              <div className={`flex items-center justify-between border-b ${isDark ? 'border-slate-800' : 'border-slate-100'} pb-2`}>
                <div className="font-bold text-sm text-slate-900 dark:text-white">{selectedWell.well.well_name}</div>
                <div className="flex items-center gap-2">
                  <RiskPill level={selectedWell.risk_level} />
                  <button onClick={() => setShowDrawer(false)} className="text-slate-400 hover:text-slate-200">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className={`p-3 rounded-md space-y-1 ${
                isDark ? 'bg-sky-950/30 border-sky-800/40 text-slate-300' : 'bg-sky-50 border-sky-200 text-slate-800'
              } border`}>
                <div className="text-[10px] text-sky-600 dark:text-sky-400 font-semibold uppercase">Multi-Factor Similarity</div>
                <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">{selectedWell.similarity_score}% Match</div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                  Distance: <span className="font-mono text-slate-700 dark:text-slate-300">{selectedWell.distance_km} km</span>
                </div>
                <div className="text-[11px] text-slate-500 dark:text-slate-400">
                  Total Depth: <span className="font-mono text-slate-700 dark:text-slate-300">{selectedWell.well.target_depth} m</span>
                </div>
              </div>

              <div className="space-y-1 text-xs text-slate-700 dark:text-slate-300">
                <div>Field: <b>{selectedWell.well.field}</b></div>
                <div>Past Incidents: <b className="text-amber-600 dark:text-amber-400 font-mono">{selectedWell.historical_events_count} events</b></div>
                <div>Status: <b>{selectedWell.well.status}</b></div>
              </div>
            </div>
          )}

          {/* Configurable Prototype Weighting Bar */}
          <div className={`p-3 rounded-lg border text-xs font-sans flex flex-wrap items-center justify-between gap-3 ${
            isDark ? 'bg-[#0B111E] border-slate-800 text-slate-400' : 'bg-white border-slate-200 text-slate-600 shadow-xs'
          }`}>
            <div className="flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-sky-500" />
              <span className="font-semibold text-slate-800 dark:text-slate-200">Similarity Weights:</span>
            </div>
            <div className="flex items-center gap-4 text-[11px] font-sans">
              <span>Distance: <b className="font-mono text-sky-600 dark:text-sky-400">30%</b></span>
              <span>Formation: <b className="font-mono text-sky-600 dark:text-sky-400">25%</b></span>
              <span>Depth: <b className="font-mono text-sky-600 dark:text-sky-400">15%</b></span>
              <span>Reservoir: <b className="font-mono text-sky-600 dark:text-sky-400">15%</b></span>
              <span>Events: <b className="font-mono text-sky-600 dark:text-sky-400">10%</b></span>
            </div>
          </div>
        </div>

        {/* Sidebar Panel (Visible in Standard mode) */}
        {!isFullMap && (
          <div className="space-y-3">
            {/* Risk Filter Chips */}
            <div className={`flex items-center gap-1 p-1 rounded-md border text-xs font-sans overflow-x-auto ${
              isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200 shadow-xs'
            }`}>
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setRiskFilter(lvl)}
                  className={`px-2 py-1 rounded text-[11px] font-sans transition ${
                    riskFilter === lvl
                      ? 'bg-sky-600 text-white font-semibold shadow-xs'
                      : (isDark ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>

            {/* Selected Well Detail Card */}
            {selectedWell && (
              <Card
                title={selectedWell.well.well_name}
                subtitle={`${selectedWell.well.field} Field (${selectedWell.distance_km} km away)`}
                headerAction={<RiskPill level={selectedWell.risk_level} />}
              >
                <div className="space-y-3 font-sans text-xs">
                  <div className={`p-3 rounded-md border ${
                    isDark ? 'bg-sky-950/20 border-sky-800/40 text-slate-200' : 'bg-sky-50 border-sky-200 text-slate-800'
                  }`}>
                    <div className="text-[10px] text-sky-600 dark:text-sky-400 uppercase font-semibold">Similarity Breakdown</div>
                    <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-0.5">{selectedWell.similarity_score}% Match</div>
                    <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] text-slate-600 dark:text-slate-400">
                      <div>Distance: <b className="font-mono text-slate-900 dark:text-white">{(selectedWell.similarity_breakdown.distance_score * 100).toFixed(0)}%</b></div>
                      <div>Formation: <b className="font-mono text-slate-900 dark:text-white">{(selectedWell.similarity_breakdown.formation_score * 100).toFixed(0)}%</b></div>
                      <div>Depth Match: <b className="font-mono text-slate-900 dark:text-white">{(selectedWell.similarity_breakdown.depth_score * 100).toFixed(0)}%</b></div>
                      <div>Event Profile: <b className="font-mono text-slate-900 dark:text-white">{(selectedWell.similarity_breakdown.events_score * 100).toFixed(0)}%</b></div>
                    </div>
                  </div>

                  <div className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
                    <div>Target Depth: <b className="font-mono">{selectedWell.well.target_depth} m</b></div>
                    <div>Well Status: <b>{selectedWell.well.status}</b></div>
                    <div>Historical Incidents: <b className="font-mono text-amber-600 dark:text-amber-400">{selectedWell.historical_events_count} events</b></div>
                    <div>Formations: <span className="text-slate-500 dark:text-slate-400">{selectedWell.common_formations.slice(0, 3).join(', ')}</span></div>
                  </div>
                </div>
              </Card>
            )}

            {/* Scrollable Nearby Wells List */}
            <div className="space-y-1.5 max-h-[360px] overflow-y-auto pr-1">
              {filteredWells.map((item) => {
                const isSelected = selectedWell?.well.well_id === item.well.well_id;
                return (
                  <div
                    key={item.well.well_id}
                    onClick={() => setSelectedWell(item)}
                    className={`p-2.5 rounded-md border transition cursor-pointer flex items-center justify-between ${
                      isSelected
                        ? (isDark
                            ? 'bg-sky-500/10 border-sky-500/60'
                            : 'bg-sky-50 border-sky-400')
                        : (isDark
                            ? 'bg-[#0B111E] border-slate-800 hover:border-slate-700 hover:bg-slate-900/50'
                            : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50 shadow-xs')
                    }`}
                  >
                    <div>
                      <div className="font-semibold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                        <span>{item.well.well_name}</span>
                        <span className="text-[10px] font-mono text-sky-600 dark:text-sky-400">({item.distance_km} km)</span>
                      </div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        Similarity: <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400">{item.similarity_score}%</span> &bull; {item.historical_events_count} events
                      </div>
                    </div>
                    <RiskPill level={item.risk_level} />
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

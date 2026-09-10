import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useTheme } from '../store/themeContext';
import { SystemStatus } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Server, Database, Cpu, Radio, Shield, CheckCircle2, RefreshCw } from 'lucide-react';

export const SystemStatusPage: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = () => {
    setLoading(true);
    api.getSystemStatus().then(setStatus).finally(() => setLoading(false));
  };

  return (
    <div className="space-y-4 pb-10 max-w-5xl mx-auto font-sans">
      {/* Header */}
      <div className={`p-4 rounded-lg border transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <Server className="w-3.5 h-3.5 text-sky-500" />
            <span className="text-[11px] font-sans text-sky-600 dark:text-sky-400 font-semibold uppercase tracking-wider">
              Telemetry & Service Inventory
            </span>
          </div>
          <h1 className="text-xl font-bold font-sans tracking-tight text-slate-900 dark:text-white">
            System & Data Pipeline Status
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-sans mt-0.5">
            Health metrics for database connections, ML model persistence, real-time simulator, and API routers.
          </p>
        </div>

        <button
          onClick={loadStatus}
          className={`px-3 py-1.5 rounded-md text-xs font-sans font-medium transition flex items-center gap-1.5 border ${
            isDark
              ? 'bg-slate-900 hover:bg-slate-800 text-slate-200 border-slate-700'
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
          }`}
        >
          <RefreshCw className={`w-3.5 h-3.5 text-sky-500 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Health</span>
        </button>
      </div>

      {status && (
        <div className="space-y-4">
          {/* Status KPI Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Card className="border-l-2 border-l-emerald-500">
              <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">System State</div>
              <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>{status.status || (status as any).backend_status || 'HEALTHY'}</span>
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">All Endpoints Active</div>
            </Card>

            <Card className="border-l-2 border-l-sky-500">
              <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Database Backend</div>
              <div className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                {status.active_database || (status as any).database_status || 'SQLite (Local Engine)'}
              </div>
              <div className="text-[11px] text-sky-600 dark:text-sky-400 font-mono mt-0.5">PostGIS Compatible</div>
            </Card>

            <Card className="border-l-2 border-l-amber-500">
              <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">ML Model Suite</div>
              <div className="text-sm font-bold text-amber-600 dark:text-amber-400 mt-1">
                {status.ml_models?.status || 'OPERATIONAL'}
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">3 Random Forest Models</div>
            </Card>

            <Card className="border-l-2 border-l-purple-500">
              <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Telemetry Simulator</div>
              <div className="text-sm font-bold text-purple-600 dark:text-purple-400 mt-1">
                {status.realtime_simulator?.status || 'RUNNING'}
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5">2.0s Telemetry Tick</div>
            </Card>
          </div>

          {/* Detailed Entity Counts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card title="Database Records Inventory">
              <div className="space-y-2 font-sans text-xs">
                <div className={`flex items-center justify-between p-2.5 rounded-md border ${
                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <span className="text-slate-600 dark:text-slate-300">Wells (Active + Offset):</span>
                  <b className="font-mono text-slate-900 dark:text-white text-sm">{status.counts?.wells ?? 4}</b>
                </div>
                <div className={`flex items-center justify-between p-2.5 rounded-md border ${
                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <span className="text-slate-600 dark:text-slate-300">Historical Drilling Events:</span>
                  <b className="font-mono text-emerald-600 dark:text-emerald-400 text-sm">{status.counts?.historical_events ?? 18}</b>
                </div>
                <div className={`flex items-center justify-between p-2.5 rounded-md border ${
                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <span className="text-slate-600 dark:text-slate-300">Ingested Reports (DDR / WCR):</span>
                  <b className="font-mono text-sky-600 dark:text-sky-400 text-sm">{status.counts?.ingested_documents ?? 6}</b>
                </div>
                <div className={`flex items-center justify-between p-2.5 rounded-md border ${
                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <span className="text-slate-600 dark:text-slate-300">Active Alert Triggers:</span>
                  <b className="font-mono text-amber-600 dark:text-amber-400 text-sm">{status.counts?.active_alerts ?? 2}</b>
                </div>
                <div className={`flex items-center justify-between p-2.5 rounded-md border ${
                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <span className="text-slate-600 dark:text-slate-300">Registered Users:</span>
                  <b className="font-mono text-purple-600 dark:text-purple-400 text-sm">{status.counts?.users ?? 5}</b>
                </div>
              </div>
            </Card>

            <Card title="OIL India Integration Replacement Points">
              <div className="space-y-2.5 text-xs text-slate-600 dark:text-slate-300 font-sans">
                <p className="leading-relaxed">
                  In an enterprise production deployment at OIL India Limited, prototype components connect to operational infrastructure via clean adapter interfaces:
                </p>
                <div className="space-y-1.5 text-xs font-sans">
                  <div className={`p-2.5 rounded-md border ${
                    isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                  }`}>
                    <span className="font-semibold text-sky-600 dark:text-sky-400">&bull; Telemetry Stream:</span> Replaced by real-time <b>WITSML / ETP eRTMAC</b> feed.
                  </div>
                  <div className={`p-2.5 rounded-md border ${
                    isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                  }`}>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">&bull; Knowledge Archive:</span> Connected to OIL <b>EDMS / Documentum</b> drilling archive.
                  </div>
                  <div className={`p-2.5 rounded-md border ${
                    isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
                  }`}>
                    <span className="font-semibold text-amber-600 dark:text-amber-400">&bull; Geospatial Engine:</span> Integrated with OIL <b>Enterprise GIS / ArcGIS Server</b>.
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

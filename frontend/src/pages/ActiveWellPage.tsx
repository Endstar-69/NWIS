import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWell } from '../store/wellContext';
import { useAuth } from '../store/authContext';
import { useTheme } from '../store/themeContext';
import { Well, DrillingEvent, RiskPredictionResponse } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area
} from 'recharts';
import {
  Activity, Gauge, AlertTriangle, Layers, ShieldAlert,
  ArrowDown, ChevronRight, Zap, RefreshCw, CheckCircle2
} from 'lucide-react';

export const ActiveWellPage: React.FC = () => {
  const { activeWell, activeDepth, activeFormation, liveTelemetry: ctxTelemetry, liveRisk: ctxRisk } = useWell();
  const { user } = useAuth();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [telemetryHistory, setTelemetryHistory] = useState<any[]>([]);
  const [offsetEvents, setOffsetEvents] = useState<DrillingEvent[]>([]);

  // Default fallback telemetry if WebSocket has not yet ticked
  const liveTelemetry = ctxTelemetry || {
    depth: activeDepth || 3420.0,
    formation_name: activeFormation || 'Barail Sandstone',
    rop: 6.2,
    wob: 16.5,
    rpm: 105.0,
    torque: 18.5,
    standpipe_pressure: 2180.0,
    flow_rate: 1750.0,
    mud_weight: 1.28,
    ecd: 1.33,
    hook_load: 122.0
  };

  const liveRisk = ctxRisk;

  useEffect(() => {
    if (!activeWell) return;

    // 1. Fetch telemetry history for current active well
    api.getTelemetryHistory(activeWell.well_id, 35)
      .then(setTelemetryHistory)
      .catch(console.error);

    // 2. Fetch offset events dynamic to active formation and depth window
    api.getEvents({
      formation: activeFormation,
      min_depth: Math.max(0, activeDepth - 150),
      max_depth: activeDepth + 150
    })
      .then(setOffsetEvents)
      .catch(console.error);
  }, [activeWell?.well_id, activeFormation, activeDepth]);

  // Keep telemetry history moving as live points arrive
  useEffect(() => {
    if (ctxTelemetry) {
      setTelemetryHistory((prev) => {
        const updated = [...prev, ctxTelemetry];
        return updated.slice(-35);
      });
    }
  }, [ctxTelemetry]);

  const preds = liveRisk?.predictions || {};
  const mudLoss = preds['MUD_LOSS'];
  const stuckPipe = preds['STUCK_PIPE'];
  const kick = preds['KICK'];

  return (
    <div className="space-y-4 pb-10">
      {/* Active Well Telemetry Top Bar */}
      <div className={`p-4 rounded-lg border transition-colors flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-sans text-emerald-600 dark:text-emerald-400 font-semibold uppercase tracking-wider">
              Real-Time eRTMAC Telemetry Stream
            </span>
            <Badge variant="primary" size="xs">{activeWell?.well_id || 'WELL-001'}</Badge>
            {user?.role === 'Viewer' && (
              <span className={`text-[10px] font-sans ${isDark ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-slate-100 text-slate-600 border-slate-200'} border px-1.5 py-0.2 rounded`}>
                READ-ONLY
              </span>
            )}
          </div>
          <h1 className="text-xl font-bold font-sans text-slate-900 dark:text-white tracking-tight">
            {activeWell?.well_name || 'Active Rig'} &bull; <span className="text-sky-600 dark:text-sky-400 font-medium">{activeFormation}</span> <span className="font-mono text-slate-600 dark:text-slate-300">({liveTelemetry.depth.toFixed(1)} m)</span>
          </h1>
        </div>

        <div className={`flex items-center gap-4 px-3.5 py-2 rounded-md border font-sans text-xs ${
          isDark ? 'bg-slate-900/80 border-slate-700/80 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'
        }`}>
          <div>
            <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Measured Depth</div>
            <div className="text-sm font-bold font-mono text-slate-900 dark:text-white">{liveTelemetry.depth.toFixed(1)} m</div>
          </div>
          <div className={`h-6 w-[1px] ${isDark ? 'bg-slate-700' : 'bg-slate-200'}`} />
          <div>
            <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Current ROP</div>
            <div className="text-sm font-bold font-mono text-sky-600 dark:text-sky-400">{liveTelemetry.rop.toFixed(1)} m/hr</div>
          </div>
          <div className={`h-6 w-[1px] ${isDark ? 'bg-slate-700' : 'bg-slate-200'}`} />
          <div>
            <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase">Mud WT / ECD</div>
            <div className="text-sm font-bold font-mono text-amber-600 dark:text-amber-400">{liveTelemetry.mud_weight.toFixed(2)} / {liveTelemetry.ecd.toFixed(2)} SG</div>
          </div>
        </div>
      </div>

      {/* 8-Dial Live Telemetry Matrix */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
        {[
          { label: 'ROP', value: `${liveTelemetry.rop.toFixed(1)}`, unit: 'm/hr', color: 'text-sky-600 dark:text-sky-400', border: 'border-sky-500/25' },
          { label: 'WOB', value: `${liveTelemetry.wob.toFixed(1)}`, unit: 'tons', color: 'text-emerald-600 dark:text-emerald-400', border: 'border-emerald-500/25' },
          { label: 'RPM', value: `${liveTelemetry.rpm.toFixed(0)}`, unit: 'RPM', color: isDark ? 'text-slate-200' : 'text-slate-800', border: isDark ? 'border-slate-800' : 'border-slate-200' },
          { label: 'TORQUE', value: `${liveTelemetry.torque.toFixed(1)}`, unit: 'kNm', color: 'text-rose-600 dark:text-rose-400', border: 'border-rose-500/25' },
          { label: 'SPP', value: `${liveTelemetry.standpipe_pressure.toFixed(0)}`, unit: 'psi', color: 'text-amber-600 dark:text-amber-400', border: 'border-amber-500/25' },
          { label: 'FLOW RATE', value: `${liveTelemetry.flow_rate.toFixed(0)}`, unit: 'LPM', color: 'text-sky-600 dark:text-sky-400', border: 'border-sky-500/25' },
          { label: 'MUD WEIGHT', value: `${liveTelemetry.mud_weight.toFixed(2)}`, unit: 'SG', color: 'text-purple-600 dark:text-purple-400', border: 'border-purple-500/25' },
          { label: 'HOOK LOAD', value: `${liveTelemetry.hook_load.toFixed(1)}`, unit: 'tons', color: isDark ? 'text-slate-300' : 'text-slate-700', border: isDark ? 'border-slate-800' : 'border-slate-200' },
        ].map((param, i) => (
          <div key={i} className={`p-2.5 rounded-lg border text-center transition-colors ${
            isDark ? 'bg-[#0B111E]' : 'bg-white shadow-xs'
          } ${param.border}`}>
            <div className="text-[10px] font-sans font-semibold uppercase text-slate-500 dark:text-slate-400">{param.label}</div>
            <div className={`text-base font-bold font-mono ${param.color} mt-0.5`}>{param.value}</div>
            <div className="text-[10px] font-sans text-slate-400 dark:text-slate-500">{param.unit}</div>
          </div>
        ))}
      </div>

      {/* ML Risk Prediction Gauges & Contributing Factors */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Mud Loss Risk Box */}
        <Card
          title="Mud Loss Risk Model"
          className="border-rose-500/25"
          headerAction={<RiskPill level={mudLoss?.risk_level || 'HIGH'} probability={mudLoss?.probability || 0.78} />}
        >
          <div className="space-y-3 font-sans text-xs">
            <div className="flex items-center justify-between text-slate-700 dark:text-slate-300">
              <span className="font-medium">Risk Probability:</span>
              <span className="text-base font-bold font-mono text-rose-600 dark:text-rose-400">{((mudLoss?.probability || 0.78) * 100).toFixed(0)}%</span>
            </div>
            <div className={`w-full ${isDark ? 'bg-slate-800' : 'bg-slate-100'} rounded-full h-1.5 overflow-hidden`}>
              <div
                className="bg-rose-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${(mudLoss?.probability || 0.78) * 100}%` }}
              />
            </div>
            <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-2">
              Contributing Factors:
            </div>
            <div className="space-y-1.5">
              {mudLoss?.contributing_factors?.map((f, i) => (
                <div key={i} className={`p-2 rounded-md border text-xs ${
                  isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <div className="font-semibold text-rose-600 dark:text-rose-400 text-xs">&bull; {f.factor_name}</div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px] mt-0.5">{f.description}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Stuck Pipe Risk Box */}
        <Card
          title="Stuck Pipe Risk Model"
          className="border-amber-500/25"
          headerAction={<RiskPill level={stuckPipe?.risk_level || 'MEDIUM'} probability={stuckPipe?.probability || 0.43} />}
        >
          <div className="space-y-3 font-sans text-xs">
            <div className="flex items-center justify-between text-slate-700 dark:text-slate-300">
              <span className="font-medium">Risk Probability:</span>
              <span className="text-base font-bold font-mono text-amber-600 dark:text-amber-400">{((stuckPipe?.probability || 0.43) * 100).toFixed(0)}%</span>
            </div>
            <div className={`w-full ${isDark ? 'bg-slate-800' : 'bg-slate-100'} rounded-full h-1.5 overflow-hidden`}>
              <div
                className="bg-amber-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${(stuckPipe?.probability || 0.43) * 100}%` }}
              />
            </div>
            <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-2">
              Contributing Factors:
            </div>
            <div className="space-y-1.5">
              {stuckPipe?.contributing_factors?.map((f, i) => (
                <div key={i} className={`p-2 rounded-md border text-xs ${
                  isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <div className="font-semibold text-amber-600 dark:text-amber-400 text-xs">&bull; {f.factor_name}</div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px] mt-0.5">{f.description}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Kick Risk Box */}
        <Card
          title="Kick / Well Control Model"
          className="border-emerald-500/25"
          headerAction={<RiskPill level={kick?.risk_level || 'LOW'} probability={kick?.probability || 0.12} />}
        >
          <div className="space-y-3 font-sans text-xs">
            <div className="flex items-center justify-between text-slate-700 dark:text-slate-300">
              <span className="font-medium">Risk Probability:</span>
              <span className="text-base font-bold font-mono text-emerald-600 dark:text-emerald-400">{((kick?.probability || 0.12) * 100).toFixed(0)}%</span>
            </div>
            <div className={`w-full ${isDark ? 'bg-slate-800' : 'bg-slate-100'} rounded-full h-1.5 overflow-hidden`}>
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${(kick?.probability || 0.12) * 100}%` }}
              />
            </div>
            <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mt-2">
              Contributing Factors:
            </div>
            <div className="space-y-1.5">
              {kick?.contributing_factors?.map((f, i) => (
                <div key={i} className={`p-2 rounded-md border text-xs ${
                  isDark ? 'bg-slate-900/50 border-slate-800' : 'bg-slate-50 border-slate-200'
                }`}>
                  <div className="font-semibold text-emerald-600 dark:text-emerald-400 text-xs">&bull; {f.factor_name}</div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px] mt-0.5">{f.description}</div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Synchronized Real-Time Telemetry Logs Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* SPP & Flow Rate Trends */}
        <Card title="Hydraulics Telemetry — Standpipe Pressure (psi) & Flow Rate (LPM)">
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetryHistory}>
                <defs>
                  <linearGradient id="sppGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="flowGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0284C7" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0284C7" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#1E293B' : '#E2E8F0'} />
                <XAxis dataKey="depth" stroke="#64748B" tick={{ fontSize: 10, fill: '#64748B' }} unit="m" />
                <YAxis stroke="#64748B" tick={{ fontSize: 10, fill: '#64748B' }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#0B111E' : '#FFFFFF',
                    borderColor: isDark ? '#1E293B' : '#CBD5E1',
                    color: isDark ? '#F1F5F9' : '#0F172A',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontFamily: 'Inter, sans-serif'
                  }}
                />
                <Area type="monotone" dataKey="standpipe_pressure" name="SPP (psi)" stroke="#F59E0B" fillOpacity={1} fill="url(#sppGrad)" strokeWidth={1.5} />
                <Area type="monotone" dataKey="flow_rate" name="Flow Rate (LPM)" stroke="#0284C7" fillOpacity={1} fill="url(#flowGrad)" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Torque & ROP Trends */}
        <Card title="Mechanical Telemetry — Rotary Torque (kNm) & ROP (m/hr)">
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetryHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#1E293B' : '#E2E8F0'} />
                <XAxis dataKey="depth" stroke="#64748B" tick={{ fontSize: 10, fill: '#64748B' }} unit="m" />
                <YAxis stroke="#64748B" tick={{ fontSize: 10, fill: '#64748B' }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#0B111E' : '#FFFFFF',
                    borderColor: isDark ? '#1E293B' : '#CBD5E1',
                    color: isDark ? '#F1F5F9' : '#0F172A',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontFamily: 'Inter, sans-serif'
                  }}
                />
                <Line type="monotone" dataKey="torque" name="Torque (kNm)" stroke="#EF4444" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="rop" name="ROP (m/hr)" stroke="#10B981" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Historical Offset Problem Zones for this Horizon */}
      <Card
        title="Historical Offset Problem Zones (3350m - 3500m Horizon)"
        subtitle="Events recorded in nearby wells penetrating this identical Barail Sandstone formation"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left font-sans text-xs">
            <thead>
              <tr className={`border-b ${isDark ? 'border-slate-800 text-slate-400 bg-slate-900/30' : 'border-slate-100 text-slate-500 bg-slate-50/60'}`}>
                <th className="py-2.5 px-3 font-semibold">Offset Well</th>
                <th className="py-2.5 px-3 font-semibold">Event Depth</th>
                <th className="py-2.5 px-3 font-semibold">Incident Type</th>
                <th className="py-2.5 px-3 font-semibold">Severity</th>
                <th className="py-2.5 px-3 font-semibold">Recorded Mitigation</th>
                <th className="py-2.5 px-3 font-semibold">Source Report</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${isDark ? 'divide-slate-800/60' : 'divide-slate-100'}`}>
              {offsetEvents.slice(0, 6).map((ev) => (
                <tr key={ev.event_id} className={`${isDark ? 'hover:bg-slate-900/40' : 'hover:bg-slate-50'} transition`}>
                  <td className="py-2.5 px-3 font-semibold text-slate-900 dark:text-white">{ev.well_name || ev.well_id}</td>
                  <td className="py-2.5 px-3 font-mono font-medium text-sky-600 dark:text-sky-400">{ev.start_depth} m</td>
                  <td className="py-2.5 px-3 font-medium text-amber-600 dark:text-amber-400">{ev.event_type}</td>
                  <td className="py-2.5 px-3"><RiskPill level={ev.severity} /></td>
                  <td className="py-2.5 px-3 text-slate-700 dark:text-slate-300 text-xs max-w-xs truncate">{ev.mitigation}</td>
                  <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400 text-[11px]">{ev.source_document} (p.{ev.source_page})</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

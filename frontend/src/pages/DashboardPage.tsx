import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWell } from '../store/wellContext';
import { useTheme } from '../store/themeContext';
import { NearbyWell, Alert, DrillingEvent, SystemStatus } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import {
  Activity, MapPin, Layers, AlertOctagon, TrendingUp, History,
  ArrowRight, ShieldAlert, Zap, Compass, RefreshCw, ChevronRight
} from 'lucide-react';

interface DashboardPageProps {
  onNavigate: (page: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { activeWell, activeDepth, activeFormation, liveTelemetry: ctxTelemetry, liveRisk: ctxRisk } = useWell();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [nearbyWells, setNearbyWells] = useState<NearbyWell[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [recentEvents, setRecentEvents] = useState<DrillingEvent[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  const liveTelemetry = ctxTelemetry || {
    depth: activeDepth || 3420.0,
    formation_name: activeFormation || 'Barail Sandstone',
    rop: 7.8,
    wob: 16.2,
    torque: 18.5,
    standpipe_pressure: 2180.0,
    flow_rate: 1750.0,
    mud_weight: 1.28
  };

  const preds = ctxRisk?.predictions || {};
  const liveRisk = {
    overall_risk_level: ctxRisk?.overall_risk_level || 'HIGH',
    mud_loss_prob: preds['MUD_LOSS']?.probability || 0.78,
    stuck_pipe_prob: preds['STUCK_PIPE']?.probability || 0.43,
    kick_prob: preds['KICK']?.probability || 0.12
  };

  useEffect(() => {
    if (!activeWell) return;
    api.getNearbyWells(activeWell.well_id, 25).then(setNearbyWells).catch(console.error);
    api.getAlerts(activeWell.well_id).then(setAlerts).catch(console.error);
    api.getEvents({ formation: activeFormation }).then((evs) => setRecentEvents(evs.slice(0, 5))).catch(console.error);
    api.getSystemStatus().then(setSystemStatus).catch(console.error);
  }, [activeWell?.well_id, activeFormation]);

  return (
    <div className="space-y-4 pb-10">
      {/* Top Operational Rig Context Banner */}
      <div className={`p-4 rounded-lg border transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isDark
          ? 'bg-[#0B111E] border-slate-800/90 text-slate-100'
          : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-sans uppercase tracking-wider text-emerald-600 dark:text-emerald-400 font-semibold">
              Real-Time Operational Rig Stream
            </span>
            <Badge variant="primary" size="xs">eRTMAC LINK</Badge>
          </div>
          <h1 className="text-xl font-bold font-sans tracking-tight text-slate-900 dark:text-white flex items-center gap-2.5">
            <span>{activeWell?.well_name || 'Dikom-104A'}</span>
            <span className="text-xs font-normal text-slate-500 dark:text-slate-400 font-sans">
              ({activeWell?.field || 'Dikom'} Field &bull; {activeWell?.block || 'Dibrugarh ML'})
            </span>
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('active-well')}
            className="px-3 py-1.5 rounded-md bg-sky-600 hover:bg-sky-500 text-white font-sans text-xs font-semibold transition flex items-center gap-1.5 shadow-xs"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Open Live Telemetry</span>
          </button>
          <button
            onClick={() => onNavigate('map')}
            className={`px-3 py-1.5 rounded-md border font-sans text-xs font-medium transition flex items-center gap-1.5 ${
              isDark
                ? 'bg-slate-900 hover:bg-slate-800 text-slate-200 border-slate-700'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
            }`}
          >
            <MapPin className="w-3.5 h-3.5 text-sky-500" />
            <span>25 km Radius Map</span>
          </button>
        </div>
      </div>

      {/* 4 Metric KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Depth & Formation */}
        <Card className="border-l-2 border-l-sky-500">
          <div className="text-[11px] font-sans font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 flex items-center justify-between">
            <span>Current Depth</span>
            <Layers className="w-3.5 h-3.5 text-sky-500" />
          </div>
          <div className="mt-1.5 text-2xl font-bold font-mono text-slate-900 dark:text-white">
            {liveTelemetry.depth.toFixed(1)} <span className="text-xs font-normal text-slate-400">m</span>
          </div>
          <div className="mt-1 text-xs text-amber-600 dark:text-amber-400 font-sans font-medium truncate">
            {liveTelemetry.formation_name}
          </div>
        </Card>

        {/* ML Risk Status */}
        <Card className="border-l-2 border-l-rose-500">
          <div className="text-[11px] font-sans font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 flex items-center justify-between">
            <span>ML Risk Status</span>
            <AlertOctagon className="w-3.5 h-3.5 text-rose-500" />
          </div>
          <div className="mt-1.5 flex items-center gap-2">
            <RiskPill level={liveRisk.overall_risk_level} />
          </div>
          <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 font-sans">
            Mud Loss: <span className="font-mono font-semibold text-rose-600 dark:text-rose-400">{(liveRisk.mud_loss_prob * 100).toFixed(0)}%</span> | Stuck: <span className="font-mono font-semibold text-amber-600 dark:text-amber-400">{(liveRisk.stuck_pipe_prob * 100).toFixed(0)}%</span>
          </div>
        </Card>

        {/* Nearby Offset Wells */}
        <Card className="border-l-2 border-l-amber-500">
          <div className="text-[11px] font-sans font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 flex items-center justify-between">
            <span>Nearby Offset Wells</span>
            <Compass className="w-3.5 h-3.5 text-amber-500" />
          </div>
          <div className="mt-1.5 text-2xl font-bold font-mono text-slate-900 dark:text-white">
            {nearbyWells.length} <span className="text-xs font-normal text-slate-400">within 25 km</span>
          </div>
          <div className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 font-sans font-medium">
            {nearbyWells.filter((w) => w.similarity_score > 70).length} High-Similarity Offsets
          </div>
        </Card>

        {/* Proactive Alerts */}
        <Card className="border-l-2 border-l-purple-500">
          <div className="text-[11px] font-sans font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400 flex items-center justify-between">
            <span>Proactive Alerts</span>
            <Zap className="w-3.5 h-3.5 text-purple-500" />
          </div>
          <div className="mt-1.5 text-2xl font-bold font-mono text-slate-900 dark:text-white">
            {alerts.length} <span className="text-xs font-normal text-slate-400">active items</span>
          </div>
          <div className="mt-1 text-xs text-slate-500 dark:text-slate-400 font-sans">
            LCM & Survey protocol active
          </div>
        </Card>
      </div>

      {/* Main Content: Offset Wells Correlation + Live Anomalies */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left 2 Cols: Nearby Offsets Ranking Table */}
        <div className="lg:col-span-2 space-y-4">
          <Card
            title="Nearby Offset Wells Correlation (25 km Window)"
            subtitle="Ranked by multi-factor stratigraphic and geospatial similarity"
            headerAction={
              <button
                onClick={() => onNavigate('map')}
                className="text-xs font-sans text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1 font-semibold"
              >
                <span>Full Map View</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            }
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-sans">
                <thead>
                  <tr className={`border-b ${isDark ? 'border-slate-800 text-slate-400 bg-slate-900/30' : 'border-slate-100 text-slate-500 bg-slate-50/60'}`}>
                    <th className="py-2.5 px-3 font-semibold">Well Name</th>
                    <th className="py-2.5 px-3 font-semibold">Distance</th>
                    <th className="py-2.5 px-3 font-semibold">Similarity</th>
                    <th className="py-2.5 px-3 font-semibold">Risk Profile</th>
                    <th className="py-2.5 px-3 font-semibold">Past Incidents</th>
                    <th className="py-2.5 px-3 text-right font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody className={`divide-y ${isDark ? 'divide-slate-800/60' : 'divide-slate-100'}`}>
                  {nearbyWells.slice(0, 5).map((item) => (
                    <tr key={item.well.well_id} className={`${isDark ? 'hover:bg-slate-900/40' : 'hover:bg-slate-50'} transition`}>
                      <td className="py-2.5 px-3 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0"></span>
                        <span className="truncate">{item.well.well_name}</span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-600 dark:text-slate-300 font-medium">
                        {item.distance_km} km
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-14 ${isDark ? 'bg-slate-800' : 'bg-slate-200'} rounded-full h-1.5 overflow-hidden`}>
                            <div
                              className="bg-emerald-500 h-full rounded-full"
                              style={{ width: `${item.similarity_score}%` }}
                            />
                          </div>
                          <span className="font-mono text-emerald-600 dark:text-emerald-400 font-semibold">{item.similarity_score}%</span>
                        </div>
                      </td>
                      <td className="py-2.5 px-3">
                        <RiskPill level={item.risk_level} />
                      </td>
                      <td className="py-2.5 px-3 font-mono text-amber-600 dark:text-amber-400 font-medium">
                        {item.historical_events_count} recorded
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => onNavigate('comparison')}
                          className={`px-2 py-1 rounded text-xs font-sans font-medium transition border ${
                            isDark
                              ? 'bg-slate-800 hover:bg-slate-700 text-sky-400 border-slate-700'
                              : 'bg-slate-100 hover:bg-slate-200 text-sky-700 border-slate-200'
                          }`}
                        >
                          Compare Log
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Recent Historical Events Stream */}
          <Card
            title="Institutional Memory — Recent Historical Incidents"
            subtitle="Verified reports from offset wells in Assam-Arakan basin"
            headerAction={
              <button
                onClick={() => onNavigate('knowledge-repo')}
                className="text-xs font-sans text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1 font-semibold"
              >
                <span>Browse All</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            }
          >
            <div className="space-y-2.5">
              {recentEvents.map((ev) => (
                <div
                  key={ev.event_id}
                  className={`p-3 rounded-lg border transition ${
                    isDark
                      ? 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
                      : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-slate-900 dark:text-white">{ev.well_name || ev.well_id}</span>
                      <span className="text-slate-500 dark:text-slate-400 font-sans text-xs">
                        @ <span className="font-mono">{ev.start_depth} m</span> ({ev.formation})
                      </span>
                    </div>
                    <RiskPill level={ev.severity} />
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-300 font-sans leading-relaxed">
                    <span className="font-semibold text-amber-600 dark:text-amber-400">{ev.event_type}: </span>
                    {ev.cause}
                  </p>
                  <div className={`mt-2 text-xs p-2 rounded border font-sans ${
                    isDark ? 'text-slate-300 bg-[#080C14] border-slate-800' : 'text-slate-700 bg-white border-slate-200'
                  }`}>
                    <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Mitigation: </span>
                    {ev.mitigation}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right 1 Col: Live Anomaly & Proactive Recommendations */}
        <div className="space-y-4">
          {/* Active Alert Capsule */}
          <Card
            title="Proactive Decision Support"
            className="border-amber-500/30 dark:border-amber-500/40"
          >
            <div className="space-y-3 font-sans text-xs">
              <div className={`p-3 border rounded-lg ${
                isDark ? 'bg-amber-950/30 border-amber-500/40 text-amber-200' : 'bg-amber-50 border-amber-200 text-amber-900'
              }`}>
                <div className="flex items-center gap-2 font-bold text-amber-600 dark:text-amber-400 mb-1">
                  <ShieldAlert className="w-4 h-4 shrink-0" />
                  <span>MUD LOSS & DIFFERENTIAL STICKING ALERT</span>
                </div>
                <p className="text-[11px] leading-relaxed opacity-90 font-sans">
                  Active depth (3420 m) penetrates depleted Barail Sandstone horizon. Offset well evidence shows 75% historical loss frequency.
                </p>
              </div>

              <div>
                <div className="text-[10px] font-sans font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                  Immediate Operating Recommendations:
                </div>
                <ul className="space-y-2 text-slate-700 dark:text-slate-300 font-sans text-xs">
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">1.</span>
                    <span>Pre-mix 40 bbl high-fluid-loss LCM pill (medium CaCO3 + nut plug) on surface.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">2.</span>
                    <span>Reduce pump rate from 2100 LPM to 1850 LPM to mitigate ECD surging.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">3.</span>
                    <span>Maintain continuous drillstring rotation (min 15-20 RPM) while surveying.</span>
                  </li>
                </ul>
              </div>

              <div className={`pt-2.5 border-t ${isDark ? 'border-slate-800' : 'border-slate-100'}`}>
                <button
                  onClick={() => onNavigate('alerts')}
                  className="w-full py-2 rounded-md bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition flex items-center justify-center gap-1.5 shadow-xs"
                >
                  <span>Acknowledge in Alerts Center</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </Card>

          {/* Quick RAG Assistant Box */}
          <Card title="NWIS Historical Assistant">
            <div className="space-y-3 font-sans text-xs">
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                Query offset well incidents, past mitigations, and lessons learned:
              </p>
              <div className="space-y-1.5">
                {[
                  'What happened in nearby wells around 3420 m?',
                  'Which wells experienced mud losses in Barail Sand?',
                  'Show past differential sticking jarring procedures.'
                ].map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => onNavigate('assistant')}
                    className={`w-full text-left p-2 rounded border text-[11px] font-sans truncate flex items-center justify-between transition ${
                      isDark
                        ? 'bg-slate-900/60 hover:bg-slate-800 text-slate-300 border-slate-800 hover:border-slate-700'
                        : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
                    }`}
                  >
                    <span className="truncate">{query}</span>
                    <ChevronRight className="w-3 h-3 text-sky-500 shrink-0 ml-1" />
                  </button>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

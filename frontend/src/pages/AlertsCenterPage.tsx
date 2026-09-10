import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../store/authContext';
import { useTheme } from '../store/themeContext';
import { Alert } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import { BellRing, CheckCircle2, ShieldAlert, History, UserCheck, AlertTriangle } from 'lucide-react';

export const AlertsCenterPage: React.FC = () => {
  const { user } = useAuth();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');

  useEffect(() => {
    loadAlerts();
  }, [selectedStatus]);

  const loadAlerts = () => {
    const statusParam = selectedStatus === 'ALL' ? undefined : selectedStatus;
    api.getAlerts(undefined, statusParam).then(setAlerts).catch(console.error);
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId, user?.full_name || 'Drilling Lead');
      loadAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  return (
    <div className="space-y-4 pb-10 max-w-5xl mx-auto">
      {/* Header */}
      <div className={`p-4 rounded-lg border transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <BellRing className="w-3.5 h-3.5 text-amber-500" />
            <span className="text-[11px] font-sans text-amber-600 dark:text-amber-400 font-semibold uppercase tracking-wider">
              Proactive Alert Engine & Incident Prevention
            </span>
          </div>
          <h1 className="text-xl font-bold font-sans text-slate-900 dark:text-white tracking-tight">
            Alerts & Operations Verification Center
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-sans mt-0.5">
            Real-time proactive warnings generated when telemetry breaches ML thresholds or approaches historical problem horizons.
          </p>
        </div>

        {/* Status Filter Chips */}
        <div className={`flex items-center gap-1 p-1 rounded-md border text-xs font-sans ${
          isDark ? 'bg-slate-900/80 border-slate-800' : 'bg-slate-50 border-slate-200'
        }`}>
          {['ALL', 'NEW', 'ACKNOWLEDGED'].map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={`px-3 py-1 rounded text-xs font-sans transition ${
                selectedStatus === st
                  ? 'bg-sky-600 text-white font-semibold shadow-xs'
                  : (isDark ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900')
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3 font-sans">
        {alerts.length === 0 ? (
          <div className={`p-10 text-center text-slate-500 dark:text-slate-400 text-xs rounded-lg border ${
            isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200 shadow-xs'
          }`}>
            No active alerts matching filter. All parameters conforming to baseline envelope.
          </div>
        ) : (
          (Array.isArray(alerts) ? alerts : []).filter(Boolean).map((alert, idx) => {
            const alertId = alert.alert_id || `alert-${idx}`;
            const alertStatus = alert.status || ((alert as any).acknowledged ? 'ACKNOWLEDGED' : 'NEW');
            const rawRisk = alert.risk_type || (alert as any).category || (alert as any).title || 'OPERATIONAL_RISK';
            const riskType = String(rawRisk).replace('_', ' ');
            const severity = alert.severity || 'HIGH';
            const prob = typeof alert.probability === 'number' ? alert.probability : 0.75;
            const depth = alert.depth || 3420.0;
            const formation = alert.formation || 'Barail Sandstone';
            const reasons = Array.isArray(alert.reasons)
              ? alert.reasons
              : ((alert as any).message ? [(alert as any).message] : []);
            const evidence = Array.isArray(alert.historical_evidence) ? alert.historical_evidence : [];
            const action = alert.recommended_action || (alert as any).message || 'Monitor parameters closely';

            return (
              <div
                key={alertId}
                className={`p-4 rounded-lg border transition space-y-3 text-xs ${
                  alertStatus === 'NEW'
                    ? (isDark ? 'bg-[#0B111E] border-amber-500/40 shadow-sm' : 'bg-white border-amber-300 shadow-xs')
                    : (isDark ? 'bg-[#0B111E]/70 border-slate-800/80 opacity-80' : 'bg-slate-50 border-slate-200 opacity-90')
                }`}
              >
                {/* Alert Header */}
                <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-2.5 ${
                  isDark ? 'border-slate-800' : 'border-slate-100'
                }`}>
                  <div className="flex items-center gap-2.5">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">{riskType} ALERT</span>
                    <RiskPill level={severity} probability={prob} />
                    <Badge variant={alertStatus === 'NEW' ? 'warning' : 'success'}>
                      {alertStatus}
                    </Badge>
                  </div>
                  <div className="text-slate-500 dark:text-slate-400 text-[11px]">
                    Depth: <b className="font-mono text-slate-700 dark:text-slate-300">{depth} m</b> ({formation}) &bull; ID: <span className="font-mono">{alertId}</span>
                  </div>
                </div>

                {/* Reasons & Evidence */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {/* Contributing Reasons */}
                  <div className="space-y-1.5">
                    <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Contributing Anomaly Reasons:
                    </div>
                    <ul className="space-y-1 text-slate-700 dark:text-slate-300 text-xs">
                      {reasons.map((r, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="text-amber-500 font-bold">&bull;</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Grounded Historical Evidence */}
                  <div className="space-y-1.5">
                    <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                      Offset Well Historical Evidence:
                    </div>
                    <div className="space-y-1">
                      {evidence.slice(0, 2).map((ev: any, i: number) => (
                        <div key={i} className={`p-2 rounded-md border text-[11px] ${
                          isDark ? 'bg-slate-900/60 border-slate-800 text-slate-300' : 'bg-slate-50 border-slate-200 text-slate-700'
                        }`}>
                          <span className="font-semibold text-sky-600 dark:text-sky-400">{ev.well_name || ev.well_id || 'Offset Rig'} @ <span className="font-mono">{ev.depth || 3200}m</span>: </span>
                          {ev.mitigation || ev.impact || 'Standard mitigation applied'}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Recommended Action & Acknowledge */}
                <div className={`pt-2.5 border-t flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-2.5 rounded-md ${
                  isDark ? 'border-slate-800 bg-slate-900/40' : 'border-slate-100 bg-slate-50/70'
                }`}>
                  <div className="text-xs text-emerald-700 dark:text-emerald-300">
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400 uppercase text-[10px] block">Recommended Action:</span>
                    {action}
                  </div>

                  {alertStatus === 'NEW' ? (
                    user?.role === 'Viewer' ? (
                      <div className={`px-3 py-1.5 rounded-md text-xs font-sans border ${
                        isDark ? 'bg-slate-800 text-slate-500 border-slate-700' : 'bg-slate-100 text-slate-500 border-slate-200'
                      }`}>
                        Viewer (Read-Only)
                      </div>
                    ) : (
                      <button
                        onClick={() => handleAcknowledge(alertId)}
                        className="px-3.5 py-1.5 rounded-md bg-amber-600 hover:bg-amber-500 text-white font-semibold text-xs transition flex items-center gap-1.5 shadow-xs shrink-0"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Acknowledge Alert</span>
                      </button>
                    )
                  ) : (
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                      <UserCheck className="w-3.5 h-3.5 text-emerald-500" />
                      <span>Acknowledged by <b>{alert.acknowledged_by || 'Drilling Supervisor'}</b></span>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

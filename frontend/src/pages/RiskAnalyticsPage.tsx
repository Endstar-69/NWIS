import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWell } from '../store/wellContext';
import { useAuth } from '../store/authContext';
import { ModelMetrics, ShapExplanationResponse } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import {
  LineChart, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area, Cell
} from 'recharts';
import {
  Cpu, Activity, Sliders, DollarSign, Layers, FileText, Search, AlertTriangle, ArrowRight, CheckCircle2, TrendingUp,
  ShieldAlert, RefreshCw, Info, HelpCircle
} from 'lucide-react';

export const RiskAnalyticsPage: React.FC = () => {
  const { activeWell, activeDepth, activeFormation, liveTelemetry } = useWell();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'models' | 'explainability' | 'depth_explorer' | 'what_if' | 'npt_cost' | 'heatmap' | 'daily_report'>('models');
  
  // Model Metrics State
  const [metrics, setMetrics] = useState<Record<string, ModelMetrics>>({});
  const [activeModelKey, setActiveModelKey] = useState<string>('mud_loss');

  // Explainability (Tree SHAP) State
  const [shapData, setShapData] = useState<ShapExplanationResponse | null>(null);
  const [shapModelKey, setShapModelKey] = useState<'mud_loss' | 'stuck_pipe' | 'kick'>('mud_loss');
  const [shapLoading, setShapLoading] = useState<boolean>(false);

  // Depth Explorer State
  const [explorerDepth, setExplorerDepth] = useState<number>(activeDepth || 3420);
  const [explorerData, setExplorerData] = useState<any>(null);
  const [timelineData, setTimelineData] = useState<any[]>([]);

  // What-If Sandbox State
  const [simParams, setSimParams] = useState({
    depth: activeDepth || 3420,
    formation: activeFormation || 'Barail Sandstone',
    mud_weight: 1.28,
    sim_mud_weight: 1.34,
    flow_rate: 550,
    sim_flow_rate: 460,
    wob: 22,
    sim_wob: 26,
    rpm: 110,
    sim_rpm: 95,
    standpipe_pressure: 2800,
    sim_standpipe_pressure: 2680
  });
  const [simResult, setSimResult] = useState<any>(null);
  const [simLoading, setSimLoading] = useState<boolean>(false);

  // NPT & Cost State
  const [nptData, setNptData] = useState<any>(null);

  // Heatmap & Knowledge Graph State
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<any>(null);

  // Daily Report State
  const [reportData, setReportData] = useState<any>(null);

  const loadShapExplanations = () => {
    setShapLoading(true);
    const telemetry = {
      well_id: activeWell?.well_id || 'WELL-001',
      depth: activeDepth || 3420.0,
      formation_name: activeFormation || 'Barail Sandstone',
      rop: liveTelemetry?.rop || 7.8,
      wob: liveTelemetry?.wob || 16.2,
      rpm: liveTelemetry?.rpm || 105.0,
      torque: liveTelemetry?.torque || 18.5,
      standpipe_pressure: liveTelemetry?.standpipe_pressure || 2180.0,
      flow_rate: liveTelemetry?.flow_rate || 1750.0,
      mud_weight: liveTelemetry?.mud_weight || 1.28,
      ecd: liveTelemetry?.ecd || 1.33
    };
    api.explainRisk(telemetry)
      .then(setShapData)
      .catch(console.error)
      .finally(() => setShapLoading(false));
  };

  useEffect(() => {
    // Initial data loading
    api.getModelMetrics().then((data) => {
      setMetrics(data);
      if (Object.keys(data).length > 0) setActiveModelKey(Object.keys(data)[0]);
    }).catch(console.error);

    loadDepthExplorer(activeDepth || 3420);
    runWhatIfSimulation();
    loadShapExplanations();
    api.getNptCostIntelligence().then(setNptData).catch(console.error);
    api.getRiskHeatmap().then(setHeatmapData).catch(console.error);
    api.getKnowledgeGraph().then(setGraphData).catch(console.error);
    api.getDailyReport().then(setReportData).catch(console.error);
  }, [activeWell?.well_id]);

  const loadDepthExplorer = (d: number) => {
    setExplorerDepth(d);
    api.getDepthExplorer(d).then(setExplorerData).catch(console.error);
    api.getPredictiveTimeline(d).then(setTimelineData).catch(console.error);
  };

  const runWhatIfSimulation = () => {
    setSimLoading(true);
    api.simulateWhatIf(simParams).then((res) => {
      setSimResult(res);
      setSimLoading(false);
    }).catch((err) => {
      console.error(err);
      setSimLoading(false);
    });
  };

  const activeModel = metrics[activeModelKey];
  const featureData = activeModel
    ? Object.entries(activeModel.feature_importances || {})
        .slice(0, 8)
        .map(([feature, importance]) => ({
          feature: feature.replace(/_/g, ' '),
          importance: Number((importance * 100).toFixed(1))
        }))
    : [];

  return (
    <div className="space-y-6 pb-16 max-w-7xl mx-auto">
      {/* Page Header with Tab Navigation */}
      <div className="bg-[#0B111E] border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Cpu className="w-5 h-5 text-sky-400" />
              <span className="text-xs font-mono text-sky-400 font-bold uppercase tracking-wider">
                Advanced Analytics & Innovation Hub (Tier 2 & 3)
              </span>
            </div>
            <h1 className="text-2xl font-bold font-mono text-white tracking-tight">
              Drilling Risk & Operational Intelligence
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Supervised ML models, Lookahead Depth Explorer, What-If Parameter Sandbox, NPT Financial Analytics & Geological Heatmaps.
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex flex-wrap items-center gap-1.5 bg-slate-900 border border-slate-800 p-1.5 rounded-xl font-mono text-xs">
            <button
              onClick={() => setActiveTab('models')}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'models' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Cpu className="w-3.5 h-3.5" /> ML Models
            </button>
            <button
              onClick={() => {
                setActiveTab('explainability');
                if (!shapData) loadShapExplanations();
              }}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'explainability' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Activity className="w-3.5 h-3.5 text-amber-400" /> SHAP Explainability
            </button>
            <button
              onClick={() => setActiveTab('depth_explorer')}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'depth_explorer' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Search className="w-3.5 h-3.5" /> Depth Explorer
            </button>
            <button
              onClick={() => setActiveTab('what_if')}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'what_if' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" /> What-If Sandbox
            </button>
            <button
              onClick={() => setActiveTab('npt_cost')}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'npt_cost' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <DollarSign className="w-3.5 h-3.5" /> NPT & Cost
            </button>
            <button
              onClick={() => setActiveTab('heatmap')}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'heatmap' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" /> Risk Heatmap
            </button>
            <button
              onClick={() => setActiveTab('daily_report')}
              className={`px-3 py-1.5 rounded-lg transition font-bold flex items-center gap-1.5 ${
                activeTab === 'daily_report' ? 'bg-sky-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" /> Daily Report
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: SUPERVISED ML MODELS */}
      {activeTab === 'models' && activeModel && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 p-2 rounded-xl font-mono text-xs w-fit">
            <span className="text-slate-400 px-2">Select Model Target:</span>
            {Object.keys(metrics).map((key) => (
              <button
                key={key}
                onClick={() => setActiveModelKey(key)}
                className={`px-3 py-1 rounded-lg transition font-bold ${
                  activeModelKey === key ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-white'
                }`}
              >
                {key.replace(/_/g, ' ').toUpperCase()}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="border-l-4 border-l-emerald-500">
              <div className="text-[11px] font-mono text-slate-400 uppercase">Test Accuracy</div>
              <div className="text-3xl font-bold font-mono text-white mt-1">{(activeModel.accuracy * 100).toFixed(1)}%</div>
              <div className="text-[11px] text-emerald-400 font-mono mt-1">Stratified 80/20 Split</div>
            </Card>
            <Card className="border-l-4 border-l-sky-500">
              <div className="text-[11px] font-mono text-slate-400 uppercase">Precision & Recall</div>
              <div className="text-2xl font-bold font-mono text-sky-400 mt-1">
                {(activeModel.precision * 100).toFixed(1)}% / {(activeModel.recall * 100).toFixed(1)}%
              </div>
              <div className="text-[11px] text-slate-400 font-mono mt-1">F1: {(activeModel.f1_score * 100).toFixed(1)}%</div>
            </Card>
            <Card className="border-l-4 border-l-amber-500">
              <div className="text-[11px] font-mono text-slate-400 uppercase">ROC-AUC Score</div>
              <div className="text-3xl font-bold font-mono text-amber-400 mt-1">{activeModel.roc_auc ? activeModel.roc_auc.toFixed(4) : '1.0000'}</div>
              <div className="text-[11px] text-slate-400 font-mono mt-1">Discriminative Power</div>
            </Card>
            <Card className="border-l-4 border-l-purple-500">
              <div className="text-[11px] font-mono text-slate-400 uppercase">Training Dataset Size</div>
              <div className="text-2xl font-bold font-mono text-purple-400 mt-1">{activeModel.training_sample_count} rows</div>
              <div className="text-[11px] text-slate-400 font-mono mt-1">Class-Balanced Random Forest</div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card title={`Top Predictive Feature Importances — ${activeModel.model_name}`} subtitle="Gini impurity relative contribution">
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={featureData} layout="vertical" margin={{ left: 40, right: 20, top: 10, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                      <XAxis type="number" stroke="#64748B" unit="%" />
                      <YAxis type="category" dataKey="feature" stroke="#94A3B8" tick={{ fontSize: 11, fill: '#94A3B8' }} width={140} />
                      <Tooltip contentStyle={{ backgroundColor: '#0B111E', borderColor: '#1E293B', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }} />
                      <Bar dataKey="importance" name="Contribution (%)" fill="#0284C7" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </div>

            <div>
              <Card title="Test Set Confusion Matrix">
                <div className="space-y-4 font-mono text-xs">
                  <div className="grid grid-cols-2 gap-2 text-center">
                    <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                      <div className="text-slate-500 text-[10px]">TRUE NEGATIVE</div>
                      <div className="text-xl font-bold text-white mt-1">{activeModel.confusion_matrix?.[0]?.[0] || 0}</div>
                    </div>
                    <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                      <div className="text-rose-400 text-[10px]">FALSE POSITIVE</div>
                      <div className="text-xl font-bold text-rose-400 mt-1">{activeModel.confusion_matrix?.[0]?.[1] || 0}</div>
                    </div>
                    <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                      <div className="text-amber-400 text-[10px]">FALSE NEGATIVE</div>
                      <div className="text-xl font-bold text-amber-400 mt-1">{activeModel.confusion_matrix?.[1]?.[0] || 0}</div>
                    </div>
                    <div className="p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-lg">
                      <div className="text-emerald-400 text-[10px]">TRUE POSITIVE</div>
                      <div className="text-xl font-bold text-emerald-400 mt-1">{activeModel.confusion_matrix?.[1]?.[1] || 0}</div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* TAB: TREE SHAP EXPLAINABILITY */}
      {activeTab === 'explainability' && (
        <div className="space-y-6">
          {/* Top Context & Model Switcher Bar */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <span className="text-slate-400 font-mono text-xs font-semibold">Select Model Explainer:</span>
              {(['mud_loss', 'stuck_pipe', 'kick'] as const).map((key) => (
                <button
                  key={key}
                  onClick={() => setShapModelKey(key)}
                  className={`px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition ${
                    shapModelKey === key
                      ? 'bg-sky-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-white bg-slate-800/80 border border-slate-700/60'
                  }`}
                >
                  {key.replace(/_/g, ' ').toUpperCase()}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-xs font-mono bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-slate-300">
                <span className="text-slate-500">Live Context:</span>
                <span className="text-emerald-400 font-bold">{activeWell?.well_name || activeWell?.well_id || 'WELL-001'}</span>
                <span className="text-slate-600">|</span>
                <span className="text-sky-400 font-bold">{activeDepth.toFixed(1)} m</span>
                <span className="text-slate-600">|</span>
                <span className="text-amber-400 font-medium">{activeFormation}</span>
              </div>
              <button
                onClick={loadShapExplanations}
                disabled={shapLoading}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-mono text-xs font-bold transition flex items-center gap-1.5"
                title="Recalculate Tree SHAP for live telemetry"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${shapLoading ? 'animate-spin' : ''}`} />
                <span>Refresh SHAP</span>
              </button>
            </div>
          </div>

          {shapLoading && (
            <div className="p-12 text-center text-slate-400 font-mono text-sm bg-[#0B111E] rounded-xl border border-slate-800">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-sky-400" />
              Computing exact TreeExplainer Shapley values f(x) = E[f(x)] + ∑ φᵢ...
            </div>
          )}

          {!shapLoading && shapData && (() => {
            const currentExpl = shapData[shapModelKey];
            const baseVal = currentExpl?.base_value || 0;
            const predVal = currentExpl?.prediction_value || 0;
            const netDelta = predVal - baseVal;
            const topFeatures = currentExpl?.top_features || [];

            const chartData = topFeatures.map((f) => ({
              feature: f.feature_name.replace(/_/g, ' '),
              shap_value: Number(f.shap_value.toFixed(4)),
              direction: f.impact_direction,
              value: f.feature_value
            }));

            return (
              <>
                {/* Shapley Additive Decomposition KPI Triad */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
                  <Card className="border-l-4 border-l-slate-500">
                    <div className="text-[11px] text-slate-400 uppercase">Prior Expected Base Rate E[f(x)]</div>
                    <div className="text-3xl font-bold text-white mt-1">{(baseVal * 100).toFixed(1)}%</div>
                    <div className="text-[11px] text-slate-400 mt-1">Global Background Dataset Expectation</div>
                  </Card>

                  <Card className={`border-l-4 ${predVal > 0.6 ? 'border-l-rose-500' : (predVal > 0.3 ? 'border-l-amber-500' : 'border-l-emerald-500')}`}>
                    <div className="text-[11px] text-slate-400 uppercase">Current Prediction Output f(x)</div>
                    <div className={`text-3xl font-bold mt-1 ${predVal > 0.6 ? 'text-rose-400' : (predVal > 0.3 ? 'text-amber-400' : 'text-emerald-400')}`}>
                      {(predVal * 100).toFixed(1)}%
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">Telemetry-Evaluated Hazard Output</div>
                  </Card>

                  <Card className={`border-l-4 ${netDelta >= 0 ? 'border-l-rose-500' : 'border-l-emerald-500'}`}>
                    <div className="text-[11px] text-slate-400 uppercase">Sum of Shapley Attributions (∑ φᵢ)</div>
                    <div className={`text-3xl font-bold mt-1 ${netDelta >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {netDelta >= 0 ? '+' : ''}{(netDelta * 100).toFixed(1)}%
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">f(x) - E[f(x)] Net Hazard Attribution</div>
                  </Card>
                </div>

                {/* Main Split: SHAP Feature Attribution Waterfall (Left) & Engineering Physics Warnings (Right) */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left: Tree SHAP Attribution Bar Chart & Feature Table */}
                  <div className="lg:col-span-2 space-y-6">
                    <Card
                      title={`Tree SHAP Feature Attribution — ${shapModelKey.replace(/_/g, ' ').toUpperCase()}`}
                      subtitle="Directional Shapley values: Positive values increase hazard; negative values decrease hazard"
                    >
                      <div className="h-80 w-full mb-6">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={chartData} layout="vertical" margin={{ left: 50, right: 30, top: 10, bottom: 10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                            <XAxis type="number" stroke="#64748B" domain={['auto', 'auto']} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                            <YAxis type="category" dataKey="feature" stroke="#94A3B8" tick={{ fontSize: 11, fill: '#94A3B8' }} width={150} />
                            <Tooltip
                              formatter={(value: any) => [`${(Number(value) * 100).toFixed(2)}%`, 'SHAP Attribution φᵢ']}
                              contentStyle={{ backgroundColor: '#0B111E', borderColor: '#1E293B', borderRadius: '8px', fontSize: '11px', fontFamily: 'monospace' }}
                            />
                            <Bar dataKey="shap_value" radius={[2, 2, 2, 2]}>
                              {chartData.map((entry, index) => (
                                <Cell
                                  key={`cell-${index}`}
                                  fill={entry.shap_value > 0 ? '#EF4444' : '#10B981'}
                                />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Top Features Breakdown Table */}
                      <div className="overflow-x-auto">
                        <table className="w-full text-left font-mono text-xs">
                          <thead>
                            <tr className="border-b border-slate-800 text-slate-400 bg-slate-900/60">
                              <th className="py-2.5 px-3">Feature Name</th>
                              <th className="py-2.5 px-3">Live Value</th>
                              <th className="py-2.5 px-3">Directional SHAP (φᵢ)</th>
                              <th className="py-2.5 px-3">Impact Effect</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60">
                            {topFeatures.map((f, i) => (
                              <tr key={i} className="hover:bg-slate-900/40 transition">
                                <td className="py-2.5 px-3 font-semibold text-white">{f.feature_name}</td>
                                <td className="py-2.5 px-3 text-sky-400">{f.feature_value.toFixed(2)}</td>
                                <td className={`py-2.5 px-3 font-bold ${f.shap_value > 0 ? 'text-rose-400' : (f.shap_value < 0 ? 'text-emerald-400' : 'text-slate-400')}`}>
                                  {f.shap_value > 0 ? '+' : ''}{(f.shap_value * 100).toFixed(2)}%
                                </td>
                                <td className="py-2.5 px-3">
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                    f.impact_direction === 'INCREASES_RISK'
                                      ? 'bg-rose-950/60 text-rose-400 border border-rose-800/60'
                                      : (f.impact_direction === 'DECREASES_RISK'
                                          ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/60'
                                          : 'bg-slate-800 text-slate-400 border border-slate-700')
                                  }`}>
                                    {f.impact_direction.replace(/_/g, ' ')}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </Card>
                  </div>

                  {/* Right: Deterministic Engineering Physics Warnings */}
                  <div className="space-y-6">
                    <Card
                      title="Deterministic Physics Warnings"
                      subtitle="Hydraulic & mechanical constraints strictly separated from statistical ML"
                      className="border-amber-500/40 bg-amber-950/10"
                    >
                      <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-xl mb-4 text-xs font-sans text-amber-200 leading-relaxed">
                        <b>Engineering Precedence Principle:</b> Physical hydraulics (pore pressure, fracture gradient, swab/surge) take immediate operational priority over statistical model attributions.
                      </div>

                      <div className="space-y-3 font-mono text-xs">
                        {shapData.engineering_warnings.length === 0 ? (
                          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-center">
                            <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1.5" />
                            All deterministic physical limits (ECD, Torque, SPP) within nominal operating envelope.
                          </div>
                        ) : (
                          shapData.engineering_warnings.map((w, idx) => (
                            <div key={idx} className="p-3.5 rounded-xl bg-slate-900/90 border border-amber-700/60 space-y-1.5">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-amber-300 font-mono text-[11px] flex items-center gap-1.5">
                                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                                  {w.factor_name}
                                </span>
                                <Badge variant={w.impact_level === 'HIGH' ? 'danger' : 'warning'} size="sm">
                                  {w.impact_level}
                                </Badge>
                              </div>
                              <p className="text-slate-300 font-sans text-xs leading-normal">{w.description}</p>
                              <div className="text-[10px] text-slate-500 font-mono pt-1">
                                Physics Severity Weight: {(w.contribution_score * 100).toFixed(0)}%
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </Card>

                    <Card title="Methodological Provenance">
                      <div className="space-y-2 text-xs font-mono text-slate-400">
                        <div className="flex items-center justify-between pb-1.5 border-b border-slate-800">
                          <span>Framework:</span>
                          <span className="text-white font-bold">{currentExpl?.methodology || 'shap.TreeExplainer'}</span>
                        </div>
                        <div className="flex items-center justify-between pb-1.5 border-b border-slate-800">
                          <span>Classification:</span>
                          <span className="text-sky-400">{currentExpl?.provenance || '[D] Supervised ML Tree SHAP'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Efficiency Invariant:</span>
                          <span className="text-emerald-400 font-bold">|f(x) - (E + ∑φ)| &lt; 10⁻⁵</span>
                        </div>
                      </div>
                    </Card>
                  </div>
                </div>
              </>
            );
          })()}
        </div>
      )}

      {/* TAB 2: DEPTH EXPLORER & LOOKAHEAD */}
      {activeTab === 'depth_explorer' && (
        <div className="space-y-6">
          <Card title="Interactive Depth Scrubber (0 – 4300 m)" subtitle="Simulate lookahead predictions for prospective drilling depths">
            <div className="space-y-4">
              <div className="flex items-center justify-between font-mono">
                <span className="text-slate-400 text-sm">Target Depth:</span>
                <span className="text-2xl font-bold text-sky-400">{explorerDepth} m</span>
              </div>
              <input
                type="range"
                min="500"
                max="4200"
                step="20"
                value={explorerDepth}
                onChange={(e) => loadDepthExplorer(Number(e.target.value))}
                className="w-full accent-sky-500 h-2 bg-slate-800 rounded-lg cursor-pointer"
              />
              <div className="flex justify-between text-[11px] font-mono text-slate-500">
                <span>500m (Dhekiajuli)</span>
                <span>2000m (Tipam Sand)</span>
                <span>3420m (Barail Sand)</span>
                <span>3800m (Sylhet Limestone)</span>
                <span>4200m (Disang)</span>
              </div>
            </div>
          </Card>

          {explorerData && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card title="Stratigraphic & Risk Outlook">
                <div className="space-y-3 font-mono text-xs">
                  <div>
                    <div className="text-slate-500 text-[10px]">FORMATION HORIZON</div>
                    <div className="text-lg font-bold text-white mt-0.5">{explorerData.formation}</div>
                  </div>
                  <div>
                    <div className="text-slate-500 text-[10px]">OFFSET INCIDENTS IN CORRIDOR (+/-150m)</div>
                    <div className="text-xl font-bold text-amber-400 mt-0.5">{explorerData.offset_incidents_count} recorded events</div>
                  </div>
                  <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                    <div className="text-slate-400 text-[10px] uppercase">Recommended Pre-Treatment</div>
                    <p className="text-slate-200 mt-1 text-[11px] font-sans">{explorerData.recommended_pre_treatment}</p>
                  </div>
                </div>
              </Card>

              <div className="lg:col-span-2">
                <Card title="Forward-Looking Lookahead Timeline (+350m Forecast)">
                  <div className="space-y-2 font-mono text-xs">
                    {timelineData.map((t, idx) => (
                      <div key={idx} className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sky-400">{t.depth}m</span>
                            <span className="text-slate-400 font-sans">({t.formation})</span>
                            <Badge variant={t.status === 'ACTIVE' ? 'primary' : (t.status === 'HIGH_RISK_ZONE' ? 'danger' : 'warning')}>
                              {t.status}
                            </Badge>
                          </div>
                          <div className="text-[11px] text-slate-400 font-sans mt-1">Action: {t.recommended_action}</div>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] text-slate-500">Offset Incidents</span>
                          <div className="font-bold text-amber-400">{t.offset_incidents_count}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: WHAT-IF SIMULATION SANDBOX */}
      {activeTab === 'what_if' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card title="Operational Parameter Controls" subtitle="Modify parameters and evaluate real-time hydraulic impact">
              <div className="space-y-4 font-mono text-xs">
                <div>
                  <label className="text-slate-400 block mb-1">Simulated Mud Weight: {simParams.sim_mud_weight} SG</label>
                  <input
                    type="range" min="1.10" max="1.60" step="0.01" value={simParams.sim_mud_weight}
                    onChange={(e) => setSimParams({ ...simParams, sim_mud_weight: Number(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Simulated Flow Rate: {simParams.sim_flow_rate} gpm</label>
                  <input
                    type="range" min="300" max="800" step="10" value={simParams.sim_flow_rate}
                    onChange={(e) => setSimParams({ ...simParams, sim_flow_rate: Number(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Simulated WOB: {simParams.sim_wob} klbs</label>
                  <input
                    type="range" min="10" max="40" step="1" value={simParams.sim_wob}
                    onChange={(e) => setSimParams({ ...simParams, sim_wob: Number(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Simulated RPM: {simParams.sim_rpm} RPM</label>
                  <input
                    type="range" min="60" max="180" step="5" value={simParams.sim_rpm}
                    onChange={(e) => setSimParams({ ...simParams, sim_rpm: Number(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>
                <button
                  onClick={runWhatIfSimulation}
                  disabled={simLoading || user?.role === 'Viewer'}
                  className={`w-full py-2 rounded-lg font-bold transition flex items-center justify-center gap-2 ${
                    user?.role === 'Viewer'
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                      : 'bg-sky-600 hover:bg-sky-500 text-white'
                  }`}
                  title={user?.role === 'Viewer' ? 'Read-only: Engineer role required' : ''}
                >
                  <Activity className="w-4 h-4" />
                  {user?.role === 'Viewer' ? 'READ-ONLY (VIEWER ROLE)' : (simLoading ? 'CALCULATING...' : 'Recalculate Risk Margins')}
                </button>
              </div>
            </Card>

            {simResult && (
              <div className="lg:col-span-2 space-y-4">
                <Card title="Simulation Outcome & Risk Deltas">
                  <div className="grid grid-cols-3 gap-3 font-mono text-center">
                    <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                      <div className="text-slate-400 text-[10px]">MUD LOSS RISK</div>
                      <div className="text-2xl font-bold text-white mt-1">
                        {(simResult.simulated.risks.MUD_LOSS.probability * 100).toFixed(0)}%
                      </div>
                      <div className={`text-[11px] mt-1 ${simResult.risk_deltas.mud_loss > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {simResult.risk_deltas.mud_loss > 0 ? '+' : ''}{(simResult.risk_deltas.mud_loss * 100).toFixed(0)}% vs Base
                      </div>
                    </div>

                    <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                      <div className="text-slate-400 text-[10px]">STUCK PIPE RISK</div>
                      <div className="text-2xl font-bold text-white mt-1">
                        {(simResult.simulated.risks.STUCK_PIPE.probability * 100).toFixed(0)}%
                      </div>
                      <div className={`text-[11px] mt-1 ${simResult.risk_deltas.stuck_pipe > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {simResult.risk_deltas.stuck_pipe > 0 ? '+' : ''}{(simResult.risk_deltas.stuck_pipe * 100).toFixed(0)}% vs Base
                      </div>
                    </div>

                    <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                      <div className="text-slate-400 text-[10px]">KICK RISK</div>
                      <div className="text-2xl font-bold text-white mt-1">
                        {(simResult.simulated.risks.KICK.probability * 100).toFixed(0)}%
                      </div>
                      <div className={`text-[11px] mt-1 ${simResult.risk_deltas.kick > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                        {simResult.risk_deltas.kick > 0 ? '+' : ''}{(simResult.risk_deltas.kick * 100).toFixed(0)}% vs Base
                      </div>
                    </div>
                  </div>

                  {simResult.warnings.length > 0 && (
                    <div className="mt-4 p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl space-y-1">
                      <div className="flex items-center gap-2 text-rose-400 font-bold text-xs">
                        <AlertTriangle className="w-4 h-4" /> Operational Warnings:
                      </div>
                      {simResult.warnings.map((w: string, idx: number) => (
                        <div key={idx} className="text-[11px] text-slate-300 ml-6">• {w}</div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: NPT & COST INTELLIGENCE */}
      {activeTab === 'npt_cost' && nptData && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
            <Card className="border-l-4 border-l-rose-500">
              <div className="text-[11px] text-slate-400 uppercase">Historical NPT Hours</div>
              <div className="text-3xl font-bold text-white mt-1">{nptData.total_npt_hours} hrs</div>
              <div className="text-[11px] text-rose-400 mt-1">{nptData.total_historical_events} recorded incidents</div>
            </Card>
            <Card className="border-l-4 border-l-amber-500">
              <div className="text-[11px] text-slate-400 uppercase">Total Financial Impact</div>
              <div className="text-3xl font-bold text-amber-400 mt-1">₹{nptData.total_cost_crores} Cr</div>
              <div className="text-[11px] text-slate-400 mt-1">Standard Rig Rate: ₹25L/day</div>
            </Card>
            <Card className="border-l-4 border-l-emerald-500">
              <div className="text-[11px] text-slate-400 uppercase">Projected NWIS Savings</div>
              <div className="text-3xl font-bold text-emerald-400 mt-1">₹{nptData.projected_nwis_savings_crores} Cr</div>
              <div className="text-[11px] text-emerald-400 mt-1">~35% Risk Avoidance</div>
            </Card>
            <Card className="border-l-4 border-l-sky-500">
              <div className="text-[11px] text-slate-400 uppercase">Top NPT Driver</div>
              <div className="text-xl font-bold text-sky-400 mt-1">STUCK PIPE & LOSSES</div>
              <div className="text-[11px] text-slate-400 mt-1">Barail & Kopili Formations</div>
            </Card>
          </div>

          <Card title="NPT Hours Breakdown by Incident Taxonomy">
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={nptData.breakdown} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                  <XAxis dataKey="event_type" stroke="#94A3B8" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#94A3B8" tick={{ fontSize: 11 }} unit=" hrs" />
                  <Tooltip contentStyle={{ backgroundColor: '#0B111E', borderColor: '#1E293B', borderRadius: '8px' }} />
                  <Bar dataKey="npt_hours" name="NPT Duration (Hours)" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}

      {/* TAB 5: RISK HEATMAP & KNOWLEDGE GRAPH */}
      {activeTab === 'heatmap' && (
        <div className="space-y-6">
          <Card title="Stratigraphic Risk Heatmap (Depth vs Incident Frequency)">
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={heatmapData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                  <XAxis dataKey="depth_interval" stroke="#94A3B8" tick={{ fontSize: 10 }} />
                  <YAxis stroke="#94A3B8" tick={{ fontSize: 10 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0B111E', borderColor: '#1E293B', borderRadius: '8px', fontSize: '11px' }} />
                  <Area type="monotone" dataKey="mud_loss_count" name="Mud Loss" stackId="1" stroke="#EF4444" fill="#EF4444" />
                  <Area type="monotone" dataKey="stuck_pipe_count" name="Stuck Pipe" stackId="1" stroke="#F59E0B" fill="#F59E0B" />
                  <Area type="monotone" dataKey="kick_count" name="Kick / Influx" stackId="1" stroke="#DC2626" fill="#DC2626" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {graphData && (
            <Card title="Knowledge Graph Entity Relations Summary" subtitle="Graph linking Wells, Formations, Incident Types, Causes & Mitigations">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-center text-xs">
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-slate-500 text-[10px]">TOTAL NODES</div>
                  <div className="text-2xl font-bold text-sky-400 mt-1">{graphData.total_nodes}</div>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-slate-500 text-[10px]">TOTAL EDGES / LINKS</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{graphData.total_links}</div>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-slate-500 text-[10px]">CORE LITHOLOGY NODES</div>
                  <div className="text-2xl font-bold text-amber-400 mt-1">10</div>
                </div>
                <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                  <div className="text-slate-500 text-[10px]">MITIGATION PROCEDURES</div>
                  <div className="text-2xl font-bold text-purple-400 mt-1">60+</div>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}

      {/* TAB 6: DAILY INTELLIGENCE REPORT */}
      {activeTab === 'daily_report' && reportData && (
        <Card title={reportData.report_title} subtitle="Automated decision-support briefing for morning operational calls">
          <div className="bg-slate-950 p-6 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
            {reportData.markdown_content}
          </div>
        </Card>
      )}
    </div>
  );
};

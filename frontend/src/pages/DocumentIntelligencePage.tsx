import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWell } from '../store/wellContext';
import { useAuth } from '../store/authContext';
import { useTheme } from '../store/themeContext';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { RiskPill } from '../components/common/RiskPill';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, ShieldAlert, Loader2 } from 'lucide-react';

export const DocumentIntelligencePage: React.FC = () => {
  const { activeWell, availableWells } = useWell();
  const { user } = useAuth();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [documents, setDocuments] = useState<any[]>([]);
  const [targetWellId, setTargetWellId] = useState<string>(activeWell?.well_id || 'WELL-001');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    if (activeWell?.well_id) {
      setTargetWellId(activeWell.well_id);
    }
  }, [activeWell?.well_id]);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = () => {
    api.getDocuments().then(setDocuments).catch(console.error);
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || user?.role === 'Viewer') return;
    setUploading(true);

    try {
      const res = await api.uploadDocument(selectedFile, targetWellId);
      setUploadResult(res);
      loadDocs();
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
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
            <FileText className="w-3.5 h-3.5 text-sky-500" />
            <span className="text-[11px] font-sans text-sky-600 dark:text-sky-400 font-semibold uppercase tracking-wider">
              Document Intelligence & Ingestion Pipeline
            </span>
          </div>
          <h1 className="text-xl font-bold font-sans text-slate-900 dark:text-white tracking-tight">
            Drilling Report Extraction & Processing
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-sans mt-0.5">
            Upload PDF/TXT Daily Drilling Reports (DDR) and Well Completion Reports (WCR) for automated entity & event extraction.
          </p>
        </div>

        <Badge variant="primary" size="md">{documents.length} Ingested Documents</Badge>
      </div>

      {/* Upload Zone */}
      <Card title="Upload New Drilling Report (PDF / TXT / CSV)">
        {user?.role === 'Viewer' && (
          <div className={`mb-3 p-2.5 rounded-md flex items-center gap-2 text-xs font-sans border ${
            isDark ? 'bg-amber-950/30 border-amber-800/50 text-amber-300' : 'bg-amber-50 border-amber-200 text-amber-900'
          }`}>
            <ShieldAlert className="w-4 h-4 shrink-0 text-amber-500" />
            <span>[Viewer Role] Ingestion and extraction are restricted to Drilling Engineer and Administrator roles.</span>
          </div>
        )}

        <form onSubmit={handleFileUpload} className="space-y-3 font-sans text-xs">
          <div className={`flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-2.5 rounded-md border ${
            isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
          }`}>
            <span className="font-medium text-slate-600 dark:text-slate-400">Target Well Context:</span>
            <select
              value={targetWellId}
              onChange={(e) => setTargetWellId(e.target.value)}
              disabled={user?.role === 'Viewer'}
              className={`rounded-md px-2.5 py-1 text-xs font-sans transition border focus:outline-none focus:border-sky-500 ${
                isDark ? 'bg-slate-800 border-slate-700 text-white' : 'bg-white border-slate-300 text-slate-900'
              }`}
            >
              {availableWells.map((w) => (
                <option key={w.well_id} value={w.well_id}>
                  {w.well_id} — {w.well_name} ({w.field})
                </option>
              ))}
            </select>
          </div>

          <div className={`border-2 border-dashed rounded-lg p-6 text-center transition ${
            isDark
              ? 'border-slate-700 hover:border-sky-500 bg-slate-900/30'
              : 'border-slate-300 hover:border-sky-500 bg-slate-50/50'
          }`}>
            <Upload className="w-8 h-8 text-sky-500 mx-auto mb-2" />
            <div className="text-xs font-bold text-slate-800 dark:text-white">
              {selectedFile ? selectedFile.name : 'Select or drop Daily Drilling Report'}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Supports .pdf, .txt, .csv formats (Institutional Drilling Reports)
            </p>
            <input
              type="file"
              accept=".pdf,.txt,.csv"
              disabled={user?.role === 'Viewer'}
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              className="mt-3 text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-sky-600 file:text-white hover:file:bg-sky-500 cursor-pointer disabled:opacity-50"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={uploading || !selectedFile || user?.role === 'Viewer'}
              className={`px-4 py-2 rounded-md font-sans font-semibold text-xs transition flex items-center gap-1.5 shadow-xs ${
                user?.role === 'Viewer'
                  ? 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
                  : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-600/20'
              }`}
            >
              {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5" />}
              <span>{user?.role === 'Viewer' ? 'READ-ONLY ACCESS' : (uploading ? 'PARSING & EXTRACTING...' : 'RUN EXTRACTION PIPELINE')}</span>
            </button>
          </div>
        </form>
      </Card>

      {/* Extraction Results Preview */}
      {uploadResult && (
        <Card
          title="Extracted Knowledge & Event Preview"
          subtitle={`Document: ${uploadResult.filename} (Confidence: ${((uploadResult.extracted_events?.[0]?.confidence ?? 0.95) * 100).toFixed(0)}%)`}
          className="border-emerald-500/30"
        >
          <div className="space-y-3 font-sans text-xs">
            <div className={`flex items-center gap-2.5 p-2.5 rounded-md border ${
              isDark ? 'bg-emerald-950/30 border-emerald-700/50 text-emerald-300' : 'bg-emerald-50 border-emerald-200 text-emerald-900'
            }`}>
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
              <div>
                <div className="font-semibold">Extraction Succeeded & Saved to Knowledge Repository</div>
                <div className="text-[11px] opacity-90">
                  Successfully identified {uploadResult.extracted_events_count || (uploadResult.extracted_events || []).length} structured drilling events with full mitigation history.
                </div>
              </div>
            </div>

            {(uploadResult.extracted_events || []).map((ev: any, idx: number) => (
              <div key={idx} className={`p-3 rounded-md border space-y-1.5 ${
                isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-50 border-slate-200'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-900 dark:text-white">{ev.well_name || 'Active Rig'} &bull; {ev.formation || 'Barail Sandstone'}</span>
                  <RiskPill level={ev.severity || 'HIGH'} />
                </div>
                <div className="text-amber-600 dark:text-amber-400 font-semibold">{ev.event_type || 'Drilling Hazard'} @ <span className="font-mono">{ev.start_depth || 3200} m</span></div>
                <p className="text-xs text-slate-700 dark:text-slate-300"><b>Cause:</b> {ev.cause || 'Permeability transition'}</p>
                <p className="text-xs text-emerald-600 dark:text-emerald-400"><b>Mitigation:</b> {ev.mitigation || 'LCM pill'}</p>
                <p className="text-xs text-purple-600 dark:text-purple-400"><b>Lesson Learned:</b> {ev.lesson_learned || 'Maintain circulation'}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Ingested Document Inventory */}
      <Card title="Ingested Drilling Document Inventory">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-sans text-xs">
            <thead>
              <tr className={`border-b ${isDark ? 'border-slate-800 text-slate-400 bg-slate-900/30' : 'border-slate-100 text-slate-500 bg-slate-50/60'}`}>
                <th className="py-2.5 px-3 font-semibold">Filename</th>
                <th className="py-2.5 px-3 font-semibold">Type</th>
                <th className="py-2.5 px-3 font-semibold">Pages</th>
                <th className="py-2.5 px-3 font-semibold">Extracted Events</th>
                <th className="py-2.5 px-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className={`divide-y ${isDark ? 'divide-slate-800/60' : 'divide-slate-100'}`}>
              {(Array.isArray(documents) ? documents : []).map((doc, idx) => (
                <tr key={doc.document_id || doc.doc_id || idx} className={`${isDark ? 'hover:bg-slate-900/40' : 'hover:bg-slate-50'} transition`}>
                  <td className="py-2.5 px-3 font-semibold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-sky-500" />
                    <span>{doc.filename}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-500 dark:text-slate-400">{doc.file_type}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-700 dark:text-slate-300">{doc.total_pages}</td>
                  <td className="py-2.5 px-3 font-mono text-emerald-600 dark:text-emerald-400 font-semibold">{doc.extracted_events_count} events</td>
                  <td className="py-2.5 px-3">
                    <Badge variant="success">{doc.processing_status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

import React, { useState } from 'react';
import { useAuth, AuthProvider } from './store/authContext';
import { ThemeProvider, useTheme } from './store/themeContext';
import { WellProvider } from './store/wellContext';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';

import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ActiveWellPage } from './pages/ActiveWellPage';
import { NearbyWellsMapPage } from './pages/NearbyWellsMapPage';
import { WellComparisonPage } from './pages/WellComparisonPage';
import { KnowledgeRepoPage } from './pages/KnowledgeRepoPage';
import { AssistantSearchPage } from './pages/AssistantSearchPage';
import { DocumentIntelligencePage } from './pages/DocumentIntelligencePage';
import { RiskAnalyticsPage } from './pages/RiskAnalyticsPage';
import { AlertsCenterPage } from './pages/AlertsCenterPage';
import { SystemStatusPage } from './pages/SystemStatusPage';

// ── Global Error Boundary ─────────────────────────────────────────────────────
interface EBState { hasError: boolean; error: Error | null; }

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, EBState> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): EBState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[NWIS] Unhandled render error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '100vh', background: '#080C14',
          color: '#e2e8f0', fontFamily: 'sans-serif', padding: '2rem', gap: '1rem'
        }}>
          <div style={{ fontSize: 48 }}>⚠️</div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f87171', margin: 0 }}>
            NWIS — Application Error
          </h1>
          <p style={{ color: '#94a3b8', textAlign: 'center', maxWidth: 480, margin: 0 }}>
            A component crashed. Open the browser console (F12) for details.
          </p>
          <pre style={{
            background: '#0f172a', border: '1px solid #334155', borderRadius: 8,
            padding: '1rem', fontSize: 12, color: '#f87171', maxWidth: 640,
            whiteSpace: 'pre-wrap', wordBreak: 'break-all'
          }}>
            {this.state.error?.message}
          </pre>
          <button
            onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload(); }}
            style={{
              background: '#0284c7', color: '#fff', border: 'none', borderRadius: 8,
              padding: '0.6rem 1.5rem', fontSize: 14, fontWeight: 600, cursor: 'pointer'
            }}
          >
            Reload App
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── Main Content ──────────────────────────────────────────────────────────────
const MainAppContent: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { theme } = useTheme();
  const [currentPage, setCurrentPage] = useState<string>('dashboard');

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':     return <DashboardPage onNavigate={setCurrentPage} />;
      case 'active-well':   return <ActiveWellPage />;
      case 'map':           return <NearbyWellsMapPage />;
      case 'comparison':    return <WellComparisonPage />;
      case 'knowledge-repo':return <KnowledgeRepoPage />;
      case 'assistant':     return <AssistantSearchPage />;
      case 'documents':     return <DocumentIntelligencePage />;
      case 'risk-analytics':return <RiskAnalyticsPage />;
      case 'alerts':        return <AlertsCenterPage />;
      case 'system-status': return <SystemStatusPage />;
      default:              return <DashboardPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className={`h-screen w-screen flex flex-col font-sans transition-colors duration-200 overflow-hidden ${
      theme === 'dark' ? 'bg-[#080C14] text-slate-100' : 'bg-slate-50 text-slate-900'
    }`}>
      <div className="shrink-0 z-30">
        <Navbar onNavigate={setCurrentPage} />
      </div>
      <div className="flex-1 flex overflow-hidden min-h-0">
        <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className={`flex-1 h-full overflow-y-auto p-6 transition-colors duration-200 min-h-0 ${
          theme === 'dark' ? 'bg-[#080C14]' : 'bg-slate-50'
        }`}>
          <ErrorBoundary>
            {renderPage()}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => (
  <ErrorBoundary>
    <AuthProvider>
      <ThemeProvider>
        <WellProvider>
          <MainAppContent />
        </WellProvider>
      </ThemeProvider>
    </AuthProvider>
  </ErrorBoundary>
);

export default App;

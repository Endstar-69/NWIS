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

const MainAppContent: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const { theme } = useTheme();
  const [currentPage, setCurrentPage] = useState<string>('dashboard');

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage onNavigate={setCurrentPage} />;
      case 'active-well':
        return <ActiveWellPage />;
      case 'map':
        return <NearbyWellsMapPage />;
      case 'comparison':
        return <WellComparisonPage />;
      case 'knowledge-repo':
        return <KnowledgeRepoPage />;
      case 'assistant':
        return <AssistantSearchPage />;
      case 'documents':
        return <DocumentIntelligencePage />;
      case 'risk-analytics':
        return <RiskAnalyticsPage />;
      case 'alerts':
        return <AlertsCenterPage />;
      case 'system-status':
        return <SystemStatusPage />;
      default:
        return <DashboardPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className={`h-screen w-screen flex flex-col font-sans transition-colors duration-200 overflow-hidden ${
      theme === 'dark' ? 'bg-[#080C14] text-slate-100' : 'bg-slate-50 text-slate-900'
    }`}>
      {/* Top Navbar */}
      <div className="shrink-0 z-30">
        <Navbar onNavigate={setCurrentPage} />
      </div>

      {/* Main Body with Sidebar + Active View */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className={`flex-1 h-full overflow-y-auto p-6 transition-colors duration-200 min-h-0 ${
          theme === 'dark' ? 'bg-[#080C14]' : 'bg-slate-50'
        }`}>
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <ThemeProvider>
        <WellProvider>
          <MainAppContent />
        </WellProvider>
      </ThemeProvider>
    </AuthProvider>
  );
};

export default App;

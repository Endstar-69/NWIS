import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { useTheme } from '../../store/themeContext';

export const DemoBanner: React.FC = () => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <div className={`px-4 py-1.5 text-xs font-mono flex items-center justify-between border-b shadow-inner transition-colors ${
      isDark
        ? 'bg-amber-950/80 border-amber-600/40 text-amber-200'
        : 'bg-amber-50 border-amber-300 text-amber-900'
    }`}>
      <div className="flex items-center gap-2">
        <span className="flex h-2 w-2 relative">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isDark ? 'bg-amber-400' : 'bg-amber-500'} opacity-75`}></span>
          <span className={`relative inline-flex rounded-full h-2 w-2 ${isDark ? 'bg-amber-500' : 'bg-amber-600'}`}></span>
        </span>
        <AlertTriangle className={`w-3.5 h-3.5 ${isDark ? 'text-amber-400' : 'text-amber-600'}`} />
        <span className="font-bold tracking-wide">PROTOTYPE DEMO ENVIRONMENT</span>
        <span className={`hidden md:inline ${isDark ? 'text-amber-300/70' : 'text-amber-700/70'}`}>|</span>
        <span className={`hidden md:inline ${isDark ? 'text-amber-300/80' : 'text-amber-800'}`}>Synthetic Assam-Arakan Basin Data & ML Models (Not for Real-Life Well Operations)</span>
      </div>
      <div className="flex items-center gap-3">
        <span className={`px-2 py-0.5 rounded border text-[10px] uppercase tracking-wider font-semibold ${
          isDark
            ? 'bg-amber-900/60 text-amber-300 border-amber-600/30'
            : 'bg-amber-100 text-amber-900 border-amber-300'
        }`}>
          OIL HACKATHON BUILD v1.0
        </span>
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../store/authContext';
import { useTheme } from '../../store/themeContext';
import { useWell } from '../../store/wellContext';
import { api } from '../../services/api';
import {
  Bell, UserCircle, Activity, Search, ChevronDown, Sun, Moon, LogOut
} from 'lucide-react';

interface NavbarProps {
  onNavigate?: (page: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  const { activeWell, availableWells, activeDepth, activeFormation, setActiveWellId } = useWell();
  const [activeAlertsCount, setActiveAlertsCount] = useState(2);
  const [isWellMenuOpen, setIsWellMenuOpen] = useState(false);

  useEffect(() => {
    api.getAlerts(undefined, 'NEW').then((alerts) => {
      setActiveAlertsCount(alerts.length);
    }).catch(() => {});
  }, []);

  return (
    <nav className={`${
      isDark ? 'bg-[#0B111E] border-slate-800 text-slate-100' : 'bg-white border-slate-200 text-slate-900'
    } border-b px-4 py-2 flex items-center justify-between shadow-xs transition-colors z-30`}>
      {/* Brand & Active Rig Status */}
      <div className="flex items-center gap-5">
        <div
          className="flex items-center gap-2.5 cursor-pointer select-none group"
          onClick={() => onNavigate && onNavigate('dashboard')}
        >
          <div className={`p-1.5 rounded-md ${
            isDark ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30' : 'bg-sky-50 text-sky-600 border border-sky-200'
          }`}>
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold font-sans tracking-tight text-sm text-slate-900 dark:text-white">NWIS</span>
              <span className={`text-[10px] font-sans font-semibold px-1.5 py-0.2 rounded border ${
                isDark ? 'bg-sky-950/60 text-sky-400 border-sky-800/50' : 'bg-sky-50 text-sky-700 border-sky-200'
              }`}>
                OIL INDIA
              </span>
            </div>
            <p className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-slate-500'} font-sans leading-none mt-0.5`}>
              Nearby Wells Intelligence System
            </p>
          </div>
        </div>

        {/* Dynamic Active Well Live Telemetry Capsule & Selector */}
        <div className="relative hidden md:block">
          <button
            onClick={() => setIsWellMenuOpen(!isWellMenuOpen)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-sans transition border ${
              isDark
                ? 'bg-slate-900/80 hover:bg-slate-800/90 border-slate-700/80 text-slate-200'
                : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-800'
            }`}
            title="Switch active drilling well context"
          >
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-semibold text-slate-400 dark:text-slate-400 uppercase tracking-wide">ACTIVE:</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              {activeWell ? `${activeWell.well_id} (${activeWell.well_name})` : 'Loading...'}
            </span>
            <span className="text-slate-300 dark:text-slate-600">|</span>
            <span className="font-mono font-bold text-slate-700 dark:text-slate-200">{activeDepth.toFixed(1)} m</span>
            <span className="text-slate-300 dark:text-slate-600">|</span>
            <span className="text-amber-600 dark:text-amber-400 font-medium">{activeFormation}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
          </button>

          {/* Well Selector Dropdown */}
          {isWellMenuOpen && (
            <div className={`absolute left-0 mt-1.5 w-80 ${
              isDark ? 'bg-[#0F172A] border-slate-700' : 'bg-white border-slate-200'
            } border rounded-lg shadow-xl py-1.5 z-50`}>
              <div className={`px-3 py-1 text-[10px] font-sans font-semibold uppercase tracking-wider border-b ${
                isDark ? 'text-slate-400 border-slate-800' : 'text-slate-500 border-slate-100'
              } flex justify-between items-center`}>
                <span>Select Active Well Context</span>
                <span className="text-sky-500 font-bold">{availableWells.length} Wells</span>
              </div>
              <div className="max-h-60 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60">
                {availableWells.map((w) => (
                  <button
                    key={w.well_id}
                    onClick={() => {
                      setActiveWellId(w.well_id);
                      setIsWellMenuOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between transition ${
                      activeWell?.well_id === w.well_id
                        ? (isDark ? 'bg-sky-950/40 text-sky-400 font-semibold' : 'bg-sky-50 text-sky-700 font-semibold')
                        : (isDark ? 'text-slate-300 hover:bg-slate-800/60' : 'text-slate-700 hover:bg-slate-50')
                    }`}
                  >
                    <div>
                      <div className="font-sans font-medium">{w.well_id} — {w.well_name}</div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 font-sans">
                        {w.field} &bull; Depth: <span className="font-mono">{w.current_depth?.toFixed(1) || '0.0'} m</span>
                      </div>
                    </div>
                    {activeWell?.well_id === w.well_id && (
                      <span className="text-[9px] font-sans font-bold bg-emerald-500/15 text-emerald-500 border border-emerald-500/30 px-1.5 py-0.2 rounded">ACTIVE</span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2">
        {/* Quick Assistant Search Shortcut */}
        <button
          onClick={() => onNavigate && onNavigate('assistant')}
          className={`hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-sans transition border ${
            isDark
              ? 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-700/80'
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
          }`}
        >
          <Search className="w-3.5 h-3.5 text-sky-500" />
          <span>Ask Knowledge...</span>
          <kbd className={`px-1.5 py-0.2 rounded text-[10px] font-mono border ${
            isDark ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-slate-200 text-slate-600 border-slate-300'
          }`}>⌘K</kbd>
        </button>

        {/* Light / Dark Mode Toggle */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          className={`p-1.5 rounded-md border transition flex items-center justify-center ${
            isDark
              ? 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-700/80'
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
          }`}
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-sky-600" />
          )}
        </button>

        {/* Alerts Bell */}
        <button
          onClick={() => onNavigate && onNavigate('alerts')}
          className={`relative p-1.5 rounded-md border transition ${
            isDark
              ? 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-700/80'
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
          }`}
          title="Active Alerts"
        >
          <Bell className="w-4 h-4 text-amber-500" />
          {activeAlertsCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-rose-600 text-white font-mono text-[9px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
              {activeAlertsCount}
            </span>
          )}
        </button>

        {/* User Identity & Direct Sign Out */}
        <div className={`flex items-center gap-1.5 pl-2 border-l ${
          isDark ? 'border-slate-800' : 'border-slate-200'
        }`}>
          <div
            className={`p-1.5 rounded-md border relative cursor-default ${
              isDark ? 'bg-slate-900 border-slate-700/80 text-sky-400' : 'bg-slate-50 border-slate-200 text-sky-600'
            }`}
            title={`${user?.full_name || 'Drilling Lead'} (${user?.username || 'driller'})`}
          >
            <UserCircle className="w-4 h-4" />
            <span className="absolute bottom-1 right-1 w-1.5 h-1.5 rounded-full bg-emerald-500 ring-1 ring-white dark:ring-slate-900" />
          </div>

          <button
            onClick={logout}
            title="Sign Out"
            className={`p-1.5 rounded-md border transition ${
              isDark
                ? 'bg-slate-900 hover:bg-rose-950/40 border-slate-700/80 hover:border-rose-700/50 text-slate-400 hover:text-rose-300'
                : 'bg-slate-50 hover:bg-rose-50 border-slate-200 hover:border-rose-300 text-slate-500 hover:text-rose-600'
            }`}
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </nav>
  );
};

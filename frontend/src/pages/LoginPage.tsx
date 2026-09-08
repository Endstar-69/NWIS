import React, { useState } from 'react';
import { useAuth } from '../store/authContext';
import { Activity, Shield, ArrowRight, Lock, UserCircle, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('driller');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      setError('Please enter a valid username');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await login(username.trim(), password);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Authentication failed. Please verify credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080C14] flex flex-col justify-between text-slate-100 font-sans relative overflow-hidden">
      {/* Header */}
      <header className="px-6 py-4 flex items-center justify-between border-b border-slate-800/80 bg-[#0B111E]">
        <div className="flex items-center gap-3">
          <div className="bg-sky-500/10 border border-sky-500/30 p-2 rounded-md text-sky-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold font-sans tracking-tight text-white">NWIS</h1>
              <span className="text-[10px] bg-sky-950/60 text-sky-400 border border-sky-800/60 px-1.5 py-0.2 rounded font-semibold">
                OIL INDIA LIMITED
              </span>
            </div>
            <p className="text-xs text-slate-400">Nearby Wells Intelligence System</p>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-1.5 rounded-md text-slate-400" title="Operational Decision Support Console">
          <Shield className="w-4 h-4 text-sky-400" />
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-md mx-auto w-full px-6 py-10 my-auto">
        <div className="text-center mb-6">
          <span className="text-xs font-sans font-semibold tracking-wider text-sky-400 uppercase bg-sky-500/10 px-2.5 py-0.5 rounded border border-sky-500/20">
            Console Authentication
          </span>
          <h2 className="text-2xl font-bold tracking-tight text-white mt-2 font-sans">
            Sign In to NWIS
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto leading-relaxed">
            Unified access to real-time telemetry, predictive anti-collision, lithology correlation, and operational decision support.
          </p>
        </div>

        {/* Login Form Card */}
        <div className="bg-[#0B111E] border border-slate-800 rounded-lg p-6 shadow-xl">
          {error && (
            <div className="mb-4 p-3 rounded-md bg-rose-950/30 border border-rose-600/50 flex items-start gap-2 text-xs text-rose-300 font-sans">
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5 text-xs font-sans">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1 flex items-center gap-1.5">
                <UserCircle className="w-3.5 h-3.5 text-sky-400" />
                Username / Operator ID
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-md text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
                placeholder="driller"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1 flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-sky-400" />
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700/80 rounded-md text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
                placeholder="••••••••"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 rounded-md bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs transition flex items-center justify-center gap-2 disabled:opacity-50 shadow-xs"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <Shield className="w-3.5 h-3.5" />
                    <span>Sign In to NWIS Console</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Preset Access Info */}
          <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-sans">
            <span className="flex items-center gap-1 text-emerald-400">
              <CheckCircle2 className="w-3 h-3" /> Full Operational Access
            </span>
            <span className="text-slate-500">Default: driller</span>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="p-4 border-t border-slate-900 text-center text-xs text-slate-500 font-sans">
        NWIS Prototype &bull; OIL India Limited &bull; Nearby Wells Intelligence System
      </footer>
    </div>
  );
};

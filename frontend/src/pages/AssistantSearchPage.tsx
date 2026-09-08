import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { useWell } from '../store/wellContext';
import { useAuth } from '../store/authContext';
import { useTheme } from '../store/themeContext';
import { UnifiedSearchResponse, SearchResult, SearchHistoryItem } from '../types';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import {
  Bot, Search, Send, BookOpen, ShieldCheck, AlertTriangle,
  History, RotateCcw, FileText, ChevronRight, CheckCircle2,
  Info, ArrowRight, Loader2, Sparkles, HelpCircle, Compass
} from 'lucide-react';

interface ChatTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: UnifiedSearchResponse;
  timestamp: string;
}

export const AssistantSearchPage: React.FC = () => {
  const { activeWell, activeDepth, activeFormation } = useWell();
  const { user } = useAuth();
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const [activeTab, setActiveTab] = useState<'assistant' | 'semantic' | 'history'>('assistant');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);

  // Dynamic suggestions fetched from backend based on active well/horizon
  const [dynamicSuggestions, setDynamicSuggestions] = useState<string[]>([]);

  // Conversation state
  const [conversationId, setConversationId] = useState<string>('');
  const [chatTurns, setChatTurns] = useState<ChatTurn[]>([]);

  // Raw vector search state
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);

  // Past search history
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);

  const chatBottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const loadingMessages = [
    'Searching institutional knowledge base...',
    'Retrieving offset well logs and DDRs...',
    'Correlating geological formations & risks...',
    'Synthesizing grounded engineering response...'
  ];

  // Fetch dynamic suggestions whenever active well, depth, or formation updates
  useEffect(() => {
    let isMounted = true;
    const fetchSuggestions = async () => {
      try {
        const suggs = await api.getSearchSuggestions(
          activeWell?.well_id,
          activeDepth,
          activeFormation
        );
        if (isMounted && suggs && suggs.length > 0) {
          setDynamicSuggestions(suggs);
        }
      } catch (err) {
        console.error('Failed to load dynamic suggestions:', err);
      }
    };
    fetchSuggestions();
    return () => { isMounted = false; };
  }, [activeWell?.well_id, activeDepth, activeFormation]);

  // Fetch search history when history tab is opened
  useEffect(() => {
    if (activeTab === 'history') {
      api.getSearchHistory().then(setSearchHistory).catch(console.error);
    }
  }, [activeTab]);

  // Loading animation progression
  useEffect(() => {
    let timer: any;
    if (loading) {
      setLoadingStep(0);
      timer = setInterval(() => {
        setLoadingStep((prev) => (prev < loadingMessages.length - 1 ? prev + 1 : prev));
      }, 700);
    }
    return () => clearInterval(timer);
  }, [loading]);

  // Scroll smoothly to bottom whenever new turn or loading state changes
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatTurns, loading]);

  const handleAsk = async (textToAsk?: string) => {
    const q = (textToAsk || query).trim();
    if (!q) return;

    if (activeTab === 'semantic') {
      setLoading(true);
      try {
        const results = await api.searchSemantic(q, activeDepth, activeFormation);
        setSearchResults(results);
      } catch (err) {
        console.error('Vector search error:', err);
      } finally {
        setLoading(false);
      }
      return;
    }

    // AI Assistant flow
    const userTurn: ChatTurn = {
      id: `turn-user-${Date.now()}`,
      role: 'user',
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setChatTurns((prev) => [...prev, userTurn]);
    setQuery('');
    setLoading(true);

    try {
      const res = await api.unifiedSearch({
        query: q,
        well_id: activeWell?.well_id || 'WELL-001',
        depth: activeDepth,
        formation: activeFormation,
        conversation_id: conversationId || undefined
      });

      if (res.conversation_id) {
        setConversationId(res.conversation_id);
      }

      const assistantTurn: ChatTurn = {
        id: `turn-asst-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        response: res,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setChatTurns((prev) => [...prev, assistantTurn]);
    } catch (err) {
      console.error('Unified search error:', err);
      const errorTurn: ChatTurn = {
        id: `turn-err-${Date.now()}`,
        role: 'assistant',
        content: `### Query Execution Error\n\nUnable to retrieve knowledge response. Please verify backend connection and API configuration.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setChatTurns((prev) => [...prev, errorTurn]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const startNewConversation = () => {
    setChatTurns([]);
    setConversationId('');
    setQuery('');
    inputRef.current?.focus();
  };

  const defaultStarterQueries = [
    { label: 'Lost Circulation Mitigations', query: `What happened in nearby wells around ${activeDepth.toFixed(0)} m in ${activeFormation}?` },
    { label: 'Differential Sticking Offset Logs', query: `Which offset wells experienced stuck pipe in ${activeFormation}?` },
    { label: 'Historical Mitigations at Depth', query: `Show previous stuck pipe mitigations around ${activeDepth.toFixed(0)} m.` },
    { label: 'Gas Kick Warning Indicators', query: `What are the historical gas kick warning signs in ${activeFormation}?` }
  ];

  return (
    <div className="h-[calc(100vh-80px)] flex flex-col max-w-5xl mx-auto font-sans pb-2">
      {/* 1. Header Banner & Mode Selector */}
      <div className={`p-3.5 rounded-lg border transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0 mb-3 ${
        isDark ? 'bg-[#0B111E] border-slate-800/90 text-slate-100' : 'bg-white border-slate-200 text-slate-900 shadow-xs'
      }`}>
        <div>
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-sky-500" />
            <h1 className="text-base font-bold font-sans tracking-tight text-slate-900 dark:text-white">
              NWIS Knowledge Assistant
            </h1>
            <span className="text-[10px] font-sans font-semibold px-1.5 py-0.2 rounded border bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20">
              RAG ENGINE
            </span>
          </div>

          <div className="flex items-center gap-2 mt-1 text-xs text-slate-500 dark:text-slate-400">
            <span>Grounding:</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">{activeWell?.well_name || activeWell?.well_id || 'Active Well'}</span>
            <span>&bull;</span>
            <span className="font-mono font-bold text-slate-700 dark:text-slate-200">{activeDepth.toFixed(1)} m</span>
            <span>&bull;</span>
            <span className="text-amber-600 dark:text-amber-400 font-medium">{activeFormation}</span>
          </div>
        </div>

        {/* Tab Selector & Controls */}
        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-1 p-1 rounded-md border text-xs font-sans ${
            isDark ? 'bg-slate-900/80 border-slate-800' : 'bg-slate-50 border-slate-200'
          }`}>
            <button
              onClick={() => setActiveTab('assistant')}
              className={`px-2.5 py-1 rounded text-xs font-sans transition ${
                activeTab === 'assistant'
                  ? 'bg-sky-600 text-white font-semibold shadow-xs'
                  : (isDark ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900')
              }`}
            >
              AI Assistant
            </button>
            <button
              onClick={() => { setActiveTab('semantic'); setSearchResults([]); }}
              className={`px-2.5 py-1 rounded text-xs font-sans transition ${
                activeTab === 'semantic'
                  ? 'bg-sky-600 text-white font-semibold shadow-xs'
                  : (isDark ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900')
              }`}
            >
              Vector Search
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-2.5 py-1 rounded text-xs font-sans transition flex items-center gap-1 ${
                activeTab === 'history'
                  ? 'bg-sky-600 text-white font-semibold shadow-xs'
                  : (isDark ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 hover:text-slate-900')
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>History</span>
            </button>
          </div>

          {activeTab === 'assistant' && chatTurns.length > 0 && (
            <button
              onClick={startNewConversation}
              className={`p-1.5 rounded-md border text-xs font-sans transition flex items-center gap-1 ${
                isDark
                  ? 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
                  : 'bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700'
              }`}
              title="Reset Conversation"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
              <span className="hidden sm:inline">New Session</span>
            </button>
          )}
        </div>
      </div>

      {/* 2. Scrollable Thread / Results Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 min-h-0">
        {/* Assistant Tab View */}
        {activeTab === 'assistant' && (
          <>
            {/* Empty State / Quick Investigation Starters */}
            {chatTurns.length === 0 && !loading && (
              <div className={`p-8 rounded-lg border text-center transition-colors my-auto ${
                isDark ? 'bg-[#0B111E] border-slate-800/80' : 'bg-white border-slate-200 shadow-xs'
              }`}>
                <div className="w-10 h-10 rounded-full bg-sky-500/10 text-sky-500 flex items-center justify-center mx-auto mb-3">
                  <Bot className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold font-sans text-slate-900 dark:text-white">
                  Institutional Drilling Knowledge Inquiry
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
                  Query verified offset reports, lost circulation mitigations, bit programs, and formation pore pressure records in the Assam-Arakan Basin.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-xl mx-auto mt-6 text-left">
                  {defaultStarterQueries.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuery(item.query);
                        handleAsk(item.query);
                      }}
                      className={`p-3 rounded-md border text-xs font-sans transition flex flex-col justify-between ${
                        isDark
                          ? 'bg-slate-900/60 border-slate-800 hover:border-sky-500/50 hover:bg-slate-800/80 text-slate-300'
                          : 'bg-slate-50 border-slate-200 hover:border-sky-400 hover:bg-white text-slate-700 shadow-2xs'
                      }`}
                    >
                      <span className="font-semibold text-sky-600 dark:text-sky-400 text-[11px] mb-1">{item.label}</span>
                      <span className="text-[11px] opacity-80 line-clamp-2">{item.query}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Conversation Turns Stream */}
            {chatTurns.map((turn) => (
              <div key={turn.id} className="space-y-3">
                {turn.role === 'user' ? (
                  <div className="flex justify-end">
                    <div className={`px-4 py-2.5 rounded-lg max-w-xl text-xs font-sans border shadow-xs ${
                      isDark
                        ? 'bg-sky-950/40 border-sky-700/50 text-sky-100'
                        : 'bg-sky-50 border-sky-200 text-sky-900'
                    }`}>
                      <p className="leading-relaxed font-medium">{turn.content}</p>
                      <span className="block text-right text-[10px] opacity-70 font-mono mt-1">
                        {turn.timestamp}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Card
                      title="Grounded Drilling Intelligence Response"
                      subtitle="Synthesized strictly against institutional drilling records"
                      className="border-sky-500/30 dark:border-sky-500/40"
                      headerAction={
                        <div className="flex items-center gap-2 flex-wrap">
                          {turn.response?.answer_type === 'historical_evidence' && (
                            <Badge variant="success" size="sm">
                              <ShieldCheck className="w-3 h-3 text-emerald-500" />
                              <span>NWIS Historical Evidence</span>
                            </Badge>
                          )}
                          {turn.response?.answer_type === 'general_knowledge' && (
                            <Badge variant="primary" size="sm">
                              <BookOpen className="w-3 h-3 text-sky-500" />
                              <span>General Drilling Knowledge</span>
                            </Badge>
                          )}
                          {turn.response?.answer_type === 'insufficient_evidence' && (
                            <Badge variant="warning" size="sm">
                              <AlertTriangle className="w-3 h-3 text-amber-500" />
                              <span>Insufficient Evidence</span>
                            </Badge>
                          )}
                          {turn.response?.confidence && (
                            <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${
                              isDark ? 'bg-slate-800 text-slate-300 border-slate-700' : 'bg-slate-100 text-slate-700 border-slate-200'
                            }`}>
                              Confidence: {(turn.response.confidence * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                      }
                    >
                      {/* Operational Warnings */}
                      {turn.response?.warnings && turn.response.warnings.length > 0 && (
                        <div className={`mb-3 p-3 rounded-md border text-xs font-sans flex items-start gap-2.5 ${
                          isDark ? 'bg-amber-950/20 border-amber-600/40 text-amber-200' : 'bg-amber-50 border-amber-300 text-amber-900'
                        }`}>
                          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                          <div className="space-y-0.5">
                            {turn.response.warnings.map((w, wi) => (
                              <p key={wi} className="leading-relaxed">{w}</p>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Markdown Answer Text */}
                      <div className={`p-4 rounded-md border text-xs font-sans leading-relaxed whitespace-pre-line ${
                        isDark ? 'bg-slate-900/50 border-slate-800/80 text-slate-200' : 'bg-slate-50 border-slate-200 text-slate-800'
                      }`}>
                        {turn.content}
                      </div>

                      {/* Citations and Evidence Records */}
                      {turn.response?.sources && turn.response.sources.length > 0 && (
                        <div className={`mt-4 pt-3 border-t ${isDark ? 'border-slate-800/80' : 'border-slate-100'} space-y-2.5`}>
                          <div className="text-xs font-sans font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
                            <BookOpen className="w-3.5 h-3.5 text-sky-500" />
                            <span>Grounded Offset Sources & Citations</span>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {turn.response.sources.map((src, si) => (
                              <div
                                key={si}
                                className={`p-2.5 rounded-md border text-xs space-y-1 ${
                                  isDark ? 'bg-slate-900/60 border-slate-800' : 'bg-white border-slate-200 shadow-xs'
                                }`}
                              >
                                <div className="flex items-center justify-between font-sans">
                                  <span className="font-semibold text-sky-600 dark:text-sky-400">{src.well}</span>
                                  {src.relevance && (
                                    <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-1.5 py-0.2 rounded">
                                      {(src.relevance * 100).toFixed(0)}% Match
                                    </span>
                                  )}
                                </div>
                                <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2 font-sans">
                                  <span>Depth: <b className="font-mono text-slate-700 dark:text-slate-300">{src.depth}</b></span>
                                  {src.formation && <span>&bull; {src.formation}</span>}
                                </div>
                                {src.event && (
                                  <div className="text-[11px] text-amber-600 dark:text-amber-400 font-sans">
                                    Event: <b>{src.event}</b>
                                  </div>
                                )}
                                <div className="text-[10px] text-slate-400 font-sans flex items-center gap-1 truncate">
                                  <FileText className="w-3 h-3 shrink-0" />
                                  <span className="truncate">{src.document}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Dynamic Follow-Up Questions */}
                      {turn.response?.follow_up_questions && turn.response.follow_up_questions.length > 0 && (
                        <div className={`mt-4 pt-3 border-t ${isDark ? 'border-slate-800/80' : 'border-slate-100'} space-y-2`}>
                          <div className="text-xs font-sans font-semibold text-slate-500 dark:text-slate-400">
                            Recommended Follow-Up Inquiries:
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {turn.response.follow_up_questions.map((fq, fqi) => (
                              <button
                                key={fqi}
                                onClick={() => {
                                  setQuery(fq);
                                  handleAsk(fq);
                                }}
                                className={`px-2.5 py-1 rounded text-xs font-sans transition flex items-center gap-1.5 border text-left ${
                                  isDark
                                    ? 'bg-slate-900 border-slate-700/80 hover:border-sky-500 text-slate-300 hover:text-sky-300'
                                    : 'bg-slate-50 border-slate-200 hover:border-sky-400 text-slate-700 hover:text-sky-700'
                                }`}
                              >
                                <span>{fq}</span>
                                <ChevronRight className="w-3 h-3 text-slate-400 shrink-0" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </Card>
                  </div>
                )}
              </div>
            ))}

            {/* Live Loading Step Card at bottom of stream */}
            {loading && (
              <div className={`p-4 rounded-lg border transition-colors ${
                isDark ? 'bg-[#0B111E] border-sky-500/30' : 'bg-white border-sky-300 shadow-xs'
              }`}>
                <div className="flex items-center gap-3">
                  <Loader2 className="w-4 h-4 text-sky-500 animate-spin" />
                  <div className="space-y-0.5">
                    <p className="text-xs font-sans font-semibold text-slate-900 dark:text-white">
                      {loadingMessages[loadingStep]}
                    </p>
                    <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400 font-sans">
                      <span>Phase {loadingStep + 1} of {loadingMessages.length}</span>
                      <span>&bull;</span>
                      <span className="text-sky-600 dark:text-sky-400 font-mono">Offset Context: {activeWell?.well_name} ({activeFormation}, {activeDepth.toFixed(0)}m)</span>
                    </div>
                  </div>
                </div>
                <div className={`w-full h-1 rounded-full mt-3 overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-100'}`}>
                  <div
                    className="bg-sky-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${((loadingStep + 1) / loadingMessages.length) * 100}%` }}
                  />
                </div>
              </div>
            )}
            <div ref={chatBottomRef} />
          </>
        )}

        {/* Vector Search Raw Results Tab */}
        {activeTab === 'semantic' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs font-sans text-slate-500 dark:text-slate-400 px-1">
              <span>Raw Vector Similarity Matches ({searchResults.length} records)</span>
            </div>

            {searchResults.length === 0 && !loading && (
              <div className={`p-8 rounded-lg border text-center text-slate-500 dark:text-slate-400 text-xs font-sans ${
                isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200'
              }`}>
                Enter a search query below to inspect dense semantic embedding matches.
              </div>
            )}

            {searchResults.map((item) => (
              <Card
                key={item.event_id}
                title={`${item.well_name} • ${item.event_type}`}
                subtitle={`${item.formation} at ${item.depth.toFixed(1)} m`}
                className="border-slate-800/80 hover:border-slate-700 transition"
                headerAction={
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded">
                      Score: {(item.similarity_score * 100).toFixed(1)}%
                    </span>
                    <Badge variant={item.severity === 'CRITICAL' ? 'danger' : 'warning'} size="sm">
                      {item.severity}
                    </Badge>
                  </div>
                }
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-sans">
                  <div className="space-y-1">
                    <span className="font-semibold text-slate-500 dark:text-slate-400 uppercase text-[10px]">Root Cause:</span>
                    <p className="text-slate-800 dark:text-slate-200">{item.cause}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400 uppercase text-[10px]">Mitigation:</span>
                    <p className="text-slate-800 dark:text-slate-200">{item.mitigation}</p>
                  </div>
                </div>
                <div className={`mt-3 pt-2.5 border-t ${isDark ? 'border-slate-800/80' : 'border-slate-100'} flex items-center justify-between text-[11px] text-slate-400`}>
                  <span>Source: {item.source_document} (p. {item.source_page})</span>
                  <span className="font-mono">ID: {item.event_id}</span>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs font-sans text-slate-500 dark:text-slate-400 px-1">
              <span>Recent Inquiries & Sessions</span>
            </div>

            {searchHistory.length === 0 ? (
              <div className={`p-8 rounded-lg border text-center text-slate-500 dark:text-slate-400 text-xs font-sans ${
                isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200'
              }`}>
                No previous search sessions recorded in this session.
              </div>
            ) : (
              <div className="space-y-2">
                {searchHistory.map((h) => (
                  <div
                    key={h.id}
                    onClick={() => {
                      setActiveTab('assistant');
                      setQuery(h.query);
                      handleAsk(h.query);
                    }}
                    className={`p-3.5 rounded-lg border cursor-pointer transition space-y-1.5 ${
                      isDark
                        ? 'bg-[#0B111E] border-slate-800 hover:border-sky-500/50 hover:bg-slate-900/50'
                        : 'bg-white border-slate-200 hover:border-sky-400 hover:bg-slate-50 shadow-xs'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-sans font-semibold text-slate-900 dark:text-white">
                        {h.query}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {new Date(h.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 font-sans line-clamp-2">
                      {h.answer_preview}
                    </p>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400 font-sans pt-0.5">
                      {h.formation && <span>Horizon: <b>{h.formation}</b></span>}
                      {h.depth && <span>Depth: <b className="font-mono">{h.depth.toFixed(0)} m</b></span>}
                      <span>{h.sources_count} cited source(s)</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 3. Bottom Sticky Enterprise Input Dock */}
      {activeTab !== 'history' && (
        <div className={`pt-2 border-t shrink-0 ${isDark ? 'border-slate-800/80 bg-[#080C14]' : 'border-slate-200 bg-slate-50'}`}>
          {/* Dynamic Suggestion Chips Docked Directly Above Input */}
          {dynamicSuggestions.length > 0 && (
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1.5 mb-1 text-xs no-scrollbar">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider shrink-0 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-500" />
                Suggestions:
              </span>
              {dynamicSuggestions.map((p, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setQuery(p);
                    handleAsk(p);
                  }}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-sans transition whitespace-nowrap border shrink-0 ${
                    isDark
                      ? 'bg-slate-900/80 border-slate-800 hover:border-slate-700 text-slate-300 hover:text-sky-300'
                      : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700 hover:text-sky-700 shadow-2xs'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {/* Form Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAsk();
            }}
            className={`p-2 rounded-lg border transition-colors flex items-center gap-2 ${
              isDark ? 'bg-[#0B111E] border-slate-800' : 'bg-white border-slate-200 shadow-xs'
            }`}
          >
            <div className="relative flex-1 flex items-center">
              <Search className="w-4 h-4 text-slate-400 ml-2 mr-2 shrink-0" />
              <input
                ref={inputRef}
                type="text"
                placeholder={
                  activeTab === 'assistant'
                    ? 'Ask about offset wells, formations, lost circulation, stuck pipe, or mitigations...'
                    : 'Enter semantic search query (e.g. "LCM pill Barail 3400m")...'
                }
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
                className={`w-full bg-transparent py-1 text-xs font-sans focus:outline-none ${
                  isDark ? 'text-white placeholder-slate-500' : 'text-slate-900 placeholder-slate-400'
                }`}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-4 py-2 rounded-md bg-sky-600 hover:bg-sky-500 text-white font-sans font-semibold text-xs transition flex items-center gap-1.5 disabled:opacity-50 shadow-xs shrink-0"
            >
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              <span>{loading ? 'Searching...' : 'Send'}</span>
            </button>
          </form>

          <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 px-1">
            <span>Institutional memory decision support &bull; OIL India Limited</span>
            <span>Assam-Arakan Basin Model</span>
          </div>
        </div>
      )}
    </div>
  );
};

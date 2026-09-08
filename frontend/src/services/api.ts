import {
  Well, NearbyWell, Formation, DrillingEvent, RiskPredictionResponse,
  Alert, Recommendation, ModelMetrics, SearchResult, AssistantAnswer, SystemStatus,
  ShapExplanationResponse, UnifiedSearchResponse, SearchHistoryItem
} from '../types';

const API_BASE = '/api';

const getAuthHeaders = (extraHeaders: Record<string, string> = {}): HeadersInit => {
  const token = localStorage.getItem('nwis_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...extraHeaders,
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login-json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error('Invalid credentials');
    return res.json();
  },

  // Wells
  getWells: async (): Promise<Well[]> => {
    const res = await fetch(`${API_BASE}/wells`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch wells');
    return res.json();
  },

  getActiveWell: async (): Promise<Well> => {
    const res = await fetch(`${API_BASE}/wells/active`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch active well');
    return res.json();
  },

  getWellById: async (wellId: string): Promise<Well> => {
    const res = await fetch(`${API_BASE}/wells/${wellId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error(`Failed to fetch well ${wellId}`);
    return res.json();
  },

  getNearbyWells: async (wellId: string, radiusKm = 25): Promise<NearbyWell[]> => {
    const res = await fetch(`${API_BASE}/wells/${wellId}/nearby?radius_km=${radiusKm}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch nearby wells');
    return res.json();
  },

  getWellEvents: async (wellId: string): Promise<DrillingEvent[]> => {
    const res = await fetch(`${API_BASE}/wells/${wellId}/events`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch well events');
    return res.json();
  },

  getWellTrajectory: async (wellId: string) => {
    const res = await fetch(`${API_BASE}/wells/${wellId}/trajectory`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch trajectory');
    return res.json();
  },

  compareWells: async (wellIds: string[]) => {
    const params = new URLSearchParams();
    wellIds.forEach(id => params.append('well_ids', id));
    const res = await fetch(`${API_BASE}/wells/compare?${params.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to compare wells');
    return res.json();
  },

  getTelemetryHistory: async (wellId: string, limit = 80) => {
    const res = await fetch(`${API_BASE}/wells/${wellId}/telemetry-history?limit=${limit}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch telemetry history');
    return res.json();
  },

  // Formations
  getFormations: async (): Promise<Formation[]> => {
    const res = await fetch(`${API_BASE}/formations`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch formations');
    return res.json();
  },

  // Knowledge Repo Events
  getEvents: async (filters: { formation?: string; event_type?: string; severity?: string; min_depth?: number; max_depth?: number } = {}): Promise<DrillingEvent[]> => {
    const params = new URLSearchParams();
    if (filters.formation) params.append('formation', filters.formation);
    if (filters.event_type) params.append('event_type', filters.event_type);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.min_depth !== undefined) params.append('min_depth', filters.min_depth.toString());
    if (filters.max_depth !== undefined) params.append('max_depth', filters.max_depth.toString());

    const res = await fetch(`${API_BASE}/events?${params.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch events');
    return res.json();
  },

  // ML Risk
  predictRisk: async (telemetry: any): Promise<RiskPredictionResponse> => {
    const res = await fetch(`${API_BASE}/risk/predict`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(telemetry)
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Drilling Engineer or Admin required to run risk prediction.');
      throw new Error('Failed to predict risk');
    }
    return res.json();
  },

  explainRisk: async (telemetry: any): Promise<ShapExplanationResponse> => {
    const res = await fetch(`${API_BASE}/risk/explain`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(telemetry)
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Drilling Engineer or Admin required to explain risk.');
      throw new Error('Failed to compute SHAP risk explanation');
    }
    return res.json();
  },

  getModelMetrics: async (): Promise<Record<string, ModelMetrics>> => {
    const res = await fetch(`${API_BASE}/risk/metrics`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch model metrics');
    return res.json();
  },

  // Alerts
  getAlerts: async (wellId?: string, status?: string): Promise<Alert[]> => {
    const params = new URLSearchParams();
    if (wellId) params.append('well_id', wellId);
    if (status) params.append('status', status);
    const res = await fetch(`${API_BASE}/alerts?${params.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  acknowledgeAlert: async (alertId: string, acknowledgedBy: string): Promise<Alert> => {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ acknowledged_by: acknowledgedBy })
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Supervisor, Drilling Engineer, or Admin required to acknowledge alerts.');
      throw new Error('Failed to acknowledge alert');
    }
    return res.json();
  },

  // Recommendations
  getRecommendations: async (wellId: string): Promise<Recommendation[]> => {
    const res = await fetch(`${API_BASE}/recommendations/${wellId}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },

  generateRecommendations: async (payload: { well_id: string; target_depth?: number; current_formation?: string }): Promise<Recommendation[]> => {
    const res = await fetch(`${API_BASE}/recommendations/generate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Failed to generate dynamic recommendations');
    return res.json();
  },

  // Search
  searchKeyword: async (query: string, formation?: string, eventType?: string): Promise<SearchResult[]> => {
    const res = await fetch(`${API_BASE}/search/keyword`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ query, formation, event_type: eventType })
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Geologist role or higher required for search.');
      throw new Error('Keyword search failed');
    }
    return res.json();
  },

  searchSemantic: async (query: string, targetDepth?: number, formation?: string): Promise<SearchResult[]> => {
    const res = await fetch(`${API_BASE}/search/semantic`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ query, target_depth: targetDepth, formation })
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Geologist role or higher required for search.');
      throw new Error('Semantic search failed');
    }
    return res.json();
  },

  askAssistant: async (question: string, depth?: number, formation?: string): Promise<AssistantAnswer> => {
    const res = await fetch(`${API_BASE}/search/assistant`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ question, current_depth: depth, current_formation: formation })
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Geologist role or higher required for assistant.');
      throw new Error('Assistant query failed');
    }
    return res.json();
  },

  unifiedSearch: async (payload: {
    query: string;
    well_id?: string;
    depth?: number;
    formation?: string;
    conversation_id?: string;
  }): Promise<UnifiedSearchResponse> => {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Geologist role or higher required for search.');
      throw new Error('Search request failed');
    }
    return res.json();
  },

  getSearchSuggestions: async (wellId?: string, depth?: number, formation?: string): Promise<string[]> => {
    const params = new URLSearchParams();
    if (wellId) params.append('well_id', wellId);
    if (depth !== undefined) params.append('depth', depth.toString());
    if (formation) params.append('formation', formation);
    const res = await fetch(`${API_BASE}/search/suggestions?${params.toString()}`, { headers: getAuthHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  getSearchHistory: async (): Promise<SearchHistoryItem[]> => {
    const res = await fetch(`${API_BASE}/search/history`, { headers: getAuthHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  // Documents
  getDocuments: async () => {
    const res = await fetch(`${API_BASE}/documents`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  uploadDocument: async (file: File, wellId = 'WELL-001') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('well_id', wellId);

    const token = localStorage.getItem('nwis_token');
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      headers,
      body: formData
    });
    if (!res.ok) {
      if (res.status === 403) throw new Error('Insufficient permissions: Drilling Engineer or Admin required to upload documents.');
      throw new Error('Document upload failed');
    }
    return res.json();
  },

  // System (Open health check)
  getSystemStatus: async (): Promise<SystemStatus> => {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  // Advanced Analytics & Innovation (Tier 2 & Tier 3)
  getKnowledgeGraph: async () => {
    const res = await fetch(`${API_BASE}/analytics/knowledge-graph`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch knowledge graph');
    return res.json();
  },

  getRiskHeatmap: async () => {
    const res = await fetch(`${API_BASE}/analytics/risk-heatmap`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch risk heatmap');
    return res.json();
  },

  simulateWhatIf: async (payload: any) => {
    const res = await fetch(`${API_BASE}/analytics/what-if`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('What-if simulation failed');
    return res.json();
  },

  getNptCostIntelligence: async () => {
    const res = await fetch(`${API_BASE}/analytics/npt-cost`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch NPT cost intelligence');
    return res.json();
  },

  getDepthExplorer: async (depth: number) => {
    const res = await fetch(`${API_BASE}/analytics/depth-explorer?depth=${depth}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch depth explorer data');
    return res.json();
  },

  getDailyReport: async (wellId?: string) => {
    const url = wellId ? `${API_BASE}/analytics/daily-report?well_id=${wellId}` : `${API_BASE}/analytics/daily-report`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch daily report');
    return res.json();
  },

  getPredictiveTimeline: async (depth: number) => {
    const res = await fetch(`${API_BASE}/analytics/predictive-timeline?depth=${depth}`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch predictive timeline');
    return res.json();
  }
};

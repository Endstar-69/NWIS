export type UserRole = 'Admin' | 'Drilling Engineer' | 'Geologist' | 'Supervisor' | 'Viewer';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface Well {
  well_id: string;
  well_name: string;
  field: string;
  block: string;
  basin: string;
  operator: string;
  well_type: string;
  status: string;
  target_depth: number;
  current_depth: number;
  latitude: number;
  longitude: number;
  spud_date: string;
  completion_date?: string;
  is_active_well: boolean;
  is_demo_data: boolean;
  data_source: string;
  events_count?: number;
}

export interface SimilarityBreakdown {
  distance_score: number;
  formation_score: number;
  depth_score: number;
  reservoir_score: number;
  trajectory_score: number;
  events_score: number;
  weights_used: Record<string, number>;
}

export interface NearbyWell {
  well: Well;
  distance_km: number;
  similarity_score: number;
  similarity_breakdown: SimilarityBreakdown;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  historical_events_count: number;
  common_formations: string[];
}

export interface Formation {
  formation_id: string;
  formation_name: string;
  lithology: string;
  age_era: string;
  typical_top_depth: number;
  typical_bottom_depth: number;
  pore_pressure_gradient_sg: number;
  fracture_gradient_sg: number;
  known_hazards: string;
  drillability_rating: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  color_hex: string;
}

export interface DrillingEvent {
  event_id: string;
  well_id: string;
  well_name?: string;
  event_type: string;
  start_depth: number;
  end_depth: number;
  formation: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  cause: string;
  impact: string;
  mitigation: string;
  lesson_learned: string;
  npt_hours: number;
  source_document: string;
  source_page: number;
  confidence: number;
  is_demo_data: boolean;
  created_at?: string;
}

export interface TelemetryPoint {
  well_id: string;
  depth: number;
  timestamp: string;
  formation_name: string;
  rop: number;
  wob: number;
  rpm: number;
  torque: number;
  standpipe_pressure: number;
  flow_rate: number;
  mud_weight: number;
  ecd: number;
  hook_load: number;
  inclination: number;
  azimuth: number;
  is_simulated?: boolean;
}

export interface RiskFactor {
  factor_name: string;
  impact_level: 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
  contribution_score: number;
}

export interface FeatureShapAttribution {
  feature_name: string;
  feature_value: number;
  shap_value: number;
  absolute_importance: number;
  impact_direction: 'INCREASES_RISK' | 'DECREASES_RISK' | 'NEUTRAL';
}

export interface ModelShapExplanation {
  base_value: number;
  prediction_value: number;
  top_features: FeatureShapAttribution[];
  methodology: string;
  provenance: string;
}

export interface SingleRisk {
  risk_type: string;
  probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence_score: number;
  contributing_factors: RiskFactor[];
  engineering_warnings?: RiskFactor[];
  shap_attribution?: ModelShapExplanation;
  historical_matches_count: number;
  offset_incident_rate: number;
}

export interface ShapExplanationResponse {
  well_id: string;
  depth: number;
  formation: string;
  mud_loss: ModelShapExplanation;
  stuck_pipe: ModelShapExplanation;
  kick: ModelShapExplanation;
  engineering_warnings: RiskFactor[];
}

export interface RiskPredictionResponse {
  well_id: string;
  depth: number;
  formation_name: string;
  overall_risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  predictions: Record<string, SingleRisk>;
  nearby_historical_evidence: any[];
  model_version: string;
  is_demo_prediction: boolean;
}

export interface Alert {
  alert_id: string;
  well_id: string;
  timestamp: string;
  depth: number;
  formation: string;
  risk_type: string;
  severity: 'INFO' | 'WATCH' | 'HIGH' | 'CRITICAL';
  probability: number;
  reasons: string[];
  historical_evidence: any[];
  recommended_action: string;
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED';
  acknowledged_by?: string;
  acknowledged_at?: string;
  is_demo_data: boolean;
}

export interface Recommendation {
  recommendation_id: string;
  well_id: string;
  depth: number;
  formation: string;
  title: string;
  summary: string;
  historical_evidence: any[];
  action_steps: string[];
  precautions: string[];
  confidence: number;
  created_at?: string;
}

export interface ModelMetrics {
  model_name: string;
  target_event: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc?: number;
  confusion_matrix: number[][];
  feature_importances: Record<string, number>;
  training_sample_count: number;
  trained_at: string;
}

export interface SearchResult {
  event_id: string;
  well_id: string;
  well_name: string;
  event_type: string;
  depth: number;
  formation: string;
  severity: string;
  cause: string;
  mitigation: string;
  lesson_learned: string;
  source_document: string;
  source_page: number;
  similarity_score: number;
  match_highlights: string[];
}

export interface AssistantAnswer {
  question: string;
  answer: string;
  grounded_evidence: SearchResult[];
  is_fallback_response: boolean;
  model_used: string;
  timestamp: string;
}

export interface UnifiedSearchSource {
  document: string;
  well: string;
  depth: string;
  formation?: string;
  event?: string;
  relevance?: number;
}

export interface UnifiedSearchResponse {
  answer: string;
  confidence?: number | null;
  answer_type: 'historical_evidence' | 'general_knowledge' | 'insufficient_evidence';
  sources: UnifiedSearchSource[];
  context: {
    well?: string;
    depth?: number;
    formation?: string;
  };
  warnings: string[];
  follow_up_questions: string[];
  conversation_id: string;
  timestamp: string;
}

export interface SearchHistoryItem {
  id: string;
  conversation_id: string;
  query: string;
  timestamp: string;
  well_id?: string;
  depth?: number;
  formation?: string;
  answer_preview: string;
  sources_count: number;
}


export interface SystemStatus {
  status: string;
  environment: string;
  active_database: string;
  counts: {
    wells: number;
    historical_events: number;
    ingested_documents: number;
    active_alerts: number;
    users: number;
  };
  ml_models: {
    status: string;
    models_loaded: Record<string, boolean>;
    fallback_mode: boolean;
  };
  realtime_simulator: {
    status: string;
    tick_interval_s: number;
    active_well_id: string;
  };
}

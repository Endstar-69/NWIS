type TelemetryCallback = (data: { telemetry: any; risk_analysis: any }) => void;

class RealtimeWebSocketService {
  private socket: WebSocket | null = null;
  private wellId: string = 'WELL-001';
  private subscribers: TelemetryCallback[] = [];
  private reconnectTimer: any = null;
  private simTimer: any = null;
  private simStep: number = 0;

  connect(wellId = 'WELL-001') {
    this.wellId = wellId;
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    const rawUrl = import.meta.env.VITE_API_URL || '';
    let wsUrl = '';
    if (rawUrl) {
      const clean = rawUrl.replace(/^http/, 'ws').replace(/\/+$/, '');
      wsUrl = `${clean}/ws/well/${wellId}`;
    } else if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
      wsUrl = `ws://localhost:8000/ws/well/${wellId}`;
    }
    // On Netlify (static host) without a backend URL, go straight to simulation
    if (!wsUrl) {
      console.info('[NWIS WS] No backend URL configured. Starting simulated telemetry feed.');
      this.startSimulatedFeed();
      return;
    }

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log(`[NWIS WS] Connected to live well stream (${wellId})`);
        this.stopSimulatedFeed();
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'TELEMETRY_UPDATE') {
            this.subscribers.forEach((cb) => cb(payload));
          }
        } catch (err) {
          console.error('[NWIS WS] Message parse error:', err);
        }
      };

      this.socket.onclose = () => {
        console.warn('[NWIS WS] Disconnected. Running simulated telemetry fallback...');
        this.socket = null;
        this.startSimulatedFeed();
      };

      this.socket.onerror = () => {
        this.socket = null;
        this.startSimulatedFeed();
      };
    } catch (e) {
      this.startSimulatedFeed();
    }
  }

  private startSimulatedFeed() {
    if (this.simTimer) return;
    this.simTimer = setInterval(() => {
      this.simStep++;
      const t = this.simStep * 0.2;
      const depth = +(3420.0 + (this.simStep * 0.15)).toFixed(1);
      const rop = +(14.2 + Math.sin(t) * 3.4).toFixed(1);
      const wob = +(16.5 + Math.cos(t * 0.7) * 2.1).toFixed(1);
      const rpm = Math.round(105 + Math.sin(t * 0.4) * 8);
      const torque = +(18.5 + Math.sin(t * 1.1) * 2.8).toFixed(1);
      const spp = Math.round(2180 + Math.cos(t) * 95);
      const flowRate = Math.round(1750 + Math.sin(t * 0.3) * 45);
      const mudWeight = 1.28;
      const ecd = +(1.33 + Math.sin(t * 0.5) * 0.02).toFixed(2);
      const hookLoad = +(122.0 + Math.sin(t * 0.2) * 4.2).toFixed(1);

      const payload = {
        type: 'TELEMETRY_UPDATE',
        telemetry: {
          well_id: this.wellId,
          depth,
          timestamp: new Date().toISOString(),
          formation_name: 'Barail Sandstone',
          rop,
          wob,
          rpm,
          torque,
          standpipe_pressure: spp,
          flow_rate: flowRate,
          mud_weight: mudWeight,
          ecd,
          hook_load: hookLoad,
          inclination: 18.2,
          azimuth: 55.4,
          is_simulated: true
        },
        risk_analysis: {
          well_id: this.wellId,
          depth,
          formation_name: 'Barail Sandstone',
          overall_risk_level: 'HIGH',
          predictions: {
            mud_loss: {
              risk_type: 'Mud Loss',
              probability: 0.78,
              risk_level: 'HIGH',
              confidence_score: 0.91,
              contributing_factors: [
                { factor_name: 'ECD vs Fracture Gradient', impact_level: 'HIGH', description: 'ECD (1.34 SG) approaching formation fracture threshold (1.38 SG).', contribution_score: 0.42 },
                { factor_name: 'Lithology Permeability', impact_level: 'MEDIUM', description: 'Coarse-grained Barail sandstone with micro-fractures.', contribution_score: 0.28 }
              ],
              historical_matches_count: 3,
              offset_incident_rate: 0.67
            },
            stuck_pipe: {
              risk_type: 'Stuck Pipe',
              probability: 0.43,
              risk_level: 'MEDIUM',
              confidence_score: 0.88,
              contributing_factors: [
                { factor_name: 'Torque Fluctuations', impact_level: 'MEDIUM', description: 'Overpull tendency observed during recent connection.', contribution_score: 0.31 }
              ],
              historical_matches_count: 2,
              offset_incident_rate: 0.40
            },
            kick: {
              risk_type: 'Gas Kick',
              probability: 0.12,
              risk_level: 'LOW',
              confidence_score: 0.94,
              contributing_factors: [
                { factor_name: 'Pore Pressure Differential', impact_level: 'LOW', description: 'Mud weight provides +0.08 SG overbalance cushion.', contribution_score: 0.11 }
              ],
              historical_matches_count: 1,
              offset_incident_rate: 0.15
            }
          },
          nearby_historical_evidence: [
            { well_id: 'WELL-002', well_name: 'NHRK-098', event_type: 'Mud Loss', depth: 3218.0, formation: 'Barail Sandstone', distance_km: 2.8 }
          ],
          model_version: 'RandomForest-XAI-v1.4',
          is_demo_prediction: true
        }
      };

      this.subscribers.forEach((cb) => cb(payload));
    }, 1500);
  }

  private stopSimulatedFeed() {
    if (this.simTimer) {
      clearInterval(this.simTimer);
      this.simTimer = null;
    }
  }

  subscribe(callback: TelemetryCallback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter((cb) => cb !== callback);
    };
  }

  disconnect() {
    this.stopSimulatedFeed();
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const realtimeWS = new RealtimeWebSocketService();

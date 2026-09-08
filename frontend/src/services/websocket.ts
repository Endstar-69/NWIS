type TelemetryCallback = (data: { telemetry: any; risk_analysis: any }) => void;

class RealtimeWebSocketService {
  private socket: WebSocket | null = null;
  private wellId: string = 'WELL-001';
  private subscribers: TelemetryCallback[] = [];
  private reconnectTimer: any = null;

  connect(wellId = 'WELL-001') {
    this.wellId = wellId;
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // In vite dev mode, proxy /ws to localhost:8000
    const wsUrl = `${protocol}//${host}/ws/well/${wellId}`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log(`[NWIS WS] Connected to live well stream (${wellId})`);
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
        console.warn('[NWIS WS] Disconnected. Reconnecting in 3s...');
        this.socket = null;
        this.reconnectTimer = setTimeout(() => this.connect(this.wellId), 3000);
      };

      this.socket.onerror = (err) => {
        console.error('[NWIS WS] Error:', err);
      };
    } catch (e) {
      console.error('[NWIS WS] Connection attempt error:', e);
    }
  }

  subscribe(callback: TelemetryCallback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter((cb) => cb !== callback);
    };
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const realtimeWS = new RealtimeWebSocketService();

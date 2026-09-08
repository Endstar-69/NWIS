import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Well, RiskPredictionResponse } from '../types';
import { api } from '../services/api';
import { realtimeWS } from '../services/websocket';

interface WellContextType {
  activeWell: Well | null;
  availableWells: Well[];
  activeDepth: number;
  activeFormation: string;
  liveTelemetry: any | null;
  liveRisk: RiskPredictionResponse | null;
  isLoading: boolean;
  setActiveWellId: (wellId: string) => Promise<void>;
  setManualDepth: (depth: number) => void;
  refreshWellData: () => Promise<void>;
}

const WellContext = createContext<WellContextType | undefined>(undefined);

export const WellProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [availableWells, setAvailableWells] = useState<Well[]>([]);
  const [activeWell, setActiveWell] = useState<Well | null>(null);
  const [activeDepth, setActiveDepth] = useState<number>(3420.0);
  const [activeFormation, setActiveFormation] = useState<string>('Barail Sandstone');
  const [liveTelemetry, setLiveTelemetry] = useState<any | null>(null);
  const [liveRisk, setLiveRisk] = useState<RiskPredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initial fetch of all wells and default active well
  const refreshWellData = useCallback(async () => {
    setIsLoading(true);
    try {
      const wells = await api.getWells();
      setAvailableWells(wells);

      const savedWellId = localStorage.getItem('nwis_active_well_id');
      let targetWell = wells.find(w => w.well_id === savedWellId);
      if (!targetWell) {
        targetWell = await api.getActiveWell();
      }

      if (targetWell) {
        setActiveWell(targetWell);
        setActiveDepth(targetWell.current_depth || 3420.0);
        localStorage.setItem('nwis_active_well_id', targetWell.well_id);
      }
    } catch (err) {
      console.error('Failed to load active well context:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshWellData();
  }, [refreshWellData]);

  // Set active well by ID and reconnect live telemetry stream
  const setActiveWellId = async (wellId: string) => {
    const target = availableWells.find(w => w.well_id === wellId);
    if (target) {
      setActiveWell(target);
      setActiveDepth(target.current_depth || 3420.0);
      localStorage.setItem('nwis_active_well_id', target.well_id);
    } else {
      try {
        const fetched = await api.getWellById(wellId);
        setActiveWell(fetched);
        setActiveDepth(fetched.current_depth || 3420.0);
        localStorage.setItem('nwis_active_well_id', fetched.well_id);
      } catch (e) {
        console.error('Could not switch to well:', wellId, e);
      }
    }
  };

  const setManualDepth = (depth: number) => {
    setActiveDepth(depth);
  };

  // Real-time WebSocket connection to active well telemetry stream
  useEffect(() => {
    if (!activeWell) return;

    realtimeWS.connect(activeWell.well_id);
    const unsubscribe = realtimeWS.subscribe((payload) => {
      if (payload.telemetry) {
        setLiveTelemetry(payload.telemetry);
        if (payload.telemetry.depth) {
          setActiveDepth(payload.telemetry.depth);
        }
        if (payload.telemetry.formation_name) {
          setActiveFormation(payload.telemetry.formation_name);
        }
      }
      if (payload.risk_analysis) {
        setLiveRisk(payload.risk_analysis);
      }
    });

    return () => {
      unsubscribe();
      realtimeWS.disconnect();
    };
  }, [activeWell?.well_id]);

  return (
    <WellContext.Provider
      value={{
        activeWell,
        availableWells,
        activeDepth,
        activeFormation,
        liveTelemetry,
        liveRisk,
        isLoading,
        setActiveWellId,
        setManualDepth,
        refreshWellData
      }}
    >
      {children}
    </WellContext.Provider>
  );
};

export const useWell = () => {
  const context = useContext(WellContext);
  if (!context) throw new Error('useWell must be used within a WellProvider');
  return context;
};

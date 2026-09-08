import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Well, NearbyWell } from '../../types';
import { useTheme } from '../../store/themeContext';
import { Layers, Compass } from 'lucide-react';

interface WellMapProps {
  activeWell: Well | null;
  nearbyWells: NearbyWell[];
  radiusKm: number;
  onSelectWell?: (well: Well) => void;
  onCompareWell?: (wellId: string) => void;
}

type MapLayerType = 'dark' | 'satellite' | 'topo' | 'street';

export const WellMap: React.FC<WellMapProps> = ({
  activeWell,
  nearbyWells,
  radiusKm,
  onSelectWell,
  onCompareWell
}) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const circleRef = useRef<L.Circle | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);

  const [activeLayer, setActiveLayer] = useState<MapLayerType>(isDark ? 'dark' : 'street');
  const [showLayerMenu, setShowLayerMenu] = useState<boolean>(false);

  // Sync map layer with theme
  useEffect(() => {
    if (!isDark && activeLayer === 'dark') {
      setActiveLayer('street');
    } else if (isDark && activeLayer === 'street') {
      setActiveLayer('dark');
    }
  }, [isDark]);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const centerLat = activeWell ? activeWell.latitude : 27.4200;
      const centerLon = activeWell ? activeWell.longitude : 95.3200;

      const map = L.map(mapContainerRef.current, {
        center: [centerLat, centerLon],
        zoom: 11,
        zoomControl: false
      });

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      // Default Tile Layer
      const isInitialDark = theme === 'dark';
      const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        className: isInitialDark ? 'dark-map-tiles' : '',
        maxZoom: 19
      }).addTo(map);

      tileLayerRef.current = tileLayer;
      mapInstanceRef.current = map;
      markersLayerRef.current = L.layerGroup().addTo(map);
    }
  }, []);

  // Update Tile Layer when selected
  useEffect(() => {
    if (!mapInstanceRef.current) return;
    const map = mapInstanceRef.current;

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
    }

    let newTileLayer: L.TileLayer;

    if (activeLayer === 'dark') {
      newTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        className: 'dark-map-tiles',
        maxZoom: 19
      });
    } else if (activeLayer === 'satellite') {
      newTileLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '&copy; Esri, Maxar, Earthstar Geographics',
        maxZoom: 18
      });
    } else if (activeLayer === 'topo') {
      newTileLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
        attribution: '&copy; Esri, HERE, Garmin, USGS',
        maxZoom: 18
      });
    } else {
      // Standard Street
      newTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
      });
    }

    newTileLayer.addTo(map);
    tileLayerRef.current = newTileLayer;
  }, [activeLayer]);

  // Update Markers & Radius Circle
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;

    if (map && markersLayer) {
      markersLayer.clearLayers();

      if (activeWell) {
        // Draw Radius Circle
        if (circleRef.current) {
          map.removeLayer(circleRef.current);
        }

        circleRef.current = L.circle([activeWell.latitude, activeWell.longitude], {
          radius: radiusKm * 1000,
          color: '#0284C7',
          fillColor: '#0284C7',
          fillOpacity: isDark ? 0.08 : 0.05,
          weight: 1.5,
          dashArray: '4, 8'
        }).addTo(map);

        // Active Well Icon
        const activeIcon = L.divIcon({
          className: 'active-well-marker',
          html: `
            <div class="relative flex items-center justify-center">
              <span class="animate-ping absolute inline-flex h-7 w-7 rounded-full bg-sky-400 opacity-75"></span>
              <div class="w-5 h-5 rounded-full bg-sky-500 border-2 border-white shadow-xl flex items-center justify-center text-[9px] font-mono font-bold text-white">
                ★
              </div>
            </div>
          `,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });

        const activeMarker = L.marker([activeWell.latitude, activeWell.longitude], { icon: activeIcon });
        activeMarker.bindPopup(`
          <div class="p-1 font-mono text-xs">
            <div class="flex items-center gap-1.5 text-sky-500 font-bold">
              <span class="w-2 h-2 rounded-full bg-sky-500"></span>
              ACTIVE RIG: ${activeWell.well_name}
            </div>
            <div class="text-slate-500 mt-1">Field: <span class="font-bold text-slate-800 dark:text-white">${activeWell.field}</span></div>
            <div class="text-slate-500">Current Depth: <span class="text-emerald-500 font-bold">${activeWell.current_depth.toFixed(1)} m</span></div>
            <div class="text-slate-500">Horizon: <span class="text-amber-500 font-medium">Barail Sandstone</span></div>
            <div class="mt-2 text-[10px] text-sky-600 font-semibold uppercase tracking-wider bg-sky-50 dark:bg-sky-950/60 p-1 rounded border border-sky-200 dark:border-sky-800">
              Live Telemetry Streaming
            </div>
          </div>
        `);
        markersLayer.addLayer(activeMarker);
      }

      // Nearby Wells Markers
      nearbyWells.forEach((item) => {
        const w = item.well;
        const riskColors: Record<string, string> = {
          CRITICAL: '#EF4444',
          HIGH: '#F97316',
          MEDIUM: '#F59E0B',
          LOW: '#10B981'
        };
        const color = riskColors[item.risk_level] || '#0284C7';

        const markerHtml = `
          <div style="
            background-color: ${color};
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 10px ${color}80;
            cursor: pointer;
          "></div>
        `;

        const icon = L.divIcon({
          className: 'nearby-well-marker',
          html: markerHtml,
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });

        const marker = L.marker([w.latitude, w.longitude], { icon });

        // Popup Content with Actions
        const popupContent = document.createElement('div');
        popupContent.className = 'font-mono text-xs space-y-2 p-1 min-w-[200px]';
        popupContent.innerHTML = `
          <div class="flex items-center justify-between border-b pb-1.5 border-slate-200 dark:border-slate-700">
            <span class="font-bold text-slate-900 dark:text-white">${w.well_name}</span>
            <span style="color: ${color}" class="font-bold text-[10px] uppercase">${item.risk_level}</span>
          </div>
          <div class="space-y-0.5 text-slate-600 dark:text-slate-300 text-[11px]">
            <div>Field: <b class="text-slate-900 dark:text-white">${w.field}</b></div>
            <div>Distance: <b class="text-sky-500">${item.distance_km} km</b></div>
            <div>Target Depth: <b class="text-slate-900 dark:text-white">${w.target_depth} m</b></div>
            <div>Similarity: <b class="text-emerald-500">${item.similarity_score}%</b></div>
            <div>Past Incidents: <b class="text-amber-500">${item.historical_events_count}</b></div>
          </div>
        `;

        const actionRow = document.createElement('div');
        actionRow.className = 'flex items-center gap-1.5 pt-1';

        const inspectBtn = document.createElement('button');
        inspectBtn.innerText = 'Inspect Well';
        inspectBtn.className = 'flex-1 py-1 px-2 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold text-[10px] text-center transition';
        inspectBtn.onclick = () => {
          if (onSelectWell) onSelectWell(w);
        };
        actionRow.appendChild(inspectBtn);

        if (onCompareWell) {
          const compareBtn = document.createElement('button');
          compareBtn.innerText = 'Compare';
          compareBtn.className = 'flex-1 py-1 px-2 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-[10px] text-center transition';
          compareBtn.onclick = () => {
            onCompareWell(w.well_id);
          };
          actionRow.appendChild(compareBtn);
        }

        popupContent.appendChild(actionRow);
        marker.bindPopup(popupContent);

        marker.on('click', () => {
          if (onSelectWell) onSelectWell(w);
        });

        markersLayer.addLayer(marker);
      });
    }
  }, [activeWell, nearbyWells, radiusKm, onSelectWell, onCompareWell, isDark]);

  const recenterMap = () => {
    if (mapInstanceRef.current && activeWell) {
      mapInstanceRef.current.flyTo([activeWell.latitude, activeWell.longitude], 11, { duration: 1.2 });
    }
  };

  return (
    <div className={`relative w-full h-full min-h-[640px] rounded-2xl overflow-hidden ${isDark ? 'border-slate-800' : 'border-slate-200'} border shadow-xl transition-colors`}>
      <div ref={mapContainerRef} className="w-full h-full min-h-[640px]" />

      {/* Top Map Control Actions */}
      <div className="absolute top-4 right-4 z-[1000] flex items-center gap-2 pointer-events-auto">
        {/* Recenter Button */}
        <button
          onClick={recenterMap}
          title="Recenter to Active Rig"
          className={`p-2 ${
            isDark
              ? 'bg-[#0B111E]/90 hover:bg-slate-800 text-slate-300 hover:text-white border-slate-700'
              : 'bg-white/95 hover:bg-slate-100 text-slate-700 hover:text-slate-900 border-slate-200'
          } border rounded-lg shadow-xl backdrop-blur-md transition flex items-center gap-1.5 text-xs font-mono font-bold`}
        >
          <Compass className="w-4 h-4 text-sky-500" />
          <span>Recenter</span>
        </button>

        {/* Basemap Switcher */}
        <div className="relative">
          <button
            onClick={() => setShowLayerMenu(!showLayerMenu)}
            title="Switch Map Layers"
            className={`p-2 ${
              isDark
                ? 'bg-[#0B111E]/90 hover:bg-slate-800 text-slate-300 hover:text-white border-slate-700'
                : 'bg-white/95 hover:bg-slate-100 text-slate-700 hover:text-slate-900 border-slate-200'
            } border rounded-lg shadow-xl backdrop-blur-md transition flex items-center gap-1.5 text-xs font-mono font-bold`}
          >
            <Layers className="w-4 h-4 text-emerald-500" />
            <span className="capitalize">{activeLayer}</span>
          </button>

          {showLayerMenu && (
            <div className={`absolute right-0 top-10 w-44 ${
              isDark ? 'bg-[#0B111E]/95 border-slate-700' : 'bg-white/95 border-slate-200'
            } border rounded-xl shadow-2xl backdrop-blur-md p-1.5 font-mono text-xs z-[1010] space-y-1`}>
              <button
                onClick={() => { setActiveLayer('dark'); setShowLayerMenu(false); }}
                className={`w-full text-left px-3 py-1.5 rounded-lg flex items-center justify-between transition ${
                  activeLayer === 'dark'
                    ? 'bg-sky-600 text-white font-bold'
                    : (isDark ? 'text-slate-300 hover:bg-slate-800' : 'text-slate-700 hover:bg-slate-100')
                }`}
              >
                <span>🌌 Dark Mode</span>
              </button>
              <button
                onClick={() => { setActiveLayer('satellite'); setShowLayerMenu(false); }}
                className={`w-full text-left px-3 py-1.5 rounded-lg flex items-center justify-between transition ${
                  activeLayer === 'satellite'
                    ? 'bg-sky-600 text-white font-bold'
                    : (isDark ? 'text-slate-300 hover:bg-slate-800' : 'text-slate-700 hover:bg-slate-100')
                }`}
              >
                <span>🛰️ Satellite Terrain</span>
              </button>
              <button
                onClick={() => { setActiveLayer('topo'); setShowLayerMenu(false); }}
                className={`w-full text-left px-3 py-1.5 rounded-lg flex items-center justify-between transition ${
                  activeLayer === 'topo'
                    ? 'bg-sky-600 text-white font-bold'
                    : (isDark ? 'text-slate-300 hover:bg-slate-800' : 'text-slate-700 hover:bg-slate-100')
                }`}
              >
                <span>🏔️ Topographic</span>
              </button>
              <button
                onClick={() => { setActiveLayer('street'); setShowLayerMenu(false); }}
                className={`w-full text-left px-3 py-1.5 rounded-lg flex items-center justify-between transition ${
                  activeLayer === 'street'
                    ? 'bg-sky-600 text-white font-bold'
                    : (isDark ? 'text-slate-300 hover:bg-slate-800' : 'text-slate-700 hover:bg-slate-100')
                }`}
              >
                <span>🗺️ Standard Street</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Map Overlay Legend */}
      <div className={`absolute bottom-4 left-4 z-[1000] ${
        isDark ? 'bg-[#0B111E]/90 border-slate-800' : 'bg-white/95 border-slate-200'
      } border backdrop-blur-md px-3.5 py-2.5 rounded-lg text-xs font-mono shadow-2xl space-y-1.5 pointer-events-auto`}>
        <div className={`text-[10px] ${isDark ? 'text-slate-400' : 'text-slate-500'} uppercase font-bold tracking-wider`}>Offset Risk Profile</div>
        <div className="flex items-center gap-4 text-[11px]">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 border border-white"></span>
            <span className={isDark ? 'text-slate-200' : 'text-slate-700'}>Active</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span className={isDark ? 'text-slate-200' : 'text-slate-700'}>Critical</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            <span className={isDark ? 'text-slate-200' : 'text-slate-700'}>High</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
            <span className={isDark ? 'text-slate-200' : 'text-slate-700'}>Medium</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span className={isDark ? 'text-slate-200' : 'text-slate-700'}>Low</span>
          </div>
        </div>
      </div>
    </div>
  );
};

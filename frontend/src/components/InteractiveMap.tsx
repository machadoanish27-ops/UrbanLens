import { useEffect, useRef, useState, useMemo, type FC } from 'react';
import L from 'leaflet';
import { MapPin, Navigation, Filter } from 'lucide-react';

export interface MapMarkerItem {
  lat: number;
  lon: number;
  title: string;
  category?: string;
  address?: string;
  distance_meters?: number;
  provider?: string;
  website?: string;
  phone?: string;
}

// Runtime value export to prevent module resolution errors if imported without 'type'
export const MapMarkerItem = {};

interface InteractiveMapProps {
  latitude: number;
  longitude: number;
  cityName: string;
  markers?: MapMarkerItem[];
  zoom?: number;
  height?: string;
  className?: string;
  showFilters?: boolean;
}

const MAP_FILTER_OPTIONS = [
  { key: 'all', label: 'All Categories', emoji: '🌐' },
  { key: 'education', label: 'Education', emoji: '🎓' },
  { key: 'healthcare', label: 'Healthcare', emoji: '🏥' },
  { key: 'hospital', label: 'Hospitals', emoji: '🏨' },
  { key: 'clinic', label: 'Clinics', emoji: '🩺' },
  { key: 'dental', label: 'Dental', emoji: '🦷' },
  { key: 'pharmacy', label: 'Pharmacies', emoji: '💊' },
  { key: 'transit', label: 'Transit', emoji: '🚆' },
];

export const InteractiveMap: FC<InteractiveMapProps> = ({
  latitude,
  longitude,
  cityName,
  markers = [],
  zoom = 12,
  height = 'h-96',
  className = '',
  showFilters = true,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Filter markers based on selected category
  const filteredMarkers = useMemo(() => {
    if (selectedCategory === 'all') return markers;
    return markers.filter((m) => {
      const c = (m.category || '').toLowerCase();
      const t = (m.title || '').toLowerCase();
      if (selectedCategory === 'education') {
        return c.includes('education') || c.includes('university') || c.includes('college') || c.includes('school') || c.includes('institute');
      }
      if (selectedCategory === 'healthcare') {
        return c.includes('health') || c.includes('hospital') || c.includes('clinic') || c.includes('dental') || c.includes('dentist') || c.includes('pharmacy') || c.includes('doctor');
      }
      if (selectedCategory === 'hospital') {
        return c.includes('hospital') || t.includes('hospital');
      }
      if (selectedCategory === 'clinic') {
        return c.includes('clinic') || c.includes('doctor') || t.includes('clinic');
      }
      if (selectedCategory === 'dental') {
        return c.includes('dental') || c.includes('dentist') || t.includes('dental');
      }
      if (selectedCategory === 'pharmacy') {
        return c.includes('pharmacy') || c.includes('chemist') || t.includes('pharmacy');
      }
      if (selectedCategory === 'transit') {
        return c.includes('transit') || c.includes('station') || c.includes('bus') || c.includes('subway') || c.includes('train');
      }
      return c.includes(selectedCategory);
    });
  }, [markers, selectedCategory]);

  // Initialize Leaflet Map once
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    const map = L.map(mapContainerRef.current, {
      center: [latitude, longitude],
      zoom,
      zoomControl: true,
      attributionControl: true,
    });

    mapInstanceRef.current = map;

    // OpenStreetMap tile layer
    const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
      className: 'dark-tiles',
    });
    tileLayer.addTo(map);

    // City Center Anchor Pin
    const cityIcon = L.divIcon({
      className: 'custom-city-pin',
      html: `
        <div style="
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: rgba(99, 102, 241, 0.95);
          border: 3px solid #ffffff;
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 14px;
        ">
          🏙️
        </div>
      `,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -18],
    });

    const centerMarker = L.marker([latitude, longitude], { icon: cityIcon }).addTo(map);
    centerMarker.bindPopup(`
      <div style="font-size: 12px; line-height: 1.4; font-family: system-ui, sans-serif;">
        <strong style="color: #818cf8; font-size: 13px;">${cityName}</strong><br/>
        <span style="color: #94a3b8; font-size: 11px;">City Center Geographic Anchor</span><br/>
        <span style="font-family: monospace; font-size: 11px; color: #cbd5e1;">${latitude.toFixed(4)}°N, ${longitude.toFixed(4)}°E</span>
      </div>
    `);

    // Layer group for dynamic POI markers
    const markersLayer = L.layerGroup().addTo(map);
    markersLayerRef.current = markersLayer;

    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 200);

    return () => {
      clearTimeout(timer);
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [latitude, longitude, cityName, zoom]);

  // Update POI markers whenever filteredMarkers changes
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current) return;

    markersLayerRef.current.clearLayers();

    const getCategoryStyle = (cat?: string) => {
      const c = (cat || '').toLowerCase();
      if (c.includes('hospital')) {
        return { bg: 'rgba(239, 68, 68, 0.9)', glow: 'rgba(239, 68, 68, 0.8)', emoji: '🏨' };
      }
      if (c.includes('dental') || c.includes('dentist')) {
        return { bg: 'rgba(14, 165, 233, 0.9)', glow: 'rgba(14, 165, 233, 0.8)', emoji: '🦷' };
      }
      if (c.includes('pharmacy')) {
        return { bg: 'rgba(245, 158, 11, 0.9)', glow: 'rgba(245, 158, 11, 0.8)', emoji: '💊' };
      }
      if (c.includes('clinic') || c.includes('doctor')) {
        return { bg: 'rgba(16, 185, 129, 0.9)', glow: 'rgba(16, 185, 129, 0.8)', emoji: '🩺' };
      }
      if (c.includes('university') || c.includes('college') || c.includes('school') || c.includes('education')) {
        return { bg: 'rgba(168, 85, 247, 0.9)', glow: 'rgba(168, 85, 247, 0.8)', emoji: '🎓' };
      }
      if (c.includes('transit') || c.includes('station') || c.includes('bus') || c.includes('train')) {
        return { bg: 'rgba(6, 182, 212, 0.9)', glow: 'rgba(6, 182, 212, 0.8)', emoji: '🚆' };
      }
      return { bg: 'rgba(100, 116, 139, 0.9)', glow: 'rgba(100, 116, 139, 0.8)', emoji: '📍' };
    };

    filteredMarkers.forEach((m) => {
      if (m.lat === undefined || m.lon === undefined || isNaN(m.lat) || isNaN(m.lon)) return;

      const style = getCategoryStyle(m.category);
      const poiIcon = L.divIcon({
        className: 'custom-poi-pin',
        html: `
          <div style="
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: ${style.bg};
            border: 2px solid #ffffff;
            box-shadow: 0 0 10px ${style.glow};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
          ">
            ${style.emoji}
          </div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
        popupAnchor: [0, -14],
      });

      const poiMarker = L.marker([m.lat, m.lon], { icon: poiIcon });

      const popupHtml = `
        <div style="font-size: 12px; line-height: 1.4; max-width: 240px; font-family: system-ui, sans-serif;">
          <strong style="color: #f1f5f9; font-size: 13px; display: block; margin-bottom: 2px;">${m.title}</strong>
          ${m.category ? `<span style="display:inline-block; font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 1px 6px; border-radius: 4px; background: rgba(99,102,241,0.25); color: #a5b4fc; margin-bottom: 4px;">${m.category}</span><br/>` : ''}
          ${m.address ? `<div style="color: #94a3b8; font-size: 11px; margin-bottom: 4px;">${m.address}</div>` : ''}
          ${m.distance_meters !== undefined ? `<div style="color: #38bdf8; font-size: 10px; font-weight: 600; margin-bottom: 4px;">${m.distance_meters > 1000 ? `${(m.distance_meters / 1000).toFixed(1)} km from center` : `${Math.round(m.distance_meters)}m from center`}</div>` : ''}
          ${m.provider ? `<div style="color: #64748b; font-size: 10px; margin-bottom: 4px;">Source: ${m.provider}</div>` : ''}
          ${m.website ? `<div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.1);"><a href="${m.website}" target="_blank" rel="noopener noreferrer" style="color: #818cf8; text-decoration: none; font-weight: 600; font-size: 11px;">Official Website &rarr;</a></div>` : ''}
        </div>
      `;

      poiMarker.bindPopup(popupHtml);
      markersLayerRef.current?.addLayer(poiMarker);
    });
  }, [filteredMarkers]);

  return (
    <div className={`relative w-full rounded-2xl overflow-hidden border border-slate-800 shadow-xl ${height} ${className}`}>
      {/* Top Banner overlay */}
      <div className="absolute top-3 left-3 z-[1000] pointer-events-none">
        <div className="px-3 py-1.5 rounded-xl bg-slate-950/85 backdrop-blur-md border border-slate-800/80 text-xs flex items-center gap-2 shadow-lg">
          <Navigation className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-semibold text-white">{cityName}</span>
          <span className="text-slate-400 text-[11px] font-mono">
            {latitude.toFixed(4)}°, {longitude.toFixed(4)}°
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-300 font-bold">
            {filteredMarkers.length} of {markers.length} POIs
          </span>
        </div>
      </div>

      {/* Category Filter Pills */}
      {showFilters && (
        <div className="absolute top-3 right-14 z-[1000] hidden sm:flex items-center gap-1 bg-slate-950/85 backdrop-blur-md p-1 rounded-xl border border-slate-800 shadow-lg max-w-[60%] overflow-x-auto scrollbar-none">
          <div className="flex items-center gap-1 text-[11px] text-slate-400 px-1.5 py-0.5 font-semibold">
            <Filter className="w-3 h-3 text-indigo-400" />
          </div>
          {MAP_FILTER_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              type="button"
              onClick={() => setSelectedCategory(opt.key)}
              className={`px-2 py-0.5 rounded-lg text-[10px] font-semibold whitespace-nowrap transition-all ${
                selectedCategory === opt.key
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
              }`}
            >
              <span>{opt.emoji}</span> <span className="ml-0.5">{opt.label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Recenter Button */}
      <button
        type="button"
        onClick={() => {
          if (mapInstanceRef.current) {
            mapInstanceRef.current.setView([latitude, longitude], zoom, { animate: true });
          }
        }}
        className="absolute bottom-4 right-4 z-[1000] px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 shadow-lg flex items-center gap-1.5 transition-colors"
        title="Recenter to city coordinates"
      >
        <MapPin className="w-3.5 h-3.5 text-indigo-400" />
        <span>Recenter</span>
      </button>

      {/* Leaflet map DOM node */}
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};

import { useEffect, useRef, type FC } from 'react';
import L from 'leaflet';
import { MapPin, Navigation } from 'lucide-react';

export interface MapMarkerItem {
  lat: number;
  lon: number;
  title: string;
  category?: string;
  address?: string;
  distance_meters?: number;
}

interface InteractiveMapProps {
  latitude: number;
  longitude: number;
  cityName: string;
  markers?: MapMarkerItem[];
  zoom?: number;
  height?: string;
  className?: string;
}

export const InteractiveMap: FC<InteractiveMapProps> = ({
  latitude,
  longitude,
  cityName,
  markers = [],
  zoom = 12,
  height = 'h-96',
  className = '',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // If map already exists, remove it before reinitializing
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
    }

    // Initialize Leaflet Map
    const map = L.map(mapContainerRef.current, {
      center: [latitude, longitude],
      zoom,
      zoomControl: true,
      attributionControl: true,
    });

    mapInstanceRef.current = map;

    // Add OpenStreetMap tile layer (100% free, no secret API key)
    const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      className: 'dark-tiles',
    });
    tileLayer.addTo(map);

    // Create custom City Center DivIcon
    const cityIcon = L.divIcon({
      className: 'custom-city-pin',
      html: `
        <div style="
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: rgba(99, 102, 241, 0.9);
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

    // Add City Center Marker
    const centerMarker = L.marker([latitude, longitude], { icon: cityIcon }).addTo(map);
    centerMarker.bindPopup(`
      <div style="font-size: 12px; line-height: 1.4;">
        <strong style="color: #818cf8; font-size: 13px;">${cityName}</strong><br/>
        <span style="color: #94a3b8;">City Center Anchor</span><br/>
        <span style="font-family: monospace; font-size: 11px; color: #cbd5e1;">${latitude.toFixed(4)}°N, ${longitude.toFixed(4)}°E</span>
      </div>
    `);

    // Category Color Mapping
    const getCategoryStyle = (cat?: string) => {
      const c = (cat || '').toLowerCase();
      if (c.includes('hospital') || c.includes('clinic') || c.includes('health') || c.includes('pharmacy')) {
        return { bg: 'rgba(16, 185, 129, 0.9)', glow: 'rgba(16, 185, 129, 0.8)', emoji: '🏥' };
      }
      if (c.includes('university') || c.includes('school') || c.includes('college')) {
        return { bg: 'rgba(168, 85, 247, 0.9)', glow: 'rgba(168, 85, 247, 0.8)', emoji: '🎓' };
      }
      if (c.includes('transit') || c.includes('station') || c.includes('bus')) {
        return { bg: 'rgba(6, 182, 212, 0.9)', glow: 'rgba(6, 182, 212, 0.8)', emoji: '🚆' };
      }
      return { bg: 'rgba(245, 158, 11, 0.9)', glow: 'rgba(245, 158, 11, 0.8)', emoji: '📍' };
    };

    // Add Nearby POI Markers
    const markerGroup: L.Marker[] = [centerMarker];
    markers.forEach((m) => {
      if (m.lat === undefined || m.lon === undefined) return;

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

      const poiMarker = L.marker([m.lat, m.lon], { icon: poiIcon }).addTo(map);
      poiMarker.bindPopup(`
        <div style="font-size: 12px; line-height: 1.4; max-width: 200px;">
          <strong style="color: #f1f5f9; font-size: 12px;">${m.title}</strong><br/>
          ${m.category ? `<span style="display:inline-block; font-size: 10px; padding: 1px 6px; border-radius: 4px; background: rgba(99,102,241,0.2); color: #a5b4fc; margin: 3px 0;">${m.category}</span><br/>` : ''}
          ${m.address ? `<span style="color: #94a3b8; font-size: 11px;">${m.address}</span><br/>` : ''}
          ${m.distance_meters !== undefined ? `<span style="color: #38bdf8; font-size: 10px; font-weight: 600;">${m.distance_meters > 1000 ? `${(m.distance_meters / 1000).toFixed(1)} km away` : `${Math.round(m.distance_meters)}m away`}</span>` : ''}
        </div>
      `);
      markerGroup.push(poiMarker);
    });

    // Invalidate map size after a tick to prevent partial tile loading
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
  }, [latitude, longitude, cityName, markers, zoom]);

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
          {markers.length > 0 && (
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-300 font-bold">
              {markers.length} POIs
            </span>
          )}
        </div>
      </div>

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

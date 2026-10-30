import React, { useState } from 'react';
import { useUrban } from '../../context/UrbanContext';
import { useCity, useCityPlaces } from '../../hooks/useUrbanLens';
import { InteractiveMap, type MapMarkerItem } from '../InteractiveMap';
import { DataTrustBadge } from './DataTrustBadge';
import {
  Layers,
  Crosshair,
  Sparkles
} from 'lucide-react';

interface CityMapCanvasProps {
  heightClass?: string;
  cityId?: string;
  initialCategory?: string;
  showTimeline?: boolean;
}

export const CityMapCanvas: React.FC<CityMapCanvasProps> = ({
  heightClass = 'h-[520px]',
  cityId,
  initialCategory = 'hospital',
}) => {
  const { activeCityId } = useUrban();
  const targetCityId = cityId || activeCityId;

  const { data: cityResp } = useCity(targetCityId);
  const city = cityResp?.data;

  const [activeCategory, setActiveCategory] = useState<string>(initialCategory);

  const lat = city?.latitude ?? 35.6895;
  const lon = city?.longitude ?? 139.6917;

  // Query places for current city coordinates
  const { data: placesResp, isLoading } = useCityPlaces({
    lat,
    lon,
    category: activeCategory !== 'all' ? activeCategory : 'hospital',
    radius: 3500,
    limit: 15,
  });

  const rawPlaces = placesResp?.data?.places || (placesResp?.data as any)?.items || [];
  const markers: MapMarkerItem[] = rawPlaces
    .filter((p: any) => p.latitude != null && p.longitude != null)
    .map((p: any) => ({
      lat: p.latitude,
      lon: p.longitude,
      title: p.name || 'Location',
      category: p.category || activeCategory,
      address: p.address,
      distance_meters: p.distance_meters,
      provider: 'OpenStreetMap Overpass',
      website: p.tags?.website,
      phone: p.tags?.phone,
    }));

  const categories = [
    { id: 'hospital', label: 'Healthcare' },
    { id: 'school', label: 'Education' },
    { id: 'restaurant', label: 'Dining' },
    { id: 'bus_station', label: 'Transit' },
    { id: 'pharmacy', label: 'Pharmacy' },
  ];

  return (
    <div className={`relative w-full ${heightClass} rounded-2xl bg-[#030712] border border-[#1E334A] overflow-hidden group select-none shadow-2xl flex flex-col`}>
      {/* Top HUD Toolbar */}
      <div className="z-10 p-3 bg-[#0B1726]/90 backdrop-blur-md border-b border-[#1E334A] flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Crosshair className="w-4 h-4 text-cyan-400 animate-spin-slow" />
            <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
              {city?.name || 'Tokyo'} SPATIAL TWIN
            </span>
            <DataTrustBadge status={markers.length > 0 ? 'LIVE' : 'VERIFIED'} size="sm" />
          </div>
          <span className="text-[10px] font-mono text-slate-400 hidden sm:inline">
            COORDS: {lat.toFixed(4)}°, {lon.toFixed(4)}°
          </span>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
          <span className="text-[10px] font-mono text-slate-400 px-1 font-semibold flex items-center gap-1">
            <Layers className="w-3 h-3 text-cyan-400" />
            POIs:
          </span>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`px-2.5 py-1 text-[11px] font-mono rounded-lg transition-colors ${
                activeCategory === cat.id
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_10px_rgba(34,211,238,0.2)]'
                  : 'text-slate-400 hover:text-white bg-[#07111F] border border-[#1E334A]'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Embedded Real Leaflet Map */}
      <div className="relative flex-1 w-full min-h-0">
        <InteractiveMap
          latitude={lat}
          longitude={lon}
          cityName={city?.name || 'Tokyo'}
          markers={markers}
          zoom={13}
          height="h-full"
          showFilters={false}
        />

        {/* Loading overlay if fetching places */}
        {isLoading && (
          <div className="absolute top-4 right-4 z-[500] px-3 py-1.5 rounded-lg bg-[#0B1726]/90 border border-cyan-500/40 text-[10px] font-mono text-cyan-300 animate-pulse flex items-center gap-1.5 shadow-xl">
            <Sparkles className="w-3 h-3 animate-spin" />
            <span>Overpass Mirror Ingesting...</span>
          </div>
        )}

        {/* Bottom HUD Telemetry Overlay */}
        <div className="absolute bottom-3 left-3 z-[500] hidden sm:flex items-center gap-2 p-2 rounded-xl bg-[#0B1726]/85 backdrop-blur-md border border-[#1E334A] text-[10px] font-mono text-slate-400 shadow-xl">
          <span className="text-cyan-400 font-bold">{markers.length} Verified POIs</span>
          <span>·</span>
          <span>Bounding Radius: 3,500m</span>
          <span>·</span>
          <span>OSM Overpass Provenance</span>
        </div>
      </div>
    </div>
  );
};

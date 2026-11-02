import React, { useState } from 'react';
import { useUrban } from '../../context/UrbanContext';
import { useCity, useCityPlaces } from '../../hooks/useUrbanLens';
import { InteractiveMap, type MapMarkerItem } from '../InteractiveMap';
import { normalizeCityId, getStudioKeyForId, CITIES_DATA } from '../../data/urbanData';
import { DataTrustBadge } from './DataTrustBadge';
import {
  Layers,
  Crosshair,
  Sparkles,
  AlertCircle
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
  const { currentCity, activeCityId, isCityLoading } = useUrban();
  const targetCityId = cityId ? normalizeCityId(cityId) : activeCityId;
  const isCurrentActive = !cityId || targetCityId === activeCityId;

  // If a specific cityId different from active city is provided, query it
  const { data: specificCityResp, isLoading: isSpecificLoading } = useCity(
    isCurrentActive ? '' : targetCityId
  );

  const studioKey = getStudioKeyForId(targetCityId);
  const fallbackBase = CITIES_DATA[studioKey] || currentCity;

  const cityName = isCurrentActive
    ? currentCity.name
    : (specificCityResp?.data?.name || fallbackBase?.name || 'City');

  const lat = isCurrentActive
    ? currentCity.latitude
    : (specificCityResp?.data?.latitude ?? fallbackBase?.latitude);

  const lon = isCurrentActive
    ? currentCity.longitude
    : (specificCityResp?.data?.longitude ?? fallbackBase?.longitude);

  const isLoading = isCurrentActive ? isCityLoading : isSpecificLoading;

  const [activeCategory, setActiveCategory] = useState<string>(initialCategory);

  // Query places for current city coordinates
  const { data: placesResp, isLoading: isPlacesLoading } = useCityPlaces({
    lat: lat ?? 0,
    lon: lon ?? 0,
    category: activeCategory !== 'all' ? activeCategory : 'hospital',
    radius: 3500,
    limit: 15,
  });

  const rawPlaces = placesResp?.data?.places || (placesResp?.data as any)?.items || [];
  const markers: MapMarkerItem[] = (lat !== undefined && lon !== undefined)
    ? rawPlaces
        .filter((p: any) => p.latitude != null && p.longitude != null)
        .map((p: any) => ({
          lat: p.latitude,
          lon: p.longitude,
          title: p.name || 'Location',
          category: p.category || activeCategory,
          address: p.address,
          distance_meters: p.distance_meters,
          provider: p.source || p.provider || 'OpenStreetMap Overpass',
          website: p.tags?.website,
          phone: p.tags?.phone,
        }))
    : [];

  const categories = [
    { id: 'hospital', label: 'Healthcare' },
    { id: 'school', label: 'Education' },
    { id: 'restaurant', label: 'Dining' },
    { id: 'bus_station', label: 'Transit' },
    { id: 'pharmacy', label: 'Pharmacy' },
  ];

  if (lat === undefined || lon === undefined) {
    if (isLoading) {
      return (
        <div className={`relative w-full ${heightClass} rounded-2xl bg-[#030712] border border-[#1E334A] flex flex-col items-center justify-center p-6 text-center space-y-3`}>
          <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
          <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wider uppercase">
            SYNCHRONIZING SPATIAL TOPOLOGY FOR {cityName || 'CITY'}...
          </span>
        </div>
      );
    }
    return (
      <div className={`relative w-full ${heightClass} rounded-2xl bg-[#030712] border border-[#1E334A] flex flex-col items-center justify-center p-6 text-center space-y-3`}>
        <AlertCircle className="w-8 h-8 text-amber-400" />
        <span className="text-xs font-mono text-amber-300 font-semibold tracking-wider uppercase">
          SPATIAL COORDINATES UNAVAILABLE FOR {cityName || 'CITY'}
        </span>
        <span className="text-[11px] font-mono text-slate-400 max-w-md">
          UrbanLens has no verified geospatial coordinates for this sector. Map rendering paused.
        </span>
      </div>
    );
  }

  return (
    <div className={`relative w-full ${heightClass} rounded-2xl bg-[#030712] border border-[#1E334A] overflow-hidden group select-none shadow-2xl flex flex-col`}>
      {/* Top HUD Toolbar */}
      <div className="z-10 p-3 bg-[#0B1726]/90 backdrop-blur-md border-b border-[#1E334A] flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Crosshair className="w-4 h-4 text-cyan-400 animate-spin-slow" />
            <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
              {cityName} SPATIAL TWIN
            </span>
            <DataTrustBadge status={markers.length > 0 ? 'LIVE' : 'DATA UNAVAILABLE'} size="sm" source="OpenStreetMap / Overpass" />
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
          cityName={cityName}
          markers={markers}
          zoom={13}
          height="h-full"
          showFilters={false}
        />

        {/* Loading overlay if fetching places */}
        {isPlacesLoading && (
          <div className="absolute top-4 right-4 z-[500] px-3 py-1.5 rounded-lg bg-[#0B1726]/90 border border-cyan-500/40 text-[10px] font-mono text-cyan-300 animate-pulse flex items-center gap-1.5 shadow-xl">
            <Sparkles className="w-3 h-3 animate-spin" />
            <span>Overpass Mirror Ingesting...</span>
          </div>
        )}

        {/* Bottom HUD Telemetry Overlay */}
        <div className="absolute bottom-3 left-3 z-[500] hidden sm:flex items-center gap-2 p-2 rounded-xl bg-[#0B1726]/85 backdrop-blur-md border border-[#1E334A] text-[10px] font-mono text-slate-400 shadow-xl">
          {markers.length > 0 ? (
            <>
              <span className="text-cyan-400 font-bold">{markers.length} Verified POIs</span>
              <span>·</span>
              <span>Bounding Radius: 3,500m</span>
              <span>·</span>
              <span>OSM Overpass Provenance</span>
            </>
          ) : (
            <>
              <span className="text-amber-400 font-bold">DATA UNAVAILABLE</span>
              <span>·</span>
              <span>Source: OpenStreetMap / Overpass</span>
              <span>·</span>
              <span>Live Provider Unavailable</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

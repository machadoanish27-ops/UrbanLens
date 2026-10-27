import { useQuery, useMutation } from '@tanstack/react-query';
import { urbanLensApi, ApiError } from '../api/client';
import type {
  AirQualityResponse,
  ApiResponse,
  CityDetailResponse,
  CityItem,
  CostOfLivingResponse,
  DbHealthResponse,
  HealthResponse,
  IntelligenceQueryResponse,
  LiveWeatherResponse,
  LLMAskRequest,
  LLMAskResponse,
  PlacesSearchResponse,
  TransitFeedResponse,
  UniversityItem,
} from '../types/api';

export const QUERY_KEYS = {
  health: ['health'] as const,
  dbHealth: ['health', 'db'] as const,
  cities: (params?: Record<string, any>) => ['cities', params] as const,
  city: (cityId: string) => ['city', cityId] as const,
  cityOverview: (cityId: string) => ['city', cityId, 'overview'] as const,
  weather: (cityId: string, days?: number) => ['city', cityId, 'weather', days] as const,
  airQuality: (cityId: string) => ['city', cityId, 'air-quality'] as const,
  cost: (cityId: string) => ['city', cityId, 'cost'] as const,
  universities: (cityId: string) => ['city', cityId, 'universities'] as const,
  transit: (cityId: string) => ['city', cityId, 'transit'] as const,
  places: (lat: number, lon: number, category?: string) => ['places', lat, lon, category] as const,
  intelligence: (cityId: string, q?: string) => ['city', cityId, 'intelligence', q] as const,
};

export function useHealth() {
  return useQuery<HealthResponse, Error>({
    queryKey: QUERY_KEYS.health,
    queryFn: () => urbanLensApi.getHealth(),
    staleTime: 30_000,
    retry: 1,
  });
}

export function useDbHealth() {
  return useQuery<DbHealthResponse, Error>({
    queryKey: QUERY_KEYS.dbHealth,
    queryFn: () => urbanLensApi.getDbHealth(),
    staleTime: 30_000,
    retry: 1,
  });
}

export function useCities(params?: {
  q?: string;
  page?: number;
  page_size?: number;
  country_id?: string;
  min_population?: number;
}) {
  return useQuery<ApiResponse<CityItem[]>, ApiError>({
    queryKey: QUERY_KEYS.cities(params),
    queryFn: () => urbanLensApi.getCities(params),
    staleTime: 60_000,
  });
}

export function useCity(cityId: string) {
  return useQuery<ApiResponse<CityDetailResponse>, ApiError>({
    queryKey: QUERY_KEYS.city(cityId),
    queryFn: () => urbanLensApi.getCity(cityId),
    enabled: Boolean(cityId),
    staleTime: 5 * 60_000,
  });
}

export function useCityOverview(cityId: string) {
  return useQuery<ApiResponse<any>, ApiError>({
    queryKey: QUERY_KEYS.cityOverview(cityId),
    queryFn: () => urbanLensApi.getCityOverview(cityId),
    enabled: Boolean(cityId),
    staleTime: 5 * 60_000,
  });
}

export function useCityWeather(cityId: string, forecastDays: number = 7) {
  return useQuery<ApiResponse<LiveWeatherResponse>, ApiError>({
    queryKey: QUERY_KEYS.weather(cityId, forecastDays),
    queryFn: () => urbanLensApi.getCityWeatherLive(cityId, forecastDays),
    enabled: Boolean(cityId),
    staleTime: 2 * 60_000, // Weather can refresh after 2 minutes
    refetchOnWindowFocus: false,
  });
}

export function useCityAirQuality(cityId: string) {
  return useQuery<ApiResponse<AirQualityResponse>, ApiError>({
    queryKey: QUERY_KEYS.airQuality(cityId),
    queryFn: () => urbanLensApi.getCityAirQuality(cityId),
    enabled: Boolean(cityId),
    staleTime: 5 * 60_000,
    refetchOnWindowFocus: false,
  });
}

export function useCityCost(cityId: string) {
  return useQuery<ApiResponse<CostOfLivingResponse>, ApiError>({
    queryKey: QUERY_KEYS.cost(cityId),
    queryFn: () => urbanLensApi.getCityCostOfLiving(cityId),
    enabled: Boolean(cityId),
    staleTime: 10 * 60_000,
  });
}

export function useCityUniversities(cityId: string) {
  return useQuery<ApiResponse<UniversityItem[]>, ApiError>({
    queryKey: QUERY_KEYS.universities(cityId),
    queryFn: () => urbanLensApi.getCityUniversities(cityId),
    enabled: Boolean(cityId),
    staleTime: 10 * 60_000,
  });
}

export function useCityTransit(cityId: string) {
  return useQuery<ApiResponse<TransitFeedResponse>, ApiError>({
    queryKey: QUERY_KEYS.transit(cityId),
    queryFn: () => urbanLensApi.getTransitInfo(cityId),
    enabled: Boolean(cityId),
    staleTime: 10 * 60_000,
  });
}

export function useCityPlaces(params: {
  lat: number;
  lon: number;
  category?: string;
  radius?: number;
  limit?: number;
}) {
  return useQuery<ApiResponse<PlacesSearchResponse>, ApiError>({
    queryKey: QUERY_KEYS.places(params.lat, params.lon, params.category),
    queryFn: () => urbanLensApi.getPlaces(params),
    enabled: Boolean(params.lat !== undefined && params.lon !== undefined),
    staleTime: 10 * 60_000,
  });
}

export function useCityIntelligence(cityId: string, q?: string) {
  return useQuery<ApiResponse<IntelligenceQueryResponse>, ApiError>({
    queryKey: QUERY_KEYS.intelligence(cityId, q),
    queryFn: () => urbanLensApi.getCityIntelligence(cityId, q),
    enabled: Boolean(cityId),
    staleTime: 5 * 60_000,
  });
}

export function useAskIntelligence() {
  return useMutation<ApiResponse<LLMAskResponse>, ApiError, LLMAskRequest>({
    mutationFn: (payload: LLMAskRequest) => urbanLensApi.askIntelligence(payload),
  });
}

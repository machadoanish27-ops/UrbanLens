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
  CityEducationResponse,
  CityHealthcareResponse,
  CurrencyConversionResponse,
  LiveAirQualityResponse,
  RouteResponse,
  KnowledgeChunkItem,
  KnowledgeStatsResponse,
  CountryItem,
} from '../types/api';

export const QUERY_KEYS = {
  health: ['health'] as const,
  dbHealth: ['health', 'db'] as const,
  cities: (params?: Record<string, any>) => ['cities', params] as const,
  city: (cityId: string) => ['city', cityId] as const,
  cityOverview: (cityId: string) => ['city', cityId, 'overview'] as const,
  weather: (cityId: string, days?: number) => ['city', cityId, 'weather', days] as const,
  airQuality: (cityId: string) => ['city', cityId, 'air-quality'] as const,
  airQualityLive: (cityId: string) => ['city', cityId, 'air-quality-live'] as const,
  cost: (cityId: string) => ['city', cityId, 'cost'] as const,
  universities: (cityId: string) => ['city', cityId, 'universities'] as const,
  education: (cityId: string, type?: string, page?: number) => ['city', cityId, 'education', type, page] as const,
  healthcare: (cityId: string, category?: string) => ['city', cityId, 'healthcare', category] as const,
  transit: (cityId: string) => ['city', cityId, 'transit'] as const,
  currency: (from: string, to: string, amount: number) => ['currency', from, to, amount] as const,
  currencies: ['currencies'] as const,
  places: (lat: number, lon: number, category?: string) => ['places', lat, lon, category] as const,
  intelligence: (cityId: string, q?: string) => ['city', cityId, 'intelligence', q] as const,
  knowledge: (params: Record<string, any>) => ['knowledge', params] as const,
  knowledgeStats: ['knowledge', 'stats'] as const,
  route: (params: Record<string, any>) => ['route', params] as const,
  countries: ['countries'] as const,
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

export function useCurrencyConversion(fromCurrency: string, toCurrency: string, amount: number = 1.0) {
  return useQuery<ApiResponse<CurrencyConversionResponse>, ApiError>({
    queryKey: QUERY_KEYS.currency(fromCurrency, toCurrency, amount),
    queryFn: () => urbanLensApi.convertCurrency(fromCurrency, toCurrency, amount),
    enabled: Boolean(fromCurrency && toCurrency && fromCurrency.length === 3 && toCurrency.length === 3),
    staleTime: 5 * 60_000,
    refetchOnWindowFocus: false,
  });
}

export function useSupportedCurrencies() {
  return useQuery<ApiResponse<Array<{ code: string; symbol: string; name: string }>>, ApiError>({
    queryKey: QUERY_KEYS.currencies,
    queryFn: () => urbanLensApi.getSupportedCurrencies(),
    staleTime: 60 * 60_000,
  });
}

export function useCityAirQualityLive(cityId: string) {
  return useQuery<ApiResponse<LiveAirQualityResponse>, ApiError>({
    queryKey: QUERY_KEYS.airQualityLive(cityId),
    queryFn: () => urbanLensApi.getCityAirQualityLive(cityId),
    enabled: Boolean(cityId),
    staleTime: 3 * 60_000,
    refetchOnWindowFocus: false,
  });
}

export function useCityEducation(cityId: string, type?: string, page: number = 1, pageSize: number = 25) {
  return useQuery<ApiResponse<CityEducationResponse>, ApiError>({
    queryKey: QUERY_KEYS.education(cityId, type, page),
    queryFn: () => urbanLensApi.getCityEducation(cityId, type, page, pageSize),
    enabled: Boolean(cityId),
    staleTime: 10 * 60_000,
  });
}

export function useCityHealthcare(cityId: string, category?: string, radius: number = 5000, limit: number = 30) {
  return useQuery<ApiResponse<CityHealthcareResponse>, ApiError>({
    queryKey: QUERY_KEYS.healthcare(cityId, category),
    queryFn: () => urbanLensApi.getCityHealthcare(cityId, category, radius, limit),
    enabled: Boolean(cityId),
    staleTime: 10 * 60_000,
  });
}

export function useKnowledgeSearch(params: {
  query: string;
  city?: string;
  country?: string;
  category?: string;
  limit?: number;
}) {
  return useQuery<ApiResponse<KnowledgeChunkItem[]>, ApiError>({
    queryKey: QUERY_KEYS.knowledge(params),
    queryFn: () => urbanLensApi.searchKnowledge(params),
    enabled: Boolean(params.query && params.query.trim().length > 0),
    staleTime: 5 * 60_000,
  });
}

export function useKnowledgeStats() {
  return useQuery<ApiResponse<KnowledgeStatsResponse>, ApiError>({
    queryKey: QUERY_KEYS.knowledgeStats,
    queryFn: () => urbanLensApi.getKnowledgeStats(),
    staleTime: 15 * 60_000,
  });
}

export function useRouteCalculation(params: {
  origin_lat: number;
  origin_lon: number;
  dest_lat: number;
  dest_lon: number;
  profile?: 'driving' | 'walking' | 'cycling';
}) {
  return useQuery<ApiResponse<RouteResponse>, ApiError>({
    queryKey: QUERY_KEYS.route(params),
    queryFn: () => urbanLensApi.calculateRoute(params),
    enabled: Boolean(
      params.origin_lat && params.origin_lon && params.dest_lat && params.dest_lon
    ),
    staleTime: 5 * 60_000,
  });
}

export function useCountries() {
  return useQuery<ApiResponse<CountryItem[]>, ApiError>({
    queryKey: QUERY_KEYS.countries,
    queryFn: () => urbanLensApi.getCountries(),
    staleTime: 30 * 60_000,
  });
}

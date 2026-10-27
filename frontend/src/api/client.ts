/**
 * Centralized typed HTTP API client for UrbanLens backend.
 */

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

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/+$/, '');

class ApiError extends Error {
  status: number;
  code: string;
  details?: any;

  constructor(
    status: number,
    code: string,
    message: string,
    details?: any
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});
  headers.set('Accept', 'application/json');

  if (options.body && typeof options.body === 'string' && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorPayload = data?.error;
      const code = errorPayload?.code || `HTTP_${response.status}`;
      const message =
        errorPayload?.message ||
        data?.message ||
        `Request failed with status ${response.status}`;
      throw new ApiError(response.status, code, message, errorPayload?.details);
    }

    return data as ApiResponse<T>;
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      0,
      'NETWORK_ERROR',
      err?.message || 'Network request failed or server is unreachable.'
    );
  }
}

export const urbanLensApi = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return res.json();
  },

  getDbHealth: async (): Promise<DbHealthResponse> => {
    const res = await fetch(`${API_BASE_URL}/health/db`);
    return res.json();
  },

  // Cities
  getCities: async (params?: {
    q?: string;
    page?: number;
    page_size?: number;
    country_id?: string;
    min_population?: number;
  }): Promise<ApiResponse<CityItem[]>> => {
    const query = new URLSearchParams();
    if (params?.q) query.set('q', params.q);
    if (params?.page) query.set('page', String(params.page));
    if (params?.page_size) query.set('page_size', String(params.page_size));
    if (params?.country_id) query.set('country_id', params.country_id);
    if (params?.min_population) query.set('min_population', String(params.min_population));

    const qs = query.toString();
    return request<CityItem[]>(`/api/v1/cities${qs ? `?${qs}` : ''}`);
  },

  getCity: async (cityId: string): Promise<ApiResponse<CityDetailResponse>> => {
    return request<CityDetailResponse>(`/api/v1/cities/${encodeURIComponent(cityId)}`);
  },

  getCityOverview: async (cityId: string): Promise<ApiResponse<any>> => {
    return request<any>(`/api/v1/cities/${encodeURIComponent(cityId)}/overview`);
  },

  // Live Weather
  getCityWeatherLive: async (
    cityId: string,
    forecastDays: number = 7
  ): Promise<ApiResponse<LiveWeatherResponse>> => {
    return request<LiveWeatherResponse>(
      `/api/v1/cities/${encodeURIComponent(cityId)}/weather/live?forecast_days=${forecastDays}`
    );
  },

  // Air Quality
  getCityAirQuality: async (
    cityId: string
  ): Promise<ApiResponse<AirQualityResponse>> => {
    return request<AirQualityResponse>(
      `/api/v1/cities/${encodeURIComponent(cityId)}/air-quality`
    );
  },

  // Cost of Living
  getCityCostOfLiving: async (
    cityId: string
  ): Promise<ApiResponse<CostOfLivingResponse>> => {
    return request<CostOfLivingResponse>(
      `/api/v1/cities/${encodeURIComponent(cityId)}/cost-of-living`
    );
  },

  // Universities
  getCityUniversities: async (
    cityId: string
  ): Promise<ApiResponse<UniversityItem[]>> => {
    return request<UniversityItem[]>(
      `/api/v1/cities/${encodeURIComponent(cityId)}/universities`
    );
  },

  // Multi-Agent Intelligence
  getCityIntelligence: async (
    cityId: string,
    q?: string
  ): Promise<ApiResponse<IntelligenceQueryResponse>> => {
    const query = q ? `?q=${encodeURIComponent(q)}` : '';
    return request<IntelligenceQueryResponse>(
      `/api/v1/cities/${encodeURIComponent(cityId)}/intelligence${query}`
    );
  },

  // Public Transit
  getTransitInfo: async (
    cityId: string
  ): Promise<ApiResponse<TransitFeedResponse>> => {
    return request<TransitFeedResponse>(
      `/api/v1/transit/${encodeURIComponent(cityId)}`
    );
  },

  // Places / Healthcare / Amenities
  getPlaces: async (params: {
    lat: number;
    lon: number;
    category?: string;
    radius?: number;
    limit?: number;
  }): Promise<ApiResponse<PlacesSearchResponse>> => {
    const query = new URLSearchParams();
    query.set('lat', String(params.lat));
    query.set('lon', String(params.lon));
    if (params.category) query.set('category', params.category);
    if (params.radius) query.set('radius', String(params.radius));
    if (params.limit) query.set('limit', String(params.limit));

    return request<PlacesSearchResponse>(`/api/v1/places/search?${query.toString()}`);
  },

  // Groq LLM Intelligence Ask
  askIntelligence: async (
    payload: LLMAskRequest
  ): Promise<ApiResponse<LLMAskResponse>> => {
    return request<LLMAskResponse>('/api/v1/intelligence/ask', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

export { ApiError };

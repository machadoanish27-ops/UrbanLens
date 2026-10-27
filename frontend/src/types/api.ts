/**
 * TypeScript definitions for UrbanLens API contracts, models, and intelligence responses.
 */

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta: ResponseMeta;
}

export interface ResponseMeta {
  request_id?: string | null;
  fetched_at: string;
  source?: string | null;
  pagination?: PaginationMeta | null;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface CityItem {
  city_id: string;
  worldcities_id?: number | null;
  name: string;
  name_ascii?: string | null;
  country_id: string;
  country_iso2: string;
  country_iso3?: string | null;
  admin_name?: string | null;
  capital?: string | null;
  population?: number | null;
  latitude: number;
  longitude: number;
  aliases?: string[];
  provider_identities?: Record<string, string>;
}

export interface CityDetailResponse extends CityItem {
  aliases: string[];
  provider_identities: Record<string, string>;
}

export interface WeatherCurrent {
  temperature_c?: number | null;
  apparent_temperature_c?: number | null;
  relative_humidity_pct?: number | null;
  surface_pressure_mb?: number | null;
  wind_speed_kph?: number | null;
  precipitation_mm?: number | null;
  weather_code?: number | null;
  condition?: string | null;
  observed_at?: string | null;
}

export interface DailyForecast {
  date: string;
  temp_min_c?: number | null;
  temp_max_c?: number | null;
  precipitation_mm?: number | null;
  weather_code?: number | null;
  condition?: string | null;
}

export interface LiveWeatherResponse {
  city_id: string;
  city_name: string;
  latitude: number;
  longitude: number;
  weather: {
    latitude: number;
    longitude: number;
    timezone: string;
    elevation?: number | null;
    current: WeatherCurrent;
    daily_forecasts: DailyForecast[];
  };
  meta: {
    provider: string;
    source: string;
    status: 'fresh' | 'cached' | 'database' | 'error' | 'unavailable';
    fetched_at: string;
    observed_at?: string | null;
    confidence?: number | null;
    error_detail?: string | null;
    cached?: boolean;
  };
}

export interface GlobalWeatherAqItem {
  observed_at: string;
  provider?: string;
  aqi_us_epa?: number | null;
  air_quality_index?: number | null;
  pm25?: number | null;
  pm10?: number | null;
  no2?: number | null;
  so2?: number | null;
  o3?: number | null;
  co?: number | null;
  nitrogen_dioxide?: number | null;
  sulphur_dioxide?: number | null;
  ozone?: number | null;
  carbon_monoxide?: number | null;
}

export interface WhoAnnualAqItem {
  year: number;
  source?: string;
  pm25_annual_mean?: number | null;
  pm10_annual_mean?: number | null;
  no2_annual_mean?: number | null;
  pm25_annual_mean_ug_m3?: number | null;
  pm10_annual_mean_ug_m3?: number | null;
}

export interface AirQualityResponse {
  city_id: string;
  global_weather: GlobalWeatherAqItem[];
  who_annual: WhoAnnualAqItem[];
  available_providers?: string[];
  meta?: {
    sources?: string[];
    records_count?: number;
  };
}

export interface CostMetricItem {
  metric: string;
  value: number;
  currency?: string | null;
  category?: string | null;
  observed_at?: string | null;
  source_id?: string | null;
}

export interface CostOfLivingResponse {
  city_id: string;
  metrics: CostMetricItem[];
  summary?: {
    consumer_price_index?: number | null;
    rent_index?: number | null;
    purchasing_power_index?: number | null;
  } | null;
}

export interface UniversityRankingItem {
  ranking_metric: string;
  ranking_year: number;
  rank?: string | number | null;
}

export interface UniversityItem {
  university_id: string;
  name: string;
  city_id?: string | null;
  country_iso2: string;
  website?: string | null;
  rankings: UniversityRankingItem[];
}

export interface SourceProvenanceItem {
  source_id: string;
  provider?: string | null;
  observed_at?: string | null;
  retrieved_at?: string | null;
  source_version?: string | null;
  confidence?: number | null;
}

export interface KnowledgeEvidenceItem {
  evidence_id: string;
  document_id: string;
  chunk_id: string;
  title: string;
  source: string;
  source_url?: string | null;
  publisher?: string | null;
  text: string;
  category: string;
  city_id?: string | null;
  country_id?: string | null;
  retrieved_at?: string | null;
  retrieval_score?: number | null;
  metadata?: Record<string, any>;
}

export interface AgentResultItem {
  agent_id: string;
  status: string;
  data: Record<string, any>;
  sources: SourceProvenanceItem[];
  knowledge_evidence: KnowledgeEvidenceItem[];
  missing_data: string[];
  unavailable_fields: string[];
  warnings: string[];
  detail?: string | null;
  summary?: string | null;
  confidence: number;
  observed_at?: string | null;
  fetched_at?: string | null;
}

export interface IntelligenceQueryResponse {
  city_id: string;
  query?: string | null;
  overall_status: string;
  location: Record<string, any>;
  selected_agents: string[];
  results: AgentResultItem[];
  signals: Array<{
    domain: string;
    metric: string;
    value: any;
    source?: string | null;
  }>;
  knowledge_evidence: KnowledgeEvidenceItem[];
  summary?: string | null;
  warnings: string[];
  sources: SourceProvenanceItem[];
}

export interface EvidenceUsedItem {
  evidence_id?: string | null;
  title?: string | null;
  source?: string | null;
  source_url?: string | null;
  claim?: string | null;
}

export interface LLMMetadata {
  provider: string;
  model: string;
  status: string;
  latency_ms: number;
  cached?: boolean;
  usage?: Record<string, number> | null;
}

export interface LLMAskRequest {
  query: string;
  city_id?: string | null;
}

export interface LLMAskResponse {
  city_id: string;
  city_name?: string | null;
  country?: string | null;
  query: string;
  answer: string;
  recommendation?: string | null;
  key_points: string[];
  evidence_used: EvidenceUsedItem[];
  sources: string[];
  confidence: number;
  warnings: string[];
  llm: LLMMetadata;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
}

export interface DbHealthResponse {
  status: string;
  database: string;
  latency_ms: number;
  connected: boolean;
  error?: string | null;
}

export interface TransitFeedResponse {
  city_id: string;
  city_name?: string | null;
  transit?: Record<string, any> | null;
  meta: Record<string, any>;
}

export interface PlaceItem {
  id?: string | number;
  name?: string | null;
  category?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  distance_meters?: number | null;
  address?: string | null;
  tags?: Record<string, any>;
}

export interface PlacesSearchResponse {
  latitude: number;
  longitude: number;
  category: string;
  radius_meters: number;
  places: PlaceItem[];
  count: number;
  meta: Record<string, any>;
}

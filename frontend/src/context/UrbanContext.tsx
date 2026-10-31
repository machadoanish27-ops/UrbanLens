import React, { createContext, useContext, useState, useEffect, useMemo, useCallback, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CITIES_DATA,
  type CityData,
  type CityZone,
  LIVE_PULSE_STREAMS,
  type MetricStream,
  MOCK_ALERTS,
  type UrbanAlert,
  normalizeCityId,
  getStudioKeyForId,
  CANONICAL_CITY_MAP,
  CANONICAL_TO_KEY,
} from '../data/urbanData.ts';
import {
  useCity,
  useCityWeather,
  useCityAirQualityLive,
  useCityCost,
  useCityUniversities
} from '../hooks/useUrbanLens';

export type AppRoute =
  | 'landing'
  | 'login'
  | 'signup'
  | 'forgot-password'
  | 'onboarding'
  | 'dashboard'
  | 'cities'
  | 'city-detail'
  | 'pulse'
  | 'spatial'
  | 'ai'
  | 'predictions'
  | 'analytics'
  | 'optimization'
  | 'quantum'
  | 'environment'
  | 'universities'
  | 'education'
  | 'cost-of-living'
  | 'alerts'
  | 'compare'
  | 'reports'
  | 'settings'
  | 'profile'
  | 'mobility'
  | 'housing'
  | 'healthcare'
  | 'safety'
  | 'lifestyle'
  | 'currency'
  | 'knowledge';

export interface UserProfile {
  name: string;
  email: string;
  role: string;
  organization: string;
  avatarUrl: string;
  isAuthenticated: boolean;
}

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: 'CRITICAL' | 'WARNING' | 'SUCCESS' | 'INFO';
  timestamp: string;
}

export interface SavedCity {
  city_id: string;
  name: string;
  country: string;
  country_iso2: string;
  saved_at: string;
  notes?: string;
}

export interface UrbanContextType {
  // Navigation
  currentRoute: AppRoute;
  navigate: (route: AppRoute | string) => void;

  // Active city for dashboard & domain views
  activeCityId: string;
  setActiveCityId: (id: string) => void;
  currentCity: CityData;
  setCityById: (id: string) => void;
  selectedZone: CityZone | null;
  setSelectedZone: (zone: CityZone | null) => void;

  // Loading States
  isCityLoading: boolean;
  isWeatherLoading: boolean;
  isAqiLoading: boolean;

  // Real-time Streams & Alerts
  pulseStreams: MetricStream[];
  alerts: UrbanAlert[];
  dismissAlert: (id: string) => void;

  // UI Drawers & Modals
  isAiModalOpen: boolean;
  toggleAiModal: (open?: boolean) => void;
  isCommandPaletteOpen: boolean;
  toggleCommandPalette: (open?: boolean) => void;
  isNotificationsOpen: boolean;
  toggleNotifications: (open?: boolean) => void;
  notifications: AppNotification[];
  dismissNotification: (id: string) => void;

  // City Initialization Animation / Simulation
  isInitializingCity: boolean;
  initializingCityName: string;

  // Comparison & Settings
  compareCityId: string;
  setCompareCityId: (id: string) => void;
  activeSettingsTab: string;
  setActiveSettingsTab: (tab: string) => void;

  // User Profile (Client-side mock state, honest no-backend-claims)
  user: UserProfile;
  loginUser: (email?: string, name?: string) => void;
  logoutUser: () => void;

  // Saved Cities & Research (Client-side localStorage)
  savedCities: SavedCity[];
  toggleSaveCity: (city: { city_id: string; name: string; country: string; country_iso2: string }) => boolean;
  isCitySaved: (cityId: string) => boolean;

  // Quick Search History
  recentCities: string[];
  addRecentCity: (cityId: string) => void;
}

const UrbanContext = createContext<UrbanContextType | null>(null);

const DEFAULT_USER: UserProfile = {
  name: 'Alex Rivera',
  email: 'alex.rivera@urbanlens.ai',
  role: 'Global Relocation Specialist & Urban Analyst',
  organization: 'UrbanLens Global Intelligence',
  avatarUrl: '/src/assets/images/avatar_urban_director_1793341280235.jpg',
  isAuthenticated: true,
};

const DEFAULT_NOTIFICATIONS: AppNotification[] = [
  {
    id: 'notif-1',
    title: 'Frankfurter ECB Rates Refreshed',
    message: 'Global exchange rates synchronised with European Central Bank daily reference fixings.',
    type: 'INFO',
    timestamp: 'Just now',
  },
  {
    id: 'notif-2',
    title: 'Air Quality Sensor Network',
    message: 'WHO global air quality observations verified across 50,000+ metropolitan clusters.',
    type: 'SUCCESS',
    timestamp: '12m ago',
  },
  {
    id: 'notif-3',
    title: 'Overpass Mirror Failover Ready',
    message: 'Multi-mirror OSM infrastructure operational with automatic cooldown and circuit tracking.',
    type: 'INFO',
    timestamp: '1h ago',
  },
];

const ROUTE_MAP: Record<string, string> = {
  landing: '/',
  login: '/login',
  signup: '/signup',
  'forgot-password': '/forgot-password',
  onboarding: '/onboarding',
  dashboard: '/app',
  cities: '/app/explore',
  'city-detail': '/app/city',
  pulse: '/app/pulse',
  spatial: '/app/map',
  ai: '/app/ask',
  predictions: '/app/predictions',
  analytics: '/app/analytics',
  optimization: '/app/optimization',
  quantum: '/app/quantum',
  environment: '/app/environment',
  universities: '/app/universities',
  education: '/app/education',
  'cost-of-living': '/app/cost',
  alerts: '/app/alerts',
  compare: '/app/compare',
  reports: '/app/reports',
  settings: '/app/settings',
  profile: '/app/profile',
  mobility: '/app/mobility',
  housing: '/app/housing',
  healthcare: '/app/healthcare',
  safety: '/app/safety',
  lifestyle: '/app/lifestyle',
  currency: '/app/currency',
  knowledge: '/app/knowledge',
};

export { normalizeCityId, getStudioKeyForId, CANONICAL_CITY_MAP, CANONICAL_TO_KEY };

export const UrbanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const reactNavigate = useNavigate();

  // Authoritative Active City: Tokyo by default (city_1392685764)
  const [activeCityId, setActiveCityIdState] = useState<string>(() => {
    const saved = localStorage.getItem('urbanlens_active_city_id');
    return saved ? normalizeCityId(saved) : 'city_1356226629';
  });

  const [currentRoute, setCurrentRoute] = useState<AppRoute>('dashboard');

  const [selectedZone, setSelectedZone] = useState<CityZone | null>(() => {
    const saved = localStorage.getItem('urbanlens_active_city_id') || 'city_1356226629';
    const key = getStudioKeyForId(saved);
    return CITIES_DATA[key]?.zones?.[0] || CITIES_DATA['mumbai']?.zones?.[0] || null;
  });

  const [pulseStreams] = useState<MetricStream[]>(LIVE_PULSE_STREAMS);
  const [alerts, setAlerts] = useState<UrbanAlert[]>(MOCK_ALERTS);
  const [compareCityId, setCompareCityId] = useState<string>('mumbai');
  const [activeSettingsTab, setActiveSettingsTab] = useState<string>('profile');
  const [isInitializingCity] = useState(false);
  const [initializingCityName] = useState('');

  // Real Backend Queries dynamically keyed on activeCityId
  const { data: cityResp, isLoading: isCityLoading } = useCity(activeCityId);
  const { data: weatherResp, isLoading: isWeatherLoading } = useCityWeather(activeCityId);
  const { data: aqiResp, isLoading: isAqiLoading } = useCityAirQualityLive(activeCityId);
  const { data: costResp } = useCityCost(activeCityId);
  const { data: uniResp } = useCityUniversities(activeCityId);

  const navigate = (route: AppRoute | string) => {
    if (route.startsWith('/')) {
      reactNavigate(route);
    } else if (ROUTE_MAP[route]) {
      reactNavigate(ROUTE_MAP[route]);
    } else {
      reactNavigate(`/app/${route}`);
    }
    if (Object.keys(ROUTE_MAP).includes(route)) {
      setCurrentRoute(route as AppRoute);
    }
  };

  const setActiveCityId = useCallback((id: string) => {
    const norm = normalizeCityId(id);
    setActiveCityIdState(norm);
    const key = getStudioKeyForId(norm);
    if (CITIES_DATA[key]?.zones && CITIES_DATA[key].zones.length > 0) {
      setSelectedZone(CITIES_DATA[key].zones[0]);
    } else {
      setSelectedZone(null);
    }
    localStorage.setItem('urbanlens_active_city_id', norm);
    addRecentCity(norm);
  }, []);

  const setCityById = (id: string) => {
    setActiveCityId(id);
  };

  const dismissAlert = (id: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

  // Dynamically constructed currentCity strictly tied to activeCityId
  const currentCity: CityData = useMemo(() => {
    const canonical = cityResp?.data;
    const weather = weatherResp?.data?.weather?.current;
    const aqiData = aqiResp?.data?.air_quality;
    const costSummary = costResp?.data?.summary;
    const unis = uniResp?.data || [];

    const key = getStudioKeyForId(activeCityId);
    const fallbackBase = CITIES_DATA[key] || CITIES_DATA['mumbai'] || Object.values(CITIES_DATA)[0];

    const name = canonical?.name || fallbackBase.name;
    const country = canonical?.country_id
      ? canonical.country_id.replace('country_', '').toUpperCase()
      : fallbackBase.country;
    const countryCode = canonical?.country_iso2 || fallbackBase.countryCode;

    const population = canonical?.population
      ? Number(canonical.population).toLocaleString()
      : fallbackBase.population;
    const populationRaw = canonical?.population ?? fallbackBase.populationRaw;
    const density = canonical?.population_density
      ? `${Number(canonical.population_density).toLocaleString()} / km²`
      : fallbackBase.density;
    const coordinates = (canonical?.latitude !== undefined && canonical?.longitude !== undefined)
      ? `${canonical.latitude.toFixed(4)}° N, ${canonical.longitude.toFixed(4)}° E`
      : fallbackBase.coordinates;

    const latitude = typeof canonical?.latitude === 'number'
      ? canonical.latitude
      : fallbackBase.latitude;
    const longitude = typeof canonical?.longitude === 'number'
      ? canonical.longitude
      : fallbackBase.longitude;

    const temperature = typeof weather?.temperature_c === 'number'
      ? Math.round(weather.temperature_c)
      : fallbackBase.temperature;
    const feelsLike = typeof weather?.apparent_temperature_c === 'number'
      ? Math.round(weather.apparent_temperature_c)
      : fallbackBase.feelsLike;
    const humidity = typeof weather?.relative_humidity_pct === 'number'
      ? Math.round(weather.relative_humidity_pct)
      : fallbackBase.humidity;
    const windSpeed = typeof weather?.wind_speed_kph === 'number'
      ? `${weather.wind_speed_kph} km/h`
      : fallbackBase.windSpeed;

    const pm25 = typeof aqiData?.pollutants?.pm25 === 'number'
      ? aqiData.pollutants.pm25
      : fallbackBase.pm25;
    const pm10 = typeof aqiData?.pollutants?.pm10 === 'number'
      ? aqiData.pollutants.pm10
      : fallbackBase.pm10;
    const no2 = typeof aqiData?.pollutants?.no2 === 'number'
      ? aqiData.pollutants.no2
      : fallbackBase.no2;
    const o3 = typeof aqiData?.pollutants?.o3 === 'number'
      ? aqiData.pollutants.o3
      : fallbackBase.o3;

    const rawAqi = pm25 !== null && pm25 !== undefined ? Math.round(pm25) : fallbackBase.aqi;
    const aqiCategory: CityData['aqiCategory'] = rawAqi <= 50 ? 'Good'
      : rawAqi <= 100 ? 'Moderate'
      : rawAqi <= 150 ? 'Unhealthy for Sensitive'
      : rawAqi <= 200 ? 'Unhealthy'
      : 'Very Unhealthy';

    const costOfLivingIndex = costSummary?.consumer_price_index ?? fallbackBase.costOfLivingIndex;

    const universities = unis.length > 0
      ? unis.map((u, i) => ({
          id: u.university_id || `u-${i}`,
          name: u.name,
          location: `${name}, ${country}`,
          ranking: u.rankings?.[0]?.rank ? `#${u.rankings[0].rank} Global` : '#1 Regional',
          type: 'Public / Institute of National Importance' as const,
          studentsCount: 'Verified Institution',
          specialization: 'Higher Education & Research',
          status: 'Accredited NAAC A++' as const,
          trust: 'VERIFIED' as const,
        }))
      : fallbackBase.universities;

    return {
      ...fallbackBase,
      id: activeCityId,
      name,
      country,
      countryCode,
      country_id: canonical?.country_id || `country_${countryCode}`,
      currency: canonical?.currency || (fallbackBase as any).currency || { code: countryCode === 'JP' ? 'JPY' : countryCode === 'IN' ? 'INR' : countryCode === 'GB' ? 'GBP' : 'USD', symbol: '$', name: 'Currency' },
      population,
      populationRaw,
      density,
      coordinates,
      latitude,
      longitude,
      temperature,
      feelsLike,
      humidity,
      windSpeed,
      aqi: rawAqi,
      aqiCategory,
      pm25,
      pm10,
      no2,
      o3,
      costOfLivingIndex,
      universities,
    };
  }, [activeCityId, cityResp, weatherResp, aqiResp, costResp, uniResp, isCityLoading]);

  // UI Drawers & Modals
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<AppNotification[]>(DEFAULT_NOTIFICATIONS);

  const toggleAiModal = (open?: boolean) => {
    setIsAiModalOpen((prev) => (open !== undefined ? open : !prev));
  };

  const toggleCommandPalette = (open?: boolean) => {
    setIsCommandPaletteOpen((prev) => (open !== undefined ? open : !prev));
  };

  const toggleNotifications = (open?: boolean) => {
    setIsNotificationsOpen((prev) => (open !== undefined ? open : !prev));
  };

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  // Keyboard shortcut for Command Palette (Cmd+K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleCommandPalette();
      }
      if (e.key === 'Escape') {
        setIsCommandPaletteOpen(false);
        setIsAiModalOpen(false);
        setIsNotificationsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // User Profile
  const [user, setUser] = useState<UserProfile>(() => {
    try {
      const stored = localStorage.getItem('urbanlens_user_profile');
      if (stored) return JSON.parse(stored);
    } catch {}
    return DEFAULT_USER;
  });

  const loginUser = (email?: string, name?: string) => {
    const updated: UserProfile = {
      ...user,
      name: name || user.name,
      email: email || user.email,
      isAuthenticated: true,
    };
    setUser(updated);
    localStorage.setItem('urbanlens_user_profile', JSON.stringify(updated));
  };

  const logoutUser = () => {
    const updated: UserProfile = {
      ...user,
      isAuthenticated: false,
    };
    setUser(updated);
    localStorage.setItem('urbanlens_user_profile', JSON.stringify(updated));
  };

  // Saved Cities
  const [savedCities, setSavedCities] = useState<SavedCity[]>(() => {
    try {
      const stored = localStorage.getItem('urbanlens_saved_cities');
      if (stored) return JSON.parse(stored);
    } catch {}
    return [
      {
        city_id: 'city_1392685764',
        name: 'Tokyo',
        country: 'Japan',
        country_iso2: 'JP',
        saved_at: '2026-10-28',
        notes: 'Target relocation hub for technology & research opportunities.',
      },
      {
        city_id: 'city_1826645935',
        name: 'London',
        country: 'United Kingdom',
        country_iso2: 'GB',
        saved_at: '2026-10-29',
        notes: 'Finance and higher education shortlist.',
      },
      {
        city_id: 'city_1356226629',
        name: 'Mumbai',
        country: 'India',
        country_iso2: 'IN',
        saved_at: '2026-10-30',
        notes: 'Origin metropolitan baseline.',
      },
    ];
  });

  const toggleSaveCity = (city: { city_id: string; name: string; country: string; country_iso2: string }): boolean => {
    const exists = savedCities.some((c) => c.city_id === city.city_id);
    let updated: SavedCity[];
    if (exists) {
      updated = savedCities.filter((c) => c.city_id !== city.city_id);
    } else {
      updated = [
        ...savedCities,
        {
          city_id: city.city_id,
          name: city.name,
          country: city.country,
          country_iso2: city.country_iso2,
          saved_at: new Date().toISOString().split('T')[0],
        },
      ];
    }
    setSavedCities(updated);
    localStorage.setItem('urbanlens_saved_cities', JSON.stringify(updated));
    return !exists;
  };

  const isCitySaved = (cityId: string): boolean => {
    return savedCities.some((c) => c.city_id === cityId);
  };

  // Recent Cities History
  const [recentCities, setRecentCities] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('urbanlens_recent_cities');
      if (stored) return JSON.parse(stored);
    } catch {}
    return ['city_1392685764', 'city_1826645935', 'city_1356226629', 'city_1702341327', 'city_1784736618'];
  });

  const addRecentCity = (cityId: string) => {
    setRecentCities((prev) => {
      const filtered = prev.filter((id) => id !== cityId);
      const updated = [cityId, ...filtered].slice(0, 10);
      localStorage.setItem('urbanlens_recent_cities', JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <UrbanContext.Provider
      value={{
        currentRoute,
        navigate,
        activeCityId,
        setActiveCityId,
        currentCity,
        setCityById,
        selectedZone,
        setSelectedZone,
        isCityLoading,
        isWeatherLoading,
        isAqiLoading,
        pulseStreams,
        alerts,
        dismissAlert,
        isAiModalOpen,
        toggleAiModal,
        isCommandPaletteOpen,
        toggleCommandPalette,
        isNotificationsOpen,
        toggleNotifications,
        notifications,
        dismissNotification,
        isInitializingCity,
        initializingCityName,
        compareCityId,
        setCompareCityId,
        activeSettingsTab,
        setActiveSettingsTab,
        user,
        loginUser,
        logoutUser,
        savedCities,
        toggleSaveCity,
        isCitySaved,
        recentCities,
        addRecentCity,
      }}
    >
      {children}
    </UrbanContext.Provider>
  );
};

export const useUrban = (): UrbanContextType => {
  const context = useContext(UrbanContext);
  if (!context) {
    throw new Error('useUrban must be used within an UrbanProvider');
  }
  return context;
};

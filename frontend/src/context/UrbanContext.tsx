import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CITIES_DATA,
  type CityData,
  type CityZone,
  LIVE_PULSE_STREAMS,
  type MetricStream,
  MOCK_ALERTS,
  type UrbanAlert
} from '../data/urbanData.ts';

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
  | 'profile';

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
  cities: '/app/cities',
  'city-detail': '/app/city',
  pulse: '/app/pulse',
  spatial: '/app/spatial',
  ai: '/app/ai',
  predictions: '/app/predictions',
  analytics: '/app/analytics',
  optimization: '/app/optimization',
  quantum: '/app/quantum',
  environment: '/app/environment',
  universities: '/app/universities',
  education: '/app/education',
  'cost-of-living': '/app/cost-of-living',
  alerts: '/app/alerts',
  compare: '/app/compare',
  reports: '/app/reports',
  settings: '/app/settings',
  profile: '/app/profile',
};

export const UrbanProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const reactNavigate = useNavigate();

  // Active City: Tokyo by default (city_1392685764)
  const [activeCityId, setActiveCityIdState] = useState<string>(() => {
    return localStorage.getItem('urbanlens_active_city_id') || 'city_1392685764';
  });

  const [currentRoute, setCurrentRoute] = useState<AppRoute>('dashboard');
  const [studioCityKey, setStudioCityKey] = useState<string>('mumbai');
  const [selectedZone, setSelectedZone] = useState<CityZone | null>(
    CITIES_DATA['mumbai']?.zones?.[0] || null
  );
  const [pulseStreams] = useState<MetricStream[]>(LIVE_PULSE_STREAMS);
  const [alerts, setAlerts] = useState<UrbanAlert[]>(MOCK_ALERTS);
  const [compareCityId, setCompareCityId] = useState<string>('tokyo');
  const [activeSettingsTab, setActiveSettingsTab] = useState<string>('profile');
  const [isInitializingCity] = useState(false);
  const [initializingCityName] = useState('');

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

  const currentCity = CITIES_DATA[studioCityKey] || CITIES_DATA['mumbai'] || Object.values(CITIES_DATA)[0];

  const setCityById = (id: string) => {
    const norm = id.toLowerCase();
    if (CITIES_DATA[norm]) {
      setStudioCityKey(norm);
      setSelectedZone(CITIES_DATA[norm].zones?.[0] || null);
    }
    setActiveCityId(id);
  };

  const dismissAlert = (id: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

  const setActiveCityId = (id: string) => {
    setActiveCityIdState(id);
    localStorage.setItem('urbanlens_active_city_id', id);
    addRecentCity(id);
  };

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

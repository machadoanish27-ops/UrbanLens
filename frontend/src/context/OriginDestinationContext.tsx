import React, { createContext, useContext, useState } from 'react';

export interface OriginLocation {
  country_id: string;
  country_name: string;
  country_iso2: string;
  city_id: string;
  city_name: string;
  currency_code: string;
  currency_symbol: string;
  currency_name: string;
  source: string;
}

export interface DestinationLocation {
  country_id?: string;
  country_name?: string;
  country_iso2: string;
  city_id: string;
  city_name: string;
  currency_code: string;
  currency_symbol: string;
  currency_name: string;
}

export const DEFAULT_ORIGIN: OriginLocation = {
  country_id: 'country_IN',
  country_name: 'India',
  country_iso2: 'IN',
  city_id: 'city_1356226629',
  city_name: 'Mumbai',
  currency_code: 'INR',
  currency_symbol: '₹',
  currency_name: 'Indian Rupee',
  source: 'User Relocation Profile (Persisted)',
};

const STORAGE_KEY = 'urbanlens_origin_profile_v1';

interface OriginDestinationContextType {
  origin: OriginLocation;
  destination: DestinationLocation | null;
  setOrigin: (origin: OriginLocation) => void;
  setDestination: (destination: DestinationLocation | null) => void;
  isOriginModalOpen: boolean;
  openOriginModal: () => void;
  closeOriginModal: () => void;
}

const OriginDestinationContext = createContext<OriginDestinationContextType | undefined>(undefined);

export const OriginDestinationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [origin, setOriginState] = useState<OriginLocation>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      // Fallback on parse failure
    }
    return DEFAULT_ORIGIN;
  });

  const [destination, setDestination] = useState<DestinationLocation | null>(null);
  const [isOriginModalOpen, setIsOriginModalOpen] = useState(false);

  const setOrigin = (newOrigin: OriginLocation) => {
    setOriginState(newOrigin);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newOrigin));
    } catch {
      // Ignore quota errors
    }
  };

  const openOriginModal = () => setIsOriginModalOpen(true);
  const closeOriginModal = () => setIsOriginModalOpen(false);

  return (
    <OriginDestinationContext.Provider
      value={{
        origin,
        destination,
        setOrigin,
        setDestination,
        isOriginModalOpen,
        openOriginModal,
        closeOriginModal,
      }}
    >
      {children}
    </OriginDestinationContext.Provider>
  );
};

export const useOriginDestination = (): OriginDestinationContextType => {
  const context = useContext(OriginDestinationContext);
  if (!context) {
    throw new Error('useOriginDestination must be used within an OriginDestinationProvider');
  }
  return context;
};

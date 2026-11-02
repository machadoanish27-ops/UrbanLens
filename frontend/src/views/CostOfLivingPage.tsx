import React, { useMemo } from 'react';
import { useUrban } from '../context/UrbanContext';
import { useCityCost } from '../hooks/useUrbanLens';
import {
  Coins,
  Home,
  Utensils,
  ShoppingBag,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Building,
  Info,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';
import { sanitizeExternalUrl, getDisplayDomain } from '../utils/url';

interface HousingPortal {
  name: string;
  url: string;
  description: string;
  coverage: string;
}

const COUNTRY_HOUSING_PORTALS: Record<string, HousingPortal[]> = {
  IN: [
    {
      name: 'MagicBricks',
      url: 'https://www.magicbricks.com',
      description: 'Major Indian residential and commercial real estate portal.',
      coverage: 'Pan-India, Metropolitan & Tier-1 Hubs',
    },
    {
      name: '99acres',
      url: 'https://www.99acres.com',
      description: 'Extensive property listings, verified rent aggregations, and district insights.',
      coverage: 'Pan-India verified inventory',
    },
    {
      name: 'Housing.com',
      url: 'https://housing.com',
      description: 'Map-based rental listings with verified photos and locality price trends.',
      coverage: 'Major Indian cities',
    },
  ],
  GB: [
    {
      name: 'Rightmove',
      url: 'https://www.rightmove.co.uk',
      description: 'Largest UK property marketplace for lettings, sales, and rental comparisons.',
      coverage: 'United Kingdom Nationwide',
    },
    {
      name: 'Zoopla',
      url: 'https://www.zoopla.co.uk',
      description: 'Comprehensive UK home search with automated valuation estimates and commute times.',
      coverage: 'United Kingdom Nationwide',
    },
    {
      name: 'OnTheMarket',
      url: 'https://www.onthemarket.com',
      description: 'Agent-backed portal offering exclusive new-to-market rental properties.',
      coverage: 'United Kingdom Nationwide',
    },
  ],
  US: [
    {
      name: 'Zillow',
      url: 'https://www.zillow.com',
      description: 'Leading US real estate and rental marketplace with Zestimate valuations.',
      coverage: 'United States Nationwide',
    },
    {
      name: 'Realtor.com',
      url: 'https://www.realtor.com',
      description: 'Official MLS-linked listing portal for verified residential rentals and sales.',
      coverage: 'United States Nationwide',
    },
    {
      name: 'Redfin',
      url: 'https://www.redfin.com',
      description: 'Brokerage marketplace with real-time MLS data and neighborhood market insights.',
      coverage: 'Major US metropolitan areas',
    },
  ],
  JP: [
    {
      name: 'SUUMO (スーモ)',
      url: 'https://suumo.jp',
      description: 'Japan’s premier Recruit-operated property portal for apartments and rentals.',
      coverage: 'Tokyo, Osaka, Nagoya & Japan Nationwide',
    },
    {
      name: 'HOME’S (ライフルホームズ)',
      url: 'https://www.homes.co.jp',
      description: 'Comprehensive Japanese rental search platform with neighborhood scorecards.',
      coverage: 'Japan Nationwide',
    },
    {
      name: 'Real Estate Japan',
      url: 'https://realestate.co.jp',
      description: 'English-friendly Japanese property platform for international residents and expats.',
      coverage: 'Tokyo, Yokohama, Kansai, Fukuoka',
    },
  ],
  AE: [
    {
      name: 'Property Finder',
      url: 'https://www.propertyfinder.ae',
      description: 'Leading UAE real estate portal with verified landlord and agent listings.',
      coverage: 'Dubai, Abu Dhabi, Sharjah, UAE',
    },
    {
      name: 'Bayut',
      url: 'https://www.bayut.com',
      description: 'Comprehensive property search platform with TruCheck verified listings.',
      coverage: 'Dubai, Abu Dhabi, Northern Emirates',
    },
    {
      name: 'Dubizzle',
      url: 'https://dubai.dubizzle.com/property-for-rent/',
      description: 'Classifieds and direct rental portal widely used across the Emirates.',
      coverage: 'Dubai & UAE Nationwide',
    },
  ],
  DE: [
    {
      name: 'ImmobilienScout24',
      url: 'https://www.immobilienscout24.de',
      description: 'Germany’s leading real estate portal for apartments, flats, and house rentals.',
      coverage: 'Berlin, Munich, Hamburg, Frankfurt & Germany',
    },
    {
      name: 'Immowelt',
      url: 'https://www.immowelt.de',
      description: 'Major German property search engine with verified private and agent offers.',
      coverage: 'Germany & Austria',
    },
  ],
  AU: [
    {
      name: 'RealEstate.com.au',
      url: 'https://www.realestate.com.au',
      description: 'Australia’s largest property and rental portal operated by REA Group.',
      coverage: 'Sydney, Melbourne, Brisbane & Australia Nationwide',
    },
    {
      name: 'Domain',
      url: 'https://www.domain.com.au',
      description: 'Leading Australian digital real estate portal with auction and rental indices.',
      coverage: 'Australia Nationwide',
    },
  ],
  CA: [
    {
      name: 'Realtor.ca',
      url: 'https://www.realtor.ca',
      description: 'Official Canadian Real Estate Association marketplace for residential listings.',
      coverage: 'Canada Nationwide',
    },
    {
      name: 'Rentals.ca',
      url: 'https://rentals.ca',
      description: 'Specialized Canadian rental platform with monthly national rent reports.',
      coverage: 'Toronto, Vancouver, Montreal & Canada',
    },
  ],
  SG: [
    {
      name: 'PropertyGuru Singapore',
      url: 'https://www.propertyguru.com.sg',
      description: 'Singapore’s dominant proptech portal for HDB, condo, and landed home rentals.',
      coverage: 'Singapore Nationwide',
    },
    {
      name: '99.co Singapore',
      url: 'https://www.99.co/singapore',
      description: 'Modern map-centric property search platform with MRT distance filters.',
      coverage: 'Singapore Nationwide',
    },
  ],
  ID: [
    {
      name: 'Rumah123',
      url: 'https://www.rumah123.com',
      description: 'Leading Indonesian property portal for residential homes and apartments.',
      coverage: 'Jakarta, Surabaya, Bandung, Bali',
    },
    {
      name: 'Lamudi Indonesia',
      url: 'https://www.lamudi.co.id',
      description: 'Curated real estate platform for new developments and long-term leases.',
      coverage: 'Jabodetabek & Indonesia',
    },
  ],
};

const GLOBAL_HOUSING_PORTALS: HousingPortal[] = [
  {
    name: 'HousingAnywhere',
    url: 'https://housinganywhere.com',
    description: 'International student and expat accommodation platform across 400+ cities.',
    coverage: 'Global / Expat Relocation',
  },
  {
    name: 'Nestpick',
    url: 'https://www.nestpick.com',
    description: 'Global furnished apartment aggregator for remote professionals and relocators.',
    coverage: 'Worldwide Furnished Rentals',
  },
];

export const CostOfLivingPage: React.FC = () => {
  const { currentCity, activeCityId } = useUrban();
  const { data: costResp, isLoading: isCostLoading } = useCityCost(activeCityId);

  // Extract canonical metrics list
  const metricsList = useMemo(() => {
    return costResp?.data?.metrics || [];
  }, [costResp]);

  const isAvailable = useMemo(() => {
    return (
      costResp?.data?.is_available === true &&
      metricsList.length > 0
    );
  }, [costResp, metricsList]);

  // Index map
  const metricsMap = useMemo(() => {
    const map = new Map<string, number>();
    for (const m of metricsList) {
      if (m.metric && typeof m.value === 'number') {
        map.set(m.metric.toLowerCase().trim(), m.value);
      }
    }
    return map;
  }, [metricsList]);

  const costOfLivingIndex = metricsMap.get('cost of living index') ?? currentCity.costOfLivingIndex;
  const rentIndex = metricsMap.get('rent index') ?? currentCity.housingIndex;
  const colPlusRentIndex = metricsMap.get('cost of living plus rent index');
  const groceriesIndex = metricsMap.get('groceries index');
  const restaurantIndex = metricsMap.get('restaurant price index');
  const purchasingPowerIndex = metricsMap.get('local purchasing power index');

  // Country portals
  const countryCode = (currentCity.countryCode || '').toUpperCase();
  const portals = COUNTRY_HOUSING_PORTALS[countryCode] || GLOBAL_HOUSING_PORTALS;

  // Helper to format comparative difference relative to NYC baseline (100)
  const formatNycDelta = (val?: number | null) => {
    if (val === undefined || val === null) return null;
    const diff = Math.round((100 - val) * 10) / 10;
    if (diff > 0) {
      return {
        text: `${diff}% cheaper than NYC benchmark`,
        isCheaper: true,
      };
    } else if (diff < 0) {
      return {
        text: `${Math.abs(diff)}% higher than NYC benchmark`,
        isCheaper: false,
      };
    } else {
      return {
        text: 'Identical to NYC baseline (100.0)',
        isCheaper: true,
      };
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Coins className="w-4 h-4 text-cyan-400" />
            <span>MUNICIPAL ECONOMIC BENCHMARK</span>
            <span>·</span>
            <DataTrustBadge status={isAvailable ? 'VERIFIED' : 'DATA UNAVAILABLE'} size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Cost of Living Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Verified consumer expenditure and affordability benchmarks normalized against New York City baseline (NYC = 100.0).
          </p>
        </div>

        {isAvailable && costOfLivingIndex !== null && costOfLivingIndex !== undefined && (
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] text-right min-w-[180px]">
            <div className="text-[10px] font-mono text-slate-400">OVERALL INDEX</div>
            <div className="text-3xl font-black font-mono text-emerald-400">
              {costOfLivingIndex.toFixed(1)}
            </div>
            <div className="text-[10px] font-mono text-slate-400 mt-0.5">Base NYC = 100.0</div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {!isAvailable && !isCostLoading ? (
        /* Honest Unavailable State */
        <div className="p-12 rounded-3xl bg-[#0B1726]/80 border border-rose-500/30 text-center max-w-2xl mx-auto space-y-4 shadow-2xl">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-rose-950/50 border border-rose-500/40 flex items-center justify-center text-rose-400">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold font-mono text-white uppercase tracking-wider">
            COST INTELLIGENCE UNAVAILABLE
          </h2>
          <p className="text-sm text-slate-300 font-sans leading-relaxed">
            UrbanLens does not currently have verified city-level cost data for {currentCity.name}. <br />
            <strong className="text-white font-mono">No estimated or fabricated value is being displayed.</strong>
          </p>
          <div className="inline-block pt-2">
            <DataTrustBadge status="DATA UNAVAILABLE" size="md" />
          </div>
        </div>
      ) : (
        /* Populated State with Verified Index Components */
        <div className="space-y-8">
          {/* 6-Metric Breakdown Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* 1. Cost of Living Index */}
            {costOfLivingIndex !== null && costOfLivingIndex !== undefined && (
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <Coins className="w-4 h-4 text-cyan-400" />
                    <span className="font-semibold text-slate-200">COST OF LIVING INDEX</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/30">
                    EXCL. RENT
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono text-white">
                  {costOfLivingIndex.toFixed(1)}
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-400 rounded-full"
                    style={{ width: `${Math.min(100, costOfLivingIndex)}%` }}
                  />
                </div>
                {formatNycDelta(costOfLivingIndex) && (
                  <p className="text-[11px] text-slate-300 font-mono flex items-center gap-1.5">
                    {formatNycDelta(costOfLivingIndex)?.isCheaper ? (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
                    )}
                    <span>{formatNycDelta(costOfLivingIndex)?.text}</span>
                  </p>
                )}
              </div>
            )}

            {/* 2. Rent Index */}
            {rentIndex !== null && rentIndex !== undefined && (
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <Home className="w-4 h-4 text-emerald-400" />
                    <span className="font-semibold text-slate-200">RENT INDEX</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/30">
                    HOUSING
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono text-white">
                  {rentIndex.toFixed(1)}
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 rounded-full"
                    style={{ width: `${Math.min(100, rentIndex)}%` }}
                  />
                </div>
                {formatNycDelta(rentIndex) && (
                  <p className="text-[11px] text-slate-300 font-mono flex items-center gap-1.5">
                    {formatNycDelta(rentIndex)?.isCheaper ? (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
                    )}
                    <span>{formatNycDelta(rentIndex)?.text}</span>
                  </p>
                )}
              </div>
            )}

            {/* 3. Cost of Living Plus Rent */}
            {colPlusRentIndex !== undefined && (
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <Building className="w-4 h-4 text-blue-400" />
                    <span className="font-semibold text-slate-200">COMPOSITE (COL + RENT)</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-500/30">
                    COMBINED
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono text-white">
                  {colPlusRentIndex.toFixed(1)}
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-400 rounded-full"
                    style={{ width: `${Math.min(100, colPlusRentIndex)}%` }}
                  />
                </div>
                {formatNycDelta(colPlusRentIndex) && (
                  <p className="text-[11px] text-slate-300 font-mono flex items-center gap-1.5">
                    {formatNycDelta(colPlusRentIndex)?.isCheaper ? (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
                    )}
                    <span>{formatNycDelta(colPlusRentIndex)?.text}</span>
                  </p>
                )}
              </div>
            )}

            {/* 4. Groceries Index */}
            {groceriesIndex !== undefined && (
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <ShoppingBag className="w-4 h-4 text-amber-400" />
                    <span className="font-semibold text-slate-200">GROCERIES BASKET</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-500/30">
                    MARKET
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono text-white">
                  {groceriesIndex.toFixed(1)}
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-400 rounded-full"
                    style={{ width: `${Math.min(100, groceriesIndex)}%` }}
                  />
                </div>
                {formatNycDelta(groceriesIndex) && (
                  <p className="text-[11px] text-slate-300 font-mono flex items-center gap-1.5">
                    {formatNycDelta(groceriesIndex)?.isCheaper ? (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
                    )}
                    <span>{formatNycDelta(groceriesIndex)?.text}</span>
                  </p>
                )}
              </div>
            )}

            {/* 5. Restaurant Price Index */}
            {restaurantIndex !== undefined && (
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <Utensils className="w-4 h-4 text-purple-400" />
                    <span className="font-semibold text-slate-200">RESTAURANTS & DINING</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-500/30">
                    DINING OUT
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono text-white">
                  {restaurantIndex.toFixed(1)}
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-400 rounded-full"
                    style={{ width: `${Math.min(100, restaurantIndex)}%` }}
                  />
                </div>
                {formatNycDelta(restaurantIndex) && (
                  <p className="text-[11px] text-slate-300 font-mono flex items-center gap-1.5">
                    {formatNycDelta(restaurantIndex)?.isCheaper ? (
                      <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <TrendingUp className="w-3.5 h-3.5 text-rose-400" />
                    )}
                    <span>{formatNycDelta(restaurantIndex)?.text}</span>
                  </p>
                )}
              </div>
            )}

            {/* 6. Local Purchasing Power */}
            {purchasingPowerIndex !== undefined && (
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-teal-400" />
                    <span className="font-semibold text-slate-200">LOCAL PURCHASING POWER</span>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-teal-950 text-teal-300 border border-teal-500/30">
                    REAL WAGE
                  </span>
                </div>
                <div className="text-3xl font-extrabold font-mono text-white">
                  {purchasingPowerIndex.toFixed(1)}
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-teal-400 rounded-full"
                    style={{ width: `${Math.min(100, purchasingPowerIndex)}%` }}
                  />
                </div>
                <p className="text-[11px] text-slate-300 font-mono">
                  Relative purchasing power of typical net salary vs NYC resident (100.0).
                </p>
              </div>
            )}
          </div>

          {/* VERIFIED HOUSING & RENTAL PORTAL DISCOVERY SECTION */}
          <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E334A] pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <Home className="w-5 h-5 text-cyan-400" />
                  <h2 className="text-base sm:text-lg font-bold font-mono text-white uppercase tracking-wider">
                    VERIFIED HOUSING & RENTAL PORTALS
                  </h2>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-cyan-950 text-cyan-300 border border-cyan-500/30 font-semibold">
                    {currentCity.country} ({countryCode || 'GLOBAL'})
                  </span>
                </div>
                <p className="text-xs text-slate-400 font-sans mt-1">
                  Established regional property portals for verified apartment rentals, shared leases, and district housing search.
                </p>
              </div>
              <DataTrustBadge status="VERIFIED" size="sm" />
            </div>

            {/* Portals Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {portals.map((portal) => {
                const safeUrl = sanitizeExternalUrl(portal.url);
                const domain = getDisplayDomain(portal.url);

                return (
                  <div
                    key={portal.name}
                    className="rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 p-5 transition-all flex flex-col justify-between space-y-4"
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="text-sm font-bold font-mono text-white flex items-center gap-1.5">
                          <Building className="w-4 h-4 text-cyan-400 shrink-0" />
                          <span>{portal.name}</span>
                        </h3>
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                          {domain}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 font-sans leading-relaxed">
                        {portal.description}
                      </p>
                      <div className="text-[11px] font-mono text-cyan-400/90 flex items-center gap-1 pt-1">
                        <Info className="w-3 h-3 shrink-0" />
                        <span>Coverage: {portal.coverage}</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-[#1E334A]/60 flex items-center justify-between">
                      <span className="text-[10px] font-mono text-slate-400">
                        Independent Discovery
                      </span>
                      {safeUrl ? (
                        <a
                          href={safeUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 hover:border-cyan-400 text-cyan-300 text-xs font-mono font-medium transition-all"
                        >
                          <span>Explore Listings</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      ) : (
                        <span className="text-xs text-slate-400 font-mono">Verified Portal</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Disclaimer */}
            <div className="p-4 rounded-xl bg-[#07111F]/60 border border-[#1E334A]/60 flex items-start gap-3 text-xs text-slate-400 font-sans">
              <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
              <p>
                <strong className="text-slate-200">Municipal Discovery Notice:</strong> UrbanLens does not broker, list, or intermediate property transactions. Housing portals are linked for independent municipal discovery. External listing availability, deposit requirements, and leasing terms vary by district and property management.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

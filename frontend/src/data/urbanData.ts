/**
 * UrbanLens Real-time Urban Data & Telemetry Matrix
 * Production schema for cities, live pulses, zones, predictions, quantum jobs, and analytics.
 */

export interface MetricStream {
  id: string;
  category: 'TRAFFIC' | 'AIR QUALITY' | 'ENERGY' | 'WATER' | 'TRANSIT';
  name: string;
  currentValue: string;
  rawValue: number;
  unit: string;
  delta: string;
  trend: 'up' | 'down' | 'neutral';
  status: 'OPTIMAL' | 'MODERATE' | 'SURGE' | 'ELEVATED' | 'CRITICAL';
  source: string;
  timestamp: string;
  sparkline: number[];
  trust: 'LIVE' | 'VERIFIED' | 'PREDICTED' | 'INFERENCE' | 'SIMULATION' | 'DATA UNAVAILABLE';
}

export interface CityZone {
  id: string;
  name: string;
  traffic: number; // percentage
  trafficDelta: string;
  aqi: number;
  energyDelta: string;
  transitLoad: number;
  aiSignal: string;
  confidence: number;
  status: 'NORMAL' | 'ELEVATED' | 'HIGH_RISK';
  coordinates: [number, number]; // [x, y] on visual spatial grid 0..100
  prediction: string;
  recommendation: string;
}

export interface UniversityItem {
  id: string;
  name: string;
  location: string;
  ranking: string;
  type: 'Public / Institute of National Importance' | 'State University' | 'Private Autonomous' | 'Deemed University';
  studentsCount: string;
  specialization: string;
  status: 'Accredited NAAC A++' | 'NIRF Top 10' | 'Autonomous Center of Excellence';
  trust: 'VERIFIED';
}

export interface CityData {
  id: string;
  name: string;
  country: string;
  countryCode: string;
  population: string;
  populationRaw: number;
  density: string;
  coordinates: string;
  temperature: number;
  feelsLike: number;
  humidity: number;
  windSpeed: string;
  aqi: number;
  aqiCategory: 'Good' | 'Moderate' | 'Unhealthy for Sensitive' | 'Unhealthy' | 'Very Unhealthy';
  pm25: number;
  pm10: number;
  no2: number;
  o3: number;
  trafficLoad: number;
  trafficTrend: string;
  energyDemand: string;
  waterConsumption: string;
  transitCapacity: number;
  costOfLivingIndex: number | null; // null triggers honest unavailable state
  housingIndex: number | null;
  foodIndex: number | null;
  transportIndex: number | null;
  utilitiesIndex: number | null;
  officialLanguages: string[];
  spokenLanguages: { name: string; percentage: number }[];
  zones: CityZone[];
  universities: UniversityItem[];
  mobilityReportDate: string;
}

export interface UrbanAlert {
  id: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFORMATIONAL';
  title: string;
  location: string;
  zoneId?: string;
  time: string;
  signal: string;
  recommendedAction: string;
  status: 'ACTIVE' | 'MITIGATING' | 'RESOLVED';
  confidence: number;
}

export interface QuantumJob {
  id: string;
  title: string;
  targetCity: string;
  qubitsUsed: number;
  circuitDepth: number;
  iterations: number;
  status: 'COMPLETED' | 'EXECUTING' | 'QUEUED';
  energySavingPotential: string;
  executionTimeMs: number;
  coherenceRate: string;
}

export interface PredictionItem {
  id: string;
  category: 'TRAFFIC' | 'AIR QUALITY' | 'INFRASTRUCTURE RISK';
  timeHorizon: string;
  title: string;
  predictionValue: string;
  confidence: number;
  signalsUsed: string[];
  impactAssessment: string;
  mitigationAvailable: boolean;
}

export interface UrbanReport {
  id: string;
  title: string;
  date: string;
  author: string;
  department: string;
  pages: number;
  summary: string;
  status: 'PUBLISHED' | 'REAL-TIME DRAFT';
  keyFinding: string;
}

export const CITIES_DATA: Record<string, CityData> = {
  mumbai: {
    id: 'mumbai',
    name: 'Mumbai',
    country: 'India',
    countryCode: 'IN',
    population: '21,357,000',
    populationRaw: 21357000,
    density: '32,303 / km²',
    coordinates: '19.0760° N, 72.8777° E',
    temperature: 31,
    feelsLike: 36,
    humidity: 78,
    windSpeed: '14 km/h WSW',
    aqi: 158,
    aqiCategory: 'Unhealthy for Sensitive',
    pm25: 68.4,
    pm10: 122.0,
    no2: 44.2,
    o3: 28.6,
    trafficLoad: 68,
    trafficTrend: '+4.2%',
    energyDemand: '4.82 GW',
    waterConsumption: '72.4 ML/day',
    transitCapacity: 81,
    costOfLivingIndex: 34.2,
    housingIndex: 24.8,
    foodIndex: 28.4,
    transportIndex: 18.2,
    utilitiesIndex: 31.0,
    officialLanguages: ['Marathi (Official State Language - Maharashtra)'],
    spokenLanguages: [
      { name: 'Marathi', percentage: 42 },
      { name: 'Hindi', percentage: 34 },
      { name: 'Gujarati', percentage: 14 },
      { name: 'English (Professional / Enterprise)', percentage: 88 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-1',
        name: 'Indian Institute of Technology Bombay (IIT Bombay)',
        location: 'Powai, Mumbai',
        ranking: '#1 NIRF Engineering / Top 150 QS World',
        type: 'Public / Institute of National Importance',
        studentsCount: '13,500+',
        specialization: 'Artificial Intelligence, Robotics, Quantum Info, Structural Systems',
        status: 'NIRF Top 10',
        trust: 'VERIFIED'
      },
      {
        id: 'u-2',
        name: 'University of Mumbai',
        location: 'Fort & Kalina, Mumbai',
        ranking: 'Est. 1857 / State Apex Academic Body',
        type: 'State University',
        studentsCount: '540,000+ (Affiliated)',
        specialization: 'Applied Sciences, Urban Economics, Law, Humanities',
        status: 'Accredited NAAC A++',
        trust: 'VERIFIED'
      },
      {
        id: 'u-3',
        name: 'Tata Institute of Fundamental Research (TIFR)',
        location: 'Navy Nagar, Colaba',
        ranking: 'National Premier Advanced Research Institute',
        type: 'Public / Institute of National Importance',
        studentsCount: '1,200 (Doctoral/Postdoctoral)',
        specialization: 'Quantum Computing, High Energy Physics, Theoretical Computer Science',
        status: 'Autonomous Center of Excellence',
        trust: 'VERIFIED'
      },
      {
        id: 'u-4',
        name: 'Veermata Jijabai Technological Institute (VJTI)',
        location: 'Matunga, Mumbai',
        ranking: 'Est. 1887 / Top State Engineering College',
        type: 'Public / Institute of National Importance',
        studentsCount: '4,800',
        specialization: 'Civil Transportation, Electrical Grids, Autonomous Systems',
        status: 'Accredited NAAC A++',
        trust: 'VERIFIED'
      },
      {
        id: 'u-5',
        name: 'Institute of Chemical Technology (ICT Mumbai)',
        location: 'Matunga, Mumbai',
        ranking: 'Elite Deemed University / Global Chemical Eng Hub',
        type: 'Deemed University',
        studentsCount: '3,200',
        specialization: 'Green Energy Systems, Polymer Nanotech, Environmental Processing',
        status: 'NIRF Top 10',
        trust: 'VERIFIED'
      },
      {
        id: 'u-6',
        name: 'S.P. Jain Institute of Management and Research (SPJIMR)',
        location: 'Andheri West, Mumbai',
        ranking: '#1 FT Global Masters in Management in India',
        type: 'Private Autonomous',
        studentsCount: '1,100',
        specialization: 'Supply Chain Optimization, FinTech, Infrastructure Strategy',
        status: 'Autonomous Center of Excellence',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'bandra-west',
        name: 'Bandra West',
        traffic: 72,
        trafficDelta: '↑ 8.2%',
        aqi: 158,
        energyDelta: '+5.4%',
        transitLoad: 81,
        aiSignal: 'High congestion probability during upcoming peak period',
        confidence: 87,
        status: 'HIGH_RISK',
        coordinates: [36, 46],
        prediction: 'Transit load expected to surpass 88% by 18:30 on SV Road & Linking Road.',
        recommendation: 'Optimize traffic signal timing across the western mobility corridor and initiate PSO rerouting.'
      },
      {
        id: 'bkc',
        name: 'BKC (Bandra Kurla Complex)',
        traffic: 76,
        trafficDelta: '↑ 6.4%',
        aqi: 164,
        energyDelta: '+7.1%',
        transitLoad: 84,
        aiSignal: 'Financial district grid power surge & junction saturation',
        confidence: 91,
        status: 'HIGH_RISK',
        coordinates: [52, 42],
        prediction: 'Vehicular egress toward Western Express Highway will encounter 24 min average delays.',
        recommendation: 'Activate dynamic lane assignment on BKC Connector and deploy smart shuttle synchronization.'
      },
      {
        id: 'nariman-point',
        name: 'Nariman Point & Fort',
        traffic: 61,
        trafficDelta: '↓ 2.1%',
        aqi: 132,
        energyDelta: '+1.2%',
        transitLoad: 79,
        aiSignal: 'Coastal commercial corridor flow within acceptable variance',
        confidence: 84,
        status: 'NORMAL',
        coordinates: [26, 82],
        prediction: 'Evening outward migration toward Churchgate Station will peak between 18:00 - 19:15.',
        recommendation: 'Maintain current adaptive signaling; monitor pedestrian surges at Veer Nariman Rd.'
      },
      {
        id: 'andheri-east',
        name: 'Andheri East & SEEPZ',
        traffic: 79,
        trafficDelta: '↑ 10.3%',
        aqi: 172,
        energyDelta: '+6.3%',
        transitLoad: 86,
        aiSignal: 'Freight transit convergence bottleneck at Western Express Highway intersection',
        confidence: 89,
        status: 'HIGH_RISK',
        coordinates: [54, 26],
        prediction: 'Metro Line 1 interchange station will experience passenger dwell times exceeding 45 seconds.',
        recommendation: 'Inject 2 additional feeder bus circuits from MIDC hub and retime Chakala signal green cycles.'
      },
      {
        id: 'lower-parel',
        name: 'Lower Parel / Worli',
        traffic: 69,
        trafficDelta: '↑ 4.1%',
        aqi: 145,
        energyDelta: '+3.8%',
        transitLoad: 77,
        aiSignal: 'High-density commercial commercial towers peak energy demand',
        confidence: 82,
        status: 'ELEVATED',
        coordinates: [32, 64],
        prediction: 'Currey Road station overbridge density approaching 82% pedestrian capacity.',
        recommendation: 'Synchronize Senapati Bapat Marg traffic phases with Sea Link toll egress sensors.'
      },
      {
        id: 'powai',
        name: 'Powai Tech Corridor',
        traffic: 58,
        trafficDelta: '↑ 1.2%',
        aqi: 128,
        energyDelta: '+2.4%',
        transitLoad: 62,
        aiSignal: 'Institutional & technology corridor operating within nominal envelope',
        confidence: 94,
        status: 'NORMAL',
        coordinates: [70, 30],
        prediction: 'Stable flow predicted for next 4 hours; microclimate humidity elevated around Powai Lake.',
        recommendation: 'No manual intervention required; baseline environmental sensing active.'
      },
      {
        id: 'navi-mumbai',
        name: 'Navi Mumbai & Vashi',
        traffic: 52,
        trafficDelta: '↓ 4.0%',
        aqi: 118,
        energyDelta: '-0.8%',
        transitLoad: 68,
        aiSignal: 'Trans-Harbour Link (Atal Setu) transit throughput highly balanced',
        confidence: 92,
        status: 'NORMAL',
        coordinates: [80, 56],
        prediction: 'Free-flow conditions along Palm Beach road and MTHL approach spans.',
        recommendation: 'Continue variable speed corridor advisory at 80 km/h.'
      },
      {
        id: 'colaba',
        name: 'Colaba & Harbor Gateway',
        traffic: 44,
        trafficDelta: '↓ 3.2%',
        aqi: 110,
        energyDelta: '-1.2%',
        transitLoad: 58,
        aiSignal: 'Maritime coastal boundary nominal; low congestion indices',
        confidence: 95,
        status: 'NORMAL',
        coordinates: [24, 94],
        prediction: 'Ferry terminal passenger loads consistent with non-peak maritime scheduling.',
        recommendation: 'Standard sensor telemetry polling at 15-second cycles.'
      }
    ]
  },
  tokyo: {
    id: 'tokyo',
    name: 'Tokyo',
    country: 'Japan',
    countryCode: 'JP',
    population: '37,400,000',
    populationRaw: 37400000,
    density: '15,604 / km²',
    coordinates: '35.6762° N, 139.6503° E',
    temperature: 19,
    feelsLike: 19,
    humidity: 52,
    windSpeed: '11 km/h NNE',
    aqi: 28,
    aqiCategory: 'Good',
    pm25: 7.2,
    pm10: 16.4,
    no2: 18.0,
    o3: 21.2,
    trafficLoad: 44,
    trafficTrend: '-1.4%',
    energyDemand: '18.4 GW',
    waterConsumption: '142.0 ML/day',
    transitCapacity: 94,
    costOfLivingIndex: 68.4,
    housingIndex: 58.2,
    foodIndex: 62.1,
    transportIndex: 78.4,
    utilitiesIndex: 64.0,
    officialLanguages: ['Japanese (Official)'],
    spokenLanguages: [
      { name: 'Japanese', percentage: 98 },
      { name: 'English (Business)', percentage: 38 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-t1',
        name: 'University of Tokyo (Todai)',
        location: 'Hongo, Bunkyo, Tokyo',
        ranking: '#1 in Japan / Top 25 Global',
        type: 'Public / Institute of National Importance',
        studentsCount: '28,000',
        specialization: 'Quantum Mechanics, Precision Robotics, Urban Systems',
        status: 'Autonomous Center of Excellence',
        trust: 'VERIFIED'
      },
      {
        id: 'u-t2',
        name: 'Tokyo Institute of Technology (Science Tokyo)',
        location: 'Meguro, Tokyo',
        ranking: 'Top Tier Engineering',
        type: 'Public / Institute of National Importance',
        studentsCount: '10,500',
        specialization: 'Supercomputing, Clean Microgrids, High-Speed Rail AI',
        status: 'Accredited NAAC A++',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'shinjuku',
        name: 'Shinjuku Transport Hub',
        traffic: 54,
        trafficDelta: '+1.1%',
        aqi: 31,
        energyDelta: '+3.1%',
        transitLoad: 96,
        aiSignal: 'Subway terminal platform automated throughput near design threshold',
        confidence: 96,
        status: 'ELEVATED',
        coordinates: [38, 48],
        prediction: 'Platform turnstiles will handle 3.2M daily transits without failure.',
        recommendation: 'Synchronize Yamanote Line dispatch headway at 120s.'
      },
      {
        id: 'chiyoda',
        name: 'Marunouchi / Chiyoda',
        traffic: 38,
        trafficDelta: '-0.8%',
        aqi: 24,
        energyDelta: '-1.5%',
        transitLoad: 88,
        aiSignal: 'Pedestrian and EV subterranean distribution optimal',
        confidence: 98,
        status: 'NORMAL',
        coordinates: [60, 52],
        prediction: 'Zero traffic anomalies projected for next 12 hours.',
        recommendation: 'Maintain automated regenerative braking feedback.'
      }
    ]
  },
  london: {
    id: 'london',
    name: 'London',
    country: 'United Kingdom',
    countryCode: 'GB',
    population: '9,648,000',
    populationRaw: 9648000,
    density: '5,727 / km²',
    coordinates: '51.5074° N, 0.1278° W',
    temperature: 14,
    feelsLike: 13,
    humidity: 82,
    windSpeed: '22 km/h SW',
    aqi: 36,
    aqiCategory: 'Good',
    pm25: 9.8,
    pm10: 19.5,
    no2: 24.1,
    o3: 18.2,
    trafficLoad: 62,
    trafficTrend: '+2.8%',
    energyDemand: '5.92 GW',
    waterConsumption: '86.1 ML/day',
    transitCapacity: 86,
    costOfLivingIndex: 84.1,
    housingIndex: 86.4,
    foodIndex: 72.8,
    transportIndex: 94.2,
    utilitiesIndex: 88.0,
    officialLanguages: ['English (Official UK)'],
    spokenLanguages: [
      { name: 'English', percentage: 95 },
      { name: 'Multilingual Diaspora', percentage: 41 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-l1',
        name: 'Imperial College London',
        location: 'South Kensington, London',
        ranking: '#2 QS World 2026',
        type: 'Public / Institute of National Importance',
        studentsCount: '20,000',
        specialization: 'Biotech, AI Infrastructure, Quantum Photonics',
        status: 'NIRF Top 10',
        trust: 'VERIFIED'
      },
      {
        id: 'u-l2',
        name: 'University College London (UCL)',
        location: 'Bloomsbury, London',
        ranking: '#9 QS World 2026',
        type: 'Public / Institute of National Importance',
        studentsCount: '43,000',
        specialization: 'Urban Planning, Smart Cities, Health Analytics',
        status: 'Accredited NAAC A++',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'city-london',
        name: 'The Square Mile',
        traffic: 59,
        trafficDelta: '+1.8%',
        aqi: 38,
        energyDelta: '+2.0%',
        transitLoad: 89,
        aiSignal: 'Congestion charge corridor flow stable with ULEZ enforcement',
        confidence: 93,
        status: 'NORMAL',
        coordinates: [55, 45],
        prediction: 'Elizabeth line peak demand absorb 42% of central east-west traffic.',
        recommendation: 'Keep bus lane prioritization automated.'
      }
    ]
  },
  paris: {
    id: 'paris',
    name: 'Paris',
    country: 'France',
    countryCode: 'FR',
    population: '11,200,000',
    populationRaw: 11200000,
    density: '20,800 / km²',
    coordinates: '48.8566° N, 2.3522° E',
    temperature: 16,
    feelsLike: 16,
    humidity: 71,
    windSpeed: '12 km/h W',
    aqi: 42,
    aqiCategory: 'Good',
    pm25: 11.2,
    pm10: 22.4,
    no2: 26.5,
    o3: 20.1,
    trafficLoad: 58,
    trafficTrend: '-3.2%',
    energyDemand: '6.10 GW',
    waterConsumption: '78.0 ML/day',
    transitCapacity: 84,
    costOfLivingIndex: 79.5,
    housingIndex: 78.9,
    foodIndex: 74.2,
    transportIndex: 68.1,
    utilitiesIndex: 76.5,
    officialLanguages: ['French (Official)'],
    spokenLanguages: [
      { name: 'French', percentage: 96 },
      { name: 'English (Professional)', percentage: 62 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-p1',
        name: 'Sorbonne Université',
        location: '5th Arrondissement, Paris',
        ranking: 'Top Tier Continental Europe',
        type: 'Public / Institute of National Importance',
        studentsCount: '55,000',
        specialization: 'Computational Physics, Mathematics, Urban Ecology',
        status: 'NIRF Top 10',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'la-defense',
        name: 'La Défense Enterprise District',
        traffic: 64,
        trafficDelta: '-2.1%',
        aqi: 45,
        energyDelta: '+3.9%',
        transitLoad: 88,
        aiSignal: '15-minute city micro-mobility cycling lanes at 140% normal utilization',
        confidence: 91,
        status: 'NORMAL',
        coordinates: [30, 40],
        prediction: 'RER A passenger flow optimal; zero delay cascading.',
        recommendation: 'Maintain adaptive bike lane traffic light sensors.'
      }
    ]
  },
  newyork: {
    id: 'newyork',
    name: 'New York',
    country: 'United States',
    countryCode: 'US',
    population: '19,000,000',
    populationRaw: 19000000,
    density: '11,313 / km²',
    coordinates: '40.7128° N, 74.0060° W',
    temperature: 18,
    feelsLike: 17,
    humidity: 64,
    windSpeed: '18 km/h NNW',
    aqi: 48,
    aqiCategory: 'Good',
    pm25: 12.8,
    pm10: 25.1,
    no2: 29.8,
    o3: 24.0,
    trafficLoad: 71,
    trafficTrend: '+5.6%',
    energyDemand: '11.2 GW',
    waterConsumption: '124.5 ML/day',
    transitCapacity: 78,
    costOfLivingIndex: 100.0,
    housingIndex: 100.0,
    foodIndex: 100.0,
    transportIndex: 100.0,
    utilitiesIndex: 100.0,
    officialLanguages: ['English (De facto Official)'],
    spokenLanguages: [
      { name: 'English', percentage: 72 },
      { name: 'Spanish', percentage: 24 },
      { name: 'Chinese', percentage: 9 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-ny1',
        name: 'Columbia University',
        location: 'Morningside Heights, NYC',
        ranking: 'Ivy League / World Top 15',
        type: 'Private Autonomous',
        studentsCount: '31,000',
        specialization: 'Data Science Institute, Climate School, Urban Informatics',
        status: 'NIRF Top 10',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'midtown-manhattan',
        name: 'Midtown Manhattan',
        traffic: 78,
        trafficDelta: '+7.2%',
        aqi: 52,
        energyDelta: '+6.1%',
        transitLoad: 83,
        aiSignal: 'Cross-town arterial congestion peak around 42nd St & Lincoln Tunnel approach',
        confidence: 88,
        status: 'HIGH_RISK',
        coordinates: [50, 48],
        prediction: 'Bus lane throughput degraded by 18% during cross-avenue delivery hours.',
        recommendation: 'Trigger dynamic tolling tier and reroute transit via dedicated express avenues.'
      }
    ]
  },
  singapore: {
    id: 'singapore',
    name: 'Singapore',
    country: 'Singapore',
    countryCode: 'SG',
    population: '5,900,000',
    populationRaw: 5900000,
    density: '8,358 / km²',
    coordinates: '1.3521° N, 103.8198° E',
    temperature: 30,
    feelsLike: 35,
    humidity: 84,
    windSpeed: '9 km/h NE',
    aqi: 32,
    aqiCategory: 'Good',
    pm25: 8.6,
    pm10: 18.2,
    no2: 17.5,
    o3: 19.4,
    trafficLoad: 38,
    trafficTrend: '-0.9%',
    energyDemand: '7.45 GW',
    waterConsumption: '52.0 ML/day',
    transitCapacity: 95,
    costOfLivingIndex: 89.2,
    housingIndex: 91.5,
    foodIndex: 76.2,
    transportIndex: 92.4,
    utilitiesIndex: 82.0,
    officialLanguages: ['English', 'Malay', 'Mandarin', 'Tamil (All 4 Official)'],
    spokenLanguages: [
      { name: 'English', percentage: 92 },
      { name: 'Mandarin', percentage: 76 },
      { name: 'Malay', percentage: 22 },
      { name: 'Tamil', percentage: 8 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-sg1',
        name: 'National University of Singapore (NUS)',
        location: 'Kent Ridge, Singapore',
        ranking: '#8 QS World / #1 Asia',
        type: 'Public / Institute of National Importance',
        studentsCount: '32,000',
        specialization: 'Quantum Tech, Smart Nation AI, Tropical Climatology',
        status: 'NIRF Top 10',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'marina-bay',
        name: 'Marina Bay Financial Centre',
        traffic: 36,
        trafficDelta: '-1.4%',
        aqi: 29,
        energyDelta: '+1.5%',
        transitLoad: 91,
        aiSignal: 'Autonomous vehicle pilots and ERP 2.0 satellite road pricing fully synchronized',
        confidence: 97,
        status: 'NORMAL',
        coordinates: [56, 68],
        prediction: 'Zero gridlock events projected across downtown core.',
        recommendation: 'Continue automated cooling network district scheduling.'
      }
    ]
  },
  dubai: {
    id: 'dubai',
    name: 'Dubai',
    country: 'United Arab Emirates',
    countryCode: 'AE',
    population: '3,550,000',
    populationRaw: 3550000,
    density: '862 / km²',
    coordinates: '25.2048° N, 55.2708° E',
    temperature: 34,
    feelsLike: 39,
    humidity: 48,
    windSpeed: '16 km/h NNW',
    aqi: 95,
    aqiCategory: 'Moderate',
    pm25: 33.5,
    pm10: 88.0,
    no2: 32.1,
    o3: 27.5,
    trafficLoad: 51,
    trafficTrend: '+3.1%',
    energyDemand: '9.80 GW',
    waterConsumption: '98.2 ML/day',
    transitCapacity: 74,
    costOfLivingIndex: null, // DATA UNAVAILABLE state for testing data honesty!
    housingIndex: null,
    foodIndex: null,
    transportIndex: null,
    utilitiesIndex: null,
    officialLanguages: ['Arabic (Official)'],
    spokenLanguages: [
      { name: 'English (Lingua Franca)', percentage: 89 },
      { name: 'Arabic', percentage: 42 },
      { name: 'Hindi / Urdu', percentage: 38 }
    ],
    mobilityReportDate: 'October 29, 2026',
    universities: [
      {
        id: 'u-d1',
        name: 'American University in Dubai (AUD)',
        location: 'Dubai Media City',
        ranking: 'Premier Regional Institution',
        type: 'Private Autonomous',
        studentsCount: '4,000',
        specialization: 'Civil Engineering, Media Tech, Architecture',
        status: 'Autonomous Center of Excellence',
        trust: 'VERIFIED'
      }
    ],
    zones: [
      {
        id: 'downtown-dubai',
        name: 'Downtown & Sheikh Zayed Rd',
        traffic: 65,
        trafficDelta: '+4.8%',
        aqi: 98,
        energyDelta: '+8.2%',
        transitLoad: 76,
        aiSignal: 'Cooling tower thermal surge & Sheikh Zayed arterial flow',
        confidence: 89,
        status: 'ELEVATED',
        coordinates: [45, 55],
        prediction: 'District cooling peak demand sustained between 14:00 - 18:30.',
        recommendation: 'Shift non-essential district chiller storage to solar peak capacity.'
      }
    ]
  }
};

export const LIVE_PULSE_STREAMS: MetricStream[] = [
  {
    id: 'stream-1',
    category: 'TRAFFIC',
    name: 'TRAFFIC FLOW',
    currentValue: '68%',
    rawValue: 68,
    unit: 'capacity load',
    delta: '+4.2%',
    trend: 'up',
    status: 'SURGE',
    source: 'Municipal Lidar & Connected Vehicular Telemetry',
    timestamp: '14:32:08 UTC',
    sparkline: [58, 60, 63, 62, 65, 66, 68],
    trust: 'LIVE'
  },
  {
    id: 'stream-2',
    category: 'AIR QUALITY',
    name: 'AIR QUALITY',
    currentValue: 'AQI 142',
    rawValue: 142,
    unit: 'Index (PM2.5 / PM10)',
    delta: '-8.3%',
    trend: 'down',
    status: 'MODERATE',
    source: 'UrbanSense Multi-Gas Sensor Array #214',
    timestamp: '14:32:11 UTC',
    sparkline: [168, 162, 155, 150, 147, 144, 142],
    trust: 'LIVE'
  },
  {
    id: 'stream-3',
    category: 'ENERGY',
    name: 'ENERGY DEMAND',
    currentValue: '4.82 GW',
    rawValue: 4.82,
    unit: 'Gigawatts',
    delta: '+2.1%',
    trend: 'up',
    status: 'ELEVATED',
    source: 'State Transmission Grid Supervisory Control',
    timestamp: '14:32:15 UTC',
    sparkline: [4.4, 4.5, 4.6, 4.65, 4.72, 4.78, 4.82],
    trust: 'LIVE'
  },
  {
    id: 'stream-4',
    category: 'WATER',
    name: 'WATER CONSUMPTION',
    currentValue: '72.4 ML',
    rawValue: 72.4,
    unit: 'Megaliters / hr',
    delta: '+0.8%',
    trend: 'up',
    status: 'OPTIMAL',
    source: 'Bhandup Hydraulic Telemetry Pumping Station',
    timestamp: '14:32:02 UTC',
    sparkline: [70.1, 70.8, 71.2, 71.5, 71.9, 72.1, 72.4],
    trust: 'VERIFIED'
  },
  {
    id: 'stream-5',
    category: 'TRANSIT',
    name: 'TRANSIT LOAD',
    currentValue: '81%',
    rawValue: 81,
    unit: 'Metro & Suburban Railway Occupancy',
    delta: '+5.7%',
    trend: 'up',
    status: 'SURGE',
    source: 'Automated Fare Collection (AFC) Real-Time Gateway',
    timestamp: '14:32:18 UTC',
    sparkline: [68, 71, 74, 76, 78, 80, 81],
    trust: 'LIVE'
  }
];

export const MOCK_ALERTS: UrbanAlert[] = [
  {
    id: 'alt-1',
    severity: 'CRITICAL',
    title: 'Western Mobility Corridor Severe Jam Imminent',
    location: 'Bandra West (SV Road & Western Express Flyover)',
    zoneId: 'bandra-west',
    time: '3 minutes ago',
    signal: 'Traffic flow velocity dropped 22 km/h below nominal; queue length reached 1.8 km',
    recommendedAction: 'Trigger PSO signal synchronization route and divert secondary bus feeders to Linking Road.',
    status: 'ACTIVE',
    confidence: 87
  },
  {
    id: 'alt-2',
    severity: 'WARNING',
    title: 'High Particulate Matter Concentration Spike',
    location: 'Andheri East / MIDC Industrial Cluster',
    zoneId: 'andheri-east',
    time: '14 minutes ago',
    signal: 'PM2.5 surpassed 110 µg/m³ near transit interchange due to stagnant coastal sea-breeze inversion',
    recommendedAction: 'Activate urban mist cannon arrays and issue school zone active air advisory.',
    status: 'ACTIVE',
    confidence: 91
  },
  {
    id: 'alt-3',
    severity: 'WARNING',
    title: 'Commercial Substation Grid Thermal Load at 92%',
    location: 'Bandra Kurla Complex (BKC) Block G',
    zoneId: 'bkc',
    time: '28 minutes ago',
    signal: 'HVAC load in 14 banking headquarters peaking simultaneously; temperature 31°C',
    recommendedAction: 'Pre-cool district thermal energy storage to throttle peak draw.',
    status: 'MITIGATING',
    confidence: 84
  },
  {
    id: 'alt-4',
    severity: 'INFORMATIONAL',
    title: 'Metro Line 3 Phase-2 Automatic Signalling Calibration Complete',
    location: 'Colaba - BKC - SEEPZ Underground Alignment',
    zoneId: 'colaba',
    time: '1 hour ago',
    signal: 'CBTC signalling headway test achieved 90-second minimum train separation',
    recommendedAction: 'Verify operational readiness with central dispatch.',
    status: 'RESOLVED',
    confidence: 99
  }
];

export const QUANTUM_JOBS: QuantumJob[] = [
  {
    id: 'QPU-8821',
    title: 'Western Corridor 48-Node Signal Timing Optimization',
    targetCity: 'Mumbai',
    qubitsUsed: 42,
    circuitDepth: 180,
    iterations: 2400,
    status: 'COMPLETED',
    energySavingPotential: '-18.4% Idle Fuel Waste',
    executionTimeMs: 142.8,
    coherenceRate: '99.4%'
  },
  {
    id: 'QPU-8822',
    title: 'Multi-Modal Electric Bus Fleet Dynamic Dispatch',
    targetCity: 'Mumbai',
    qubitsUsed: 64,
    circuitDepth: 256,
    iterations: 4800,
    status: 'EXECUTING',
    energySavingPotential: '-12.6% Kilowatt-hour Draw',
    executionTimeMs: 89.2,
    coherenceRate: '98.9%'
  },
  {
    id: 'QPU-8823',
    title: 'Micro-Grid Distributed Battery Discharge Annealing',
    targetCity: 'Tokyo',
    qubitsUsed: 108,
    circuitDepth: 512,
    iterations: 9600,
    status: 'QUEUED',
    energySavingPotential: '-24.1% Peak Grid Surge',
    executionTimeMs: 0,
    coherenceRate: 'Standby'
  }
];

export const PREDICTIONS_DATA: PredictionItem[] = [
  {
    id: 'pred-1',
    category: 'TRAFFIC',
    timeHorizon: 'Next Peak Period (17:30 - 19:30)',
    title: 'Western Express Highway Congestion Bottleneck',
    predictionValue: '86% Congestion Probability (Expected delay +28 min)',
    confidence: 87,
    signalsUsed: ['Real-time vehicular GPS velocities', 'Historical rainfall/tide correlation', 'Metro Line 1 dwell times'],
    impactAssessment: 'High probability of severe queueing affecting 42,000 commuters unless signal timing is dynamically compensated.',
    mitigationAvailable: true
  },
  {
    id: 'pred-2',
    category: 'AIR QUALITY',
    timeHorizon: 'Next 6 Hours (Until 20:30)',
    title: 'Thermal Inversion Particulate Trapping',
    predictionValue: 'Expected AQI 174 ± 8 (Unhealthy Threshold)',
    confidence: 82,
    signalsUsed: ['Doppler wind profiler speeds', 'Boundary layer lidar', 'Industrial sensor streams'],
    impactAssessment: 'Low wind dispersion will concentrate surface vehicle exhausts along valley-shaped corridors.',
    mitigationAvailable: true
  },
  {
    id: 'pred-3',
    category: 'INFRASTRUCTURE RISK',
    timeHorizon: 'Next 24 Hours',
    title: 'Stormwater Culvert Capacity Stress Index',
    predictionValue: 'Low Risk (Nominal 34% capacity)',
    confidence: 94,
    signalsUsed: ['Tidal gauge forecasts', 'Reservoir level sensors', 'Drainage ultrasonic level sensors'],
    impactAssessment: 'High tide of 4.1m coincides with low precipitation probability; flood gates operating in standard cycle.',
    mitigationAvailable: false
  }
];

export const URBAN_REPORTS: UrbanReport[] = [
  {
    id: 'rep-1',
    title: 'Mumbai Metropolitan Mobility & Traffic Optimization Audit',
    date: 'October 29, 2026',
    author: 'UrbanLens Spatial AI Engine v4.2',
    department: 'Directorate of Urban Mobility & Transit Automation',
    pages: 28,
    summary: 'Comprehensive analysis of vehicular flow across 8 key municipal zones with PSO signal coordination outcomes.',
    status: 'PUBLISHED',
    keyFinding: 'Dynamic PSO signal timing across Western Corridor reduces average intersection idling by 21.4%.'
  },
  {
    id: 'rep-2',
    title: 'Coastal Atmospheric Dispersion & Particulate Vector Analysis',
    date: 'October 27, 2026',
    author: 'Environmental Sensor Telemetry Hub',
    department: 'Pollution Control & Public Health Division',
    pages: 19,
    summary: 'Evaluating diurnal particulate matter shifts influenced by Arabian Sea coastal winds.',
    status: 'PUBLISHED',
    keyFinding: 'Morning sea-breeze transition at 10:15 creates a 35-minute stagnation window over Andheri MIDC.'
  },
  {
    id: 'rep-3',
    title: 'Comparative Urban Intelligence: Mumbai vs Tokyo Spatial Efficiency',
    date: 'October 24, 2026',
    author: 'Global Urban Analytics Working Group',
    department: 'Smart Cities Joint Strategic Command',
    pages: 34,
    summary: 'Cross-metropolitan benchmarking across transit capacity, power grid resilience, and public education density.',
    status: 'PUBLISHED',
    keyFinding: 'Tokyo achieves 94% transit utilization through automated CBTC dispatch headways of 120s.'
  }
];

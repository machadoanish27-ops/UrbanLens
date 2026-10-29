import React, { useState } from 'react';
import {
  Coins,
  ArrowRightLeft,
  RefreshCw,
  TrendingUp,
  MapPin,
  Clock,
} from 'lucide-react';
import { useOriginDestination } from '../context/OriginDestinationContext';
import { useCurrencyConversion } from '../hooks/useUrbanLens';

export const CurrencyWidget: React.FC = () => {
  const { origin, destination, openOriginModal } = useOriginDestination();
  const [isOpen, setIsOpen] = useState(false);
  const [amountStr, setAmountStr] = useState('1000');

  // If no destination is set (e.g. on home page), use USD or JPY as destination preview
  const baseCurrency = origin.currency_code || 'INR';
  const quoteCurrency = destination?.currency_code || (baseCurrency === 'USD' ? 'EUR' : 'USD');

  const parsedAmount = parseFloat(amountStr) || 1.0;

  const {
    data: conversionData,
    isLoading,
    isRefetching,
    refetch,
    isError,
  } = useCurrencyConversion(baseCurrency, quoteCurrency, parsedAmount);

  const data = conversionData?.data;
  const rate = data?.rate;
  const inverseRate = data?.inverse_rate;
  const convertedAmount = data?.converted_amount;
  const status = data?.status || (isError ? 'unavailable' : 'fresh');
  const provider = data?.provider || 'Frankfurter';
  const observedAt = data?.observed_at || data?.last_updated;

  const isLive = status === 'fresh';
  const isCached = status === 'cached';

  return (
    <div className="relative">
      {/* Compact Pill in Navbar */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs text-slate-200 transition-all shadow-sm"
        title="Live Currency Exchange Rate & USD Benchmarks"
      >
        <Coins className="w-3.5 h-3.5 text-amber-400" />
        <span className="font-semibold text-white">
          {baseCurrency} {origin.currency_symbol} ↔ {quoteCurrency} {destination?.currency_symbol || '$'}
        </span>

        {rate !== undefined && rate !== null ? (
          <span className="font-mono text-indigo-300 font-medium">
            1 = {rate < 1 ? rate.toFixed(4) : rate.toFixed(2)}
          </span>
        ) : (
          <span className="text-slate-400">...</span>
        )}

        {/* Live Status indicator */}
        <span
          className={`w-2 h-2 rounded-full ${
            isLive
              ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]'
              : isCached
              ? 'bg-amber-400'
              : 'bg-slate-500'
          }`}
        />
      </button>

      {/* Expanded Currency Popover */}
      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 mt-2 w-84 sm:w-96 glass-panel p-5 rounded-2xl border border-slate-700/80 shadow-2xl bg-slate-900/98 z-50 animate-in fade-in zoom-in-95 duration-150">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Coins className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                  Live Currency Exchange
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${
                    isLive
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : isCached
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}
                >
                  {isLive ? 'Live' : isCached ? 'Cached' : 'Unavailable'}
                </span>
                <button
                  onClick={() => refetch()}
                  disabled={isRefetching}
                  className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors disabled:opacity-50"
                  title="Refresh rates"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin text-indigo-400' : ''}`} />
                </button>
              </div>
            </div>

            {/* Relocation Route Context */}
            <div className="my-3 p-2.5 rounded-xl bg-slate-950/60 border border-slate-800 text-xs space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Origin (From)</span>
                <button
                  onClick={() => {
                    setIsOpen(false);
                    openOriginModal();
                  }}
                  className="text-[10px] text-indigo-400 hover:underline flex items-center gap-1 font-medium"
                >
                  Change Origin
                </button>
              </div>
              <div className="font-semibold text-white flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                  {origin.city_name}, {origin.country_name}
                </span>
                <span className="font-mono text-indigo-300">
                  {baseCurrency} ({origin.currency_symbol})
                </span>
              </div>

              <div className="pt-1.5 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-[10px] uppercase font-semibold text-slate-400">Destination (To)</span>
                <span className="font-semibold text-white">
                  {destination ? `${destination.city_name}, ${destination.country_name || destination.country_iso2}` : 'Benchmark Preview'}
                </span>
              </div>
            </div>

            {/* Quick Interactive Converter Input */}
            <div className="space-y-2 mb-3">
              <label className="text-[11px] font-medium text-slate-300 flex items-center justify-between">
                <span>Quick Budget Conversion</span>
                <span className="text-[10px] text-slate-500 font-mono">Amount entry</span>
              </label>
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <span className="absolute left-2.5 top-2 text-xs font-bold text-indigo-400 font-mono">
                    {origin.currency_symbol}
                  </span>
                  <input
                    type="number"
                    value={amountStr}
                    onChange={(e) => setAmountStr(e.target.value)}
                    className="w-full pl-7 pr-2 py-1.5 text-xs font-mono rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                    placeholder="1000"
                    min="1"
                  />
                </div>
                <ArrowRightLeft className="w-4 h-4 text-slate-500 shrink-0" />
                <div className="flex-1 px-3 py-1.5 text-xs font-mono rounded-lg bg-slate-950/80 border border-slate-800 text-emerald-400 font-bold truncate">
                  {isLoading ? (
                    'Converting...'
                  ) : convertedAmount !== undefined && convertedAmount !== null ? (
                    `${destination?.currency_symbol || ''} ${convertedAmount.toLocaleString(undefined, {
                      maximumFractionDigits: 2,
                    })}`
                  ) : (
                    'Unavailable'
                  )}
                </div>
              </div>
            </div>

            {/* Direct & Inverse Conversion Rates */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/90 text-xs space-y-2 font-mono">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">1 {baseCurrency} =</span>
                <span className="text-white font-bold">
                  {rate !== undefined && rate !== null ? `${rate} ${quoteCurrency}` : 'Rate Unavailable'}
                </span>
              </div>
              <div className="flex items-center justify-between pt-1 border-t border-slate-900 text-slate-400">
                <span>1 {quoteCurrency} =</span>
                <span className="text-indigo-300">
                  {inverseRate !== undefined && inverseRate !== null ? `${inverseRate} ${baseCurrency}` : 'N/A'}
                </span>
              </div>
            </div>

            {/* USD Relative Benchmarks (Explicitly NOT highest currency) */}
            <div className="mt-3 p-2.5 rounded-xl bg-slate-950/50 border border-slate-800/60 text-[11px] space-y-1.5">
              <div className="flex items-center gap-1.5 text-slate-400 font-medium">
                <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-300">
                  Relative USD Benchmarks
                </span>
              </div>
              <p className="text-[10px] text-slate-500 leading-tight">
                Global reference benchmarks (measured against United States Dollar):
              </p>
              <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">1 {baseCurrency}: </span>
                  <span className="text-cyan-300 font-semibold">
                    ${data?.usd_benchmark_base?.rate_to_usd ?? 'N/A'}
                  </span>
                </div>
                <div className="p-1.5 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">1 {quoteCurrency}: </span>
                  <span className="text-cyan-300 font-semibold">
                    ${data?.usd_benchmark_quote?.rate_to_usd ?? 'N/A'}
                  </span>
                </div>
              </div>
            </div>

            {/* Provenance & Timestamp Footer */}
            <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" />
                {observedAt ? `Observed: ${observedAt}` : 'Live feed'}
              </span>
              <span className="font-medium text-slate-400">Provider: {provider}</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

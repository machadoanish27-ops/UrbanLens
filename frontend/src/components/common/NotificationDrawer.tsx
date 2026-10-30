import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useUrban } from '../../context/UrbanContext';
import {
  Bell,
  X,
  AlertTriangle,
  CheckCircle2,
  Info,
  ArrowRight
} from 'lucide-react';

export const NotificationDrawer: React.FC = () => {
  const {
    isNotificationsOpen,
    toggleNotifications,
    notifications,
    dismissNotification
  } = useUrban();

  const navigate = useNavigate();

  if (!isNotificationsOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-end pt-16 pr-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={() => toggleNotifications(false)}
    >
      <div
        className="w-full max-w-sm bg-[#0B1726] border border-[#1E334A] rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-[#1E334A] flex items-center justify-between bg-[#07111F]">
          <div className="flex items-center gap-2">
            <Bell className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
              SYSTEM NOTIFICATIONS ({notifications.length})
            </h3>
          </div>
          <button
            onClick={() => toggleNotifications(false)}
            aria-label="Close notifications"
            className="text-slate-400 hover:text-white p-1 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto divide-y divide-[#1E334A]/50 p-2">
          {notifications.length === 0 ? (
            <div className="p-6 text-center text-xs font-mono text-slate-400">
              No unread notifications. All telemetry systems operational.
            </div>
          ) : (
            notifications.map((item) => {
              const isWarning = item.type === 'WARNING';
              const isSuccess = item.type === 'SUCCESS';
              const isCritical = item.type === 'CRITICAL';

              return (
                <div key={item.id} className="p-3 hover:bg-[#07111F] rounded-xl transition-colors group relative">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      {isCritical && <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                      {isWarning && <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />}
                      {isSuccess && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                      {!isCritical && !isWarning && !isSuccess && <Info className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                      <span className="text-xs font-semibold text-white font-mono">{item.title}</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono shrink-0">{item.timestamp}</span>
                  </div>
                  <p className="text-[11px] text-slate-300 mt-1 leading-relaxed font-sans">
                    {item.message}
                  </p>
                  <div className="flex items-center justify-between mt-2 pt-1 border-t border-[#1E334A]/40 text-[10px] font-mono">
                    <button
                      onClick={() => dismissNotification(item.id)}
                      className="text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      Dismiss
                    </button>
                    <button
                      onClick={() => {
                        toggleNotifications(false);
                        navigate('/app/weather');
                      }}
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                    >
                      <span>Inspect Telemetry</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

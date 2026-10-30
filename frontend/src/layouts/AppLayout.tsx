import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/common/Sidebar';
import { GlobalTopBar } from '../components/common/GlobalTopBar';
import { LivePulseTicker } from '../components/common/LivePulseTicker';
import { AiDrawer } from '../components/common/AiDrawer';
import { CommandPalette } from '../components/common/CommandPalette';
import { NotificationDrawer } from '../components/common/NotificationDrawer';
import { OriginSelectorModal } from '../components/OriginSelectorModal';

export const AppLayout: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#030712] text-[#F8FAFC] flex overflow-x-hidden font-sans">
      {/* Desktop Collapsible Sidebar */}
      <div className="hidden md:block shrink-0">
        <Sidebar
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />
      </div>

      {/* Mobile Drawer Sidebar */}
      {isMobileSidebarOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm md:hidden animate-in fade-in"
          onClick={() => setIsMobileSidebarOpen(false)}
        >
          <div
            className="w-72 h-full bg-[#07111F]"
            onClick={(e) => e.stopPropagation()}
          >
            <Sidebar
              isCollapsed={false}
              onToggleCollapse={() => setIsMobileSidebarOpen(false)}
              onCloseMobile={() => setIsMobileSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Main Operational Viewport Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <GlobalTopBar onToggleSidebar={() => setIsMobileSidebarOpen(!isMobileSidebarOpen)} />
        <LivePulseTicker />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1700px] w-full mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Global Interactive Overlays */}
      <AiDrawer />
      <CommandPalette />
      <NotificationDrawer />
      <OriginSelectorModal />
    </div>
  );
};

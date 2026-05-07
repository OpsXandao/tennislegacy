import { Outlet, Link, useLocation } from 'react-router';
import { Home, User, Calendar, Trophy, ShoppingBag } from 'lucide-react';

export default function Root() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/player', icon: User, label: 'Player' },
    { path: '/calendar', icon: Calendar, label: 'Calendar' },
    { path: '/rankings', icon: Trophy, label: 'Rankings' },
    { path: '/market', icon: ShoppingBag, label: 'Market' },
  ];
  
  return (
    <div className="min-h-screen bg-bg-main relative overflow-hidden">
      {/* Mobile Container - 390x844px */}
      <div className="mx-auto max-w-[390px] min-h-screen relative">
        {/* Main Content */}
        <div className="pb-20">
          <Outlet />
        </div>
        
        {/* Bottom Navigation Dock */}
        <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[390px] h-20 bg-bg-card border-t-2 border-neon-green z-50"
             style={{ boxShadow: '0 -4px 20px rgba(0, 255, 136, 0.3)' }}>
          <div className="flex items-center justify-around h-full px-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="flex flex-col items-center gap-1 relative group"
                >
                  <div className={`p-2 transition-all ${
                    isActive 
                      ? 'text-neon-green' 
                      : 'text-muted-gray hover:text-neon-cyan'
                  }`}
                  style={isActive ? { 
                    filter: 'drop-shadow(0 0 8px rgba(0, 255, 136, 0.8))'
                  } : {}}>
                    <Icon 
                      size={24} 
                      strokeWidth={2}
                    />
                  </div>
                  <span 
                    className={`text-[8px] font-mono uppercase tracking-wider ${
                      isActive ? 'text-neon-green' : 'text-muted-gray'
                    }`}
                  >
                    {item.label}
                  </span>
                  {isActive && (
                    <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-1 h-1 bg-neon-green rounded-full animate-pulse" 
                         style={{ boxShadow: '0 0 8px rgba(0, 255, 136, 0.8)' }} />
                  )}
                </Link>
              );
            })}
          </div>
        </nav>
      </div>
    </div>
  );
}

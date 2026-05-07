import { motion } from 'motion/react';
import { MapPin, Trophy, Star, Award } from 'lucide-react';

export default function SeasonCalendar() {
  const tournaments = [
    {
      name: 'AUSTRALIAN OPEN',
      city: 'Melbourne',
      tier: 'grandslam',
      surface: 'hard',
      prize: '$2.5M',
      status: 'completed',
      result: 'CHAMPION',
      position: { left: '85%', top: '75%' },
    },
    {
      name: 'INDIAN WELLS',
      city: 'California',
      tier: 'masters',
      surface: 'hard',
      prize: '$1.2M',
      status: 'completed',
      result: 'RUNNER-UP',
      position: { left: '15%', top: '35%' },
    },
    {
      name: 'ROLAND GARROS',
      city: 'Paris',
      tier: 'grandslam',
      surface: 'clay',
      prize: '$2.5M',
      status: 'active',
      result: null,
      position: { left: '48%', top: '30%' },
    },
    {
      name: 'WIMBLEDON',
      city: 'London',
      tier: 'grandslam',
      surface: 'grass',
      prize: '$2.5M',
      status: 'upcoming',
      result: null,
      position: { left: '47%', top: '28%' },
    },
    {
      name: 'SHANGHAI MASTERS',
      city: 'Shanghai',
      tier: 'masters',
      surface: 'hard',
      prize: '$1.2M',
      status: 'upcoming',
      result: null,
      position: { left: '78%', top: '38%' },
    },
    {
      name: 'ROME MASTERS',
      city: 'Rome',
      tier: 'masters',
      surface: 'clay',
      prize: '$1.2M',
      status: 'upcoming',
      result: null,
      position: { left: '50%', top: '35%' },
    },
  ];

  const tierConfig = {
    grandslam: {
      icon: Trophy,
      color: '#ffe600',
      glow: 'var(--glow-gold)',
      label: 'GRAND SLAM',
      badge: '👑',
    },
    masters: {
      icon: Star,
      color: '#c0c0c0',
      glow: '0 0 10px rgba(192, 192, 192, 0.5)',
      label: 'MASTERS 1000',
      badge: '⭐',
    },
    atp250: {
      icon: Award,
      color: '#cd7f32',
      glow: '0 0 10px rgba(205, 127, 50, 0.5)',
      label: 'ATP 250',
      badge: '🎾',
    },
  };

  const surfacePatterns = {
    hard: 'bg-blue-900',
    clay: 'bg-red-900',
    grass: 'bg-green-900',
  };

  const surfaceTextures = {
    hard: 'linear-gradient(45deg, #1e3a8a 25%, transparent 25%, transparent 75%, #1e3a8a 75%), linear-gradient(45deg, #1e3a8a 25%, transparent 25%, transparent 75%, #1e3a8a 75%)',
    clay: 'repeating-linear-gradient(90deg, #7f1d1d 0px, #991b1b 2px, #7f1d1d 4px)',
    grass: 'repeating-linear-gradient(0deg, #14532d 0px, #166534 1px, #14532d 2px)',
  };

  return (
    <div className="min-h-screen bg-bg-main p-4 pt-6 font-mono pb-24">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-neon-gold text-[10px] tracking-[0.3em] mb-2"
            style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-gold)' }}>
          WORLD TOUR
        </h1>
        <div className="text-[8px] text-neon-cyan">SEASON 2026 • WEEK 12</div>
      </div>

      {/* World Map */}
      <div className="bg-bg-card border-2 border-neon-green p-4 mb-6 relative overflow-hidden"
           style={{ boxShadow: 'var(--glow-green)' }}>
        <div className="text-center text-[8px] text-neon-green mb-3 tracking-widest"
             style={{ fontFamily: 'var(--font-arcade)' }}>
          TOURNAMENT MAP
        </div>

        {/* Simplified World Map */}
        <div className="relative h-48 bg-black border-2 border-neon-cyan overflow-hidden"
             style={{ 
               backgroundImage: 'radial-gradient(circle at 50% 50%, #1a1a2e 0%, #0a0a0a 100%)',
             }}>
          {/* Grid Lines */}
          <div className="absolute inset-0">
            {[...Array(8)].map((_, i) => (
              <div 
                key={`h-${i}`}
                className="absolute w-full h-px bg-neon-cyan opacity-20"
                style={{ top: `${(i + 1) * 12.5}%` }}
              />
            ))}
            {[...Array(10)].map((_, i) => (
              <div 
                key={`v-${i}`}
                className="absolute h-full w-px bg-neon-cyan opacity-20"
                style={{ left: `${(i + 1) * 10}%` }}
              />
            ))}
          </div>

          {/* Continents (Simplified Shapes) */}
          <svg className="absolute inset-0 w-full h-full opacity-30" viewBox="0 0 100 100" preserveAspectRatio="none">
            {/* Europe */}
            <path d="M 45 25 L 55 25 L 58 35 L 50 38 L 45 35 Z" fill="#00ff88" opacity="0.3" />
            {/* North America */}
            <path d="M 10 20 L 25 20 L 28 40 L 15 45 L 10 35 Z" fill="#00ff88" opacity="0.3" />
            {/* Asia */}
            <path d="M 70 25 L 90 25 L 92 50 L 75 48 L 70 35 Z" fill="#00ff88" opacity="0.3" />
            {/* Australia */}
            <path d="M 80 70 L 90 70 L 92 80 L 85 82 L 80 78 Z" fill="#00ff88" opacity="0.3" />
          </svg>

          {/* Tournament Pins */}
          {tournaments.map((tournament, i) => (
            <motion.div
              key={i}
              className="absolute"
              style={tournament.position}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.2, type: 'spring' }}
            >
              {tournament.status === 'active' ? (
                <motion.div
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  <MapPin 
                    size={20} 
                    className="text-neon-gold -translate-x-1/2 -translate-y-full"
                    fill="#ffe600"
                    style={{ 
                      filter: 'drop-shadow(0 0 10px rgba(255, 230, 0, 0.8))',
                    }}
                  />
                </motion.div>
              ) : (
                <MapPin 
                  size={16} 
                  className={`-translate-x-1/2 -translate-y-full ${
                    tournament.status === 'completed' ? 'text-muted-gray' : 'text-neon-cyan'
                  }`}
                  style={tournament.status === 'upcoming' ? { 
                    filter: 'drop-shadow(0 0 5px rgba(0, 229, 255, 0.5))'
                  } : {}}
                />
              )}
            </motion.div>
          ))}

          {/* Connecting Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {tournaments.slice(0, -1).map((tournament, i) => {
              const next = tournaments[i + 1];
              return (
                <motion.line
                  key={i}
                  x1={tournament.position.left}
                  y1={tournament.position.top}
                  x2={next.position.left}
                  y2={next.position.top}
                  stroke="#00e5ff"
                  strokeWidth="1"
                  strokeDasharray="4 4"
                  opacity="0.3"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ delay: i * 0.3, duration: 0.5 }}
                />
              );
            })}
          </svg>
        </div>

        <div className="mt-3 text-[8px] text-neon-cyan text-center">
          ▲ = ACTIVE • ○ = UPCOMING • ● = COMPLETED
        </div>
      </div>

      {/* Tournament Cards */}
      <div className="space-y-4">
        {tournaments.map((tournament, i) => {
          const config = tierConfig[tournament.tier];
          const Icon = config.icon;

          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-bg-card border-2 overflow-hidden relative"
              style={{ 
                borderColor: config.color,
                boxShadow: config.glow,
              }}
            >
              {/* Surface Pattern Background */}
              <div 
                className="absolute inset-0 opacity-20"
                style={{ 
                  background: surfaceTextures[tournament.surface],
                  backgroundSize: '8px 8px',
                  backgroundPosition: '0 0, 4px 4px',
                }}
              />

              <div className="relative p-4">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Icon size={12} style={{ color: config.color }} />
                      <span className="text-[8px] text-muted-gray">{config.label}</span>
                      <span className="text-sm">{config.badge}</span>
                    </div>
                    <h3 
                      className="text-[11px] mb-1"
                      style={{ 
                        fontFamily: 'var(--font-arcade)',
                        color: config.color,
                      }}
                    >
                      {tournament.name}
                    </h3>
                    <div className="text-[9px] text-neon-cyan">{tournament.city}</div>
                  </div>

                  {/* Status Badge */}
                  <div 
                    className={`px-2 py-1 text-[7px] border ${
                      tournament.status === 'active' 
                        ? 'border-neon-gold text-neon-gold animate-pulse'
                        : tournament.status === 'completed'
                        ? 'border-muted-gray text-muted-gray'
                        : 'border-neon-cyan text-neon-cyan'
                    }`}
                    style={tournament.status === 'active' ? { boxShadow: 'var(--glow-gold)' } : {}}
                  >
                    {tournament.status.toUpperCase()}
                  </div>
                </div>

                {/* Tournament Info */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    {/* Surface Indicator */}
                    <div className="flex items-center gap-1">
                      <div 
                        className={`w-8 h-8 border-2 ${surfacePatterns[tournament.surface]}`}
                        style={{ 
                          borderColor: config.color,
                          background: surfaceTextures[tournament.surface],
                          backgroundSize: '4px 4px',
                        }}
                      />
                      <span className="text-[8px] text-muted-gray uppercase">{tournament.surface}</span>
                    </div>
                  </div>

                  {/* Prize Money */}
                  <div className="text-right">
                    <div className="text-[8px] text-muted-gray">PRIZE</div>
                    <div className="text-neon-gold text-sm font-bold"
                         style={{ fontFamily: 'var(--font-arcade)' }}>
                      {tournament.prize}
                    </div>
                  </div>
                </div>

                {/* Result / Action */}
                {tournament.result ? (
                  <div 
                    className={`w-full py-2 text-center text-[9px] border-2 ${
                      tournament.result === 'CHAMPION'
                        ? 'bg-neon-gold text-black border-neon-gold'
                        : 'bg-black text-neon-cyan border-neon-cyan'
                    }`}
                    style={{ fontFamily: 'var(--font-arcade)' }}
                  >
                    {tournament.result}
                  </div>
                ) : tournament.status === 'active' ? (
                  <button 
                    className="w-full bg-black border-2 border-neon-gold text-neon-gold py-2 text-[9px] hover:bg-neon-gold hover:text-black transition-all"
                    style={{ fontFamily: 'var(--font-arcade)', boxShadow: 'var(--glow-gold)' }}
                  >
                    PLAY MATCH
                  </button>
                ) : (
                  <button 
                    className="w-full bg-black border-2 border-muted-gray text-muted-gray py-2 text-[9px]"
                    style={{ fontFamily: 'var(--font-arcade)' }}
                    disabled
                  >
                    LOCKED
                  </button>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

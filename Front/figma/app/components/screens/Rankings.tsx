import { motion } from 'motion/react';
import { Trophy, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function Rankings() {
  const players = [
    { rank: 1, name: 'N. DJOKOVIC', country: '🇷🇸', points: 9850, change: 0, highlight: false },
    { rank: 2, name: 'C. ALCARAZ', country: '🇪🇸', points: 9420, change: 1, highlight: false },
    { rank: 3, name: 'J. SINNER', country: '🇮🇹', points: 8950, change: -1, highlight: false },
    { rank: 4, name: 'D. MEDVEDEV', country: '🇷🇺', points: 8100, change: 0, highlight: false },
    { rank: 5, name: 'YOU', country: '🎾', points: 7850, change: 2, highlight: true },
    { rank: 6, name: 'S. TSITSIPAS', country: '🇬🇷', points: 7420, change: -1, highlight: false },
    { rank: 7, name: 'A. RUBLEV', country: '🇷🇺', points: 7100, change: -1, highlight: false },
    { rank: 8, name: 'H. RUNE', country: '🇩🇰', points: 6850, change: 1, highlight: false },
    { rank: 9, name: 'T. FRITZ', country: '🇺🇸', points: 6420, change: -1, highlight: false },
    { rank: 10, name: 'F. AUGER', country: '🇨🇦', points: 6200, change: 0, highlight: false },
  ];

  const stats = [
    { label: 'BEST RANKING', value: '#3', color: 'neon-gold' },
    { label: 'TITLES WON', value: '8', color: 'neon-green' },
    { label: 'WIN RATE', value: '72%', color: 'neon-cyan' },
    { label: 'GRAND SLAMS', value: '1', color: 'neon-gold' },
  ];

  return (
    <div className="min-h-screen bg-bg-main p-4 pt-6 font-mono pb-24">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-neon-gold text-[10px] tracking-[0.3em] mb-2"
            style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-gold)' }}>
          ATP RANKINGS
        </h1>
        <div className="flex items-center gap-2">
          <Trophy size={16} className="text-neon-gold animate-pulse" />
          <span className="text-[8px] text-neon-cyan">LIVE • UPDATED 07 MAR 2026</span>
        </div>
      </div>

      {/* Your Stats Overview */}
      <div className="bg-bg-card border-2 border-neon-green p-4 mb-6"
           style={{ boxShadow: 'var(--glow-green)' }}>
        <div className="text-neon-green text-[10px] mb-4 tracking-wider"
             style={{ fontFamily: 'var(--font-arcade)' }}>
          YOUR CAREER STATS
        </div>

        <div className="grid grid-cols-2 gap-3">
          {stats.map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="bg-black border-2 border-neon-cyan p-3 text-center"
            >
              <div className="text-[8px] text-muted-gray mb-1">{stat.label}</div>
              <div className={`text-${stat.color} text-2xl font-bold`}
                   style={{ fontFamily: 'var(--font-arcade)' }}>
                {stat.value}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Leaderboard Header */}
      <div className="bg-bg-card border-2 border-neon-gold p-3 mb-4"
           style={{ boxShadow: 'var(--glow-gold)' }}>
        <div className="flex justify-between text-[8px] text-neon-gold">
          <span className="w-10">RANK</span>
          <span className="flex-1">PLAYER</span>
          <span className="w-16 text-right">POINTS</span>
          <span className="w-10 text-center">CHG</span>
        </div>
      </div>

      {/* Rankings List */}
      <div className="space-y-2">
        {players.map((player, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className={`p-3 border-2 relative overflow-hidden ${
              player.highlight
                ? 'bg-neon-green/20 border-neon-green'
                : 'bg-bg-card border-neon-cyan/30'
            }`}
            style={player.highlight ? { 
              boxShadow: 'var(--glow-green)',
            } : {}}
          >
            {/* Highlight Indicator */}
            {player.highlight && (
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-neon-green animate-pulse" />
            )}

            <div className="flex items-center justify-between">
              {/* Rank */}
              <div 
                className={`w-10 text-center ${
                  player.rank <= 3 ? 'text-neon-gold' : player.highlight ? 'text-neon-green' : 'text-neon-cyan'
                }`}
              >
                <span className="text-xl font-bold" style={{ fontFamily: 'var(--font-arcade)' }}>
                  {player.rank}
                </span>
                {player.rank === 1 && (
                  <Trophy size={12} className="inline ml-1 text-neon-gold animate-pulse" />
                )}
              </div>

              {/* Player Info */}
              <div className="flex-1 flex items-center gap-2">
                <span className="text-2xl">{player.country}</span>
                <div>
                  <div className={`text-[11px] ${
                    player.highlight ? 'text-neon-green' : 'text-neon-cyan'
                  }`}
                  style={{ fontFamily: 'var(--font-arcade)' }}>
                    {player.name}
                  </div>
                  {player.highlight && (
                    <div className="text-[7px] text-neon-gold">★ YOU ★</div>
                  )}
                </div>
              </div>

              {/* Points */}
              <div className="w-16 text-right">
                <div className={`text-sm font-bold ${
                  player.highlight ? 'text-neon-green' : 'text-white'
                }`}>
                  {player.points.toLocaleString()}
                </div>
                <div className="text-[7px] text-muted-gray">PTS</div>
              </div>

              {/* Change Indicator */}
              <div className="w-10 flex justify-center">
                {player.change > 0 ? (
                  <div className="flex items-center gap-1 text-neon-green">
                    <TrendingUp size={12} />
                    <span className="text-[9px]">+{player.change}</span>
                  </div>
                ) : player.change < 0 ? (
                  <div className="flex items-center gap-1 text-neon-red">
                    <TrendingDown size={12} />
                    <span className="text-[9px]">{player.change}</span>
                  </div>
                ) : (
                  <Minus size={12} className="text-muted-gray" />
                )}
              </div>
            </div>

            {/* Rank Boundary Indicators */}
            {player.rank === 4 && (
              <div className="absolute bottom-0 left-0 right-0 h-px bg-neon-gold opacity-50" />
            )}
            {player.rank === 8 && (
              <div className="absolute bottom-0 left-0 right-0 h-px bg-neon-cyan opacity-30" />
            )}
          </motion.div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-6 bg-black border-2 border-muted-gray p-4">
        <div className="text-[8px] text-muted-gray mb-2 tracking-wider"
             style={{ fontFamily: 'var(--font-arcade)' }}>
          RANKINGS INFO
        </div>
        <div className="space-y-1 text-[8px]">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 border-2 border-neon-gold" />
            <span className="text-muted-gray">TOP 4 = GRAND SLAM SEEDS</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 border-2 border-neon-cyan" />
            <span className="text-muted-gray">TOP 8 = YEAR-END FINALS</span>
          </div>
          <div className="flex items-center gap-2">
            <TrendingUp size={10} className="text-neon-green" />
            <span className="text-muted-gray">RANKING IMPROVED</span>
          </div>
        </div>
      </div>
    </div>
  );
}

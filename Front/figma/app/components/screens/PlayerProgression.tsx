import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { TrendingUp, Award } from 'lucide-react';

export default function PlayerProgression() {
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [level, setLevel] = useState(32);
  const [xp, setXp] = useState(7850);
  const [xpToNext] = useState(10000);

  const stats = [
    { attribute: 'SPEED', current: 85, base: 70, fullMark: 100 },
    { attribute: 'POWER', current: 78, base: 65, fullMark: 100 },
    { attribute: 'MENTAL', current: 92, base: 80, fullMark: 100 },
    { attribute: 'RESIST', current: 70, base: 60, fullMark: 100 },
    { attribute: 'SERVE', current: 88, base: 75, fullMark: 100 },
    { attribute: 'TECH', current: 82, base: 70, fullMark: 100 },
  ];

  const equipment = [
    { slot: 'RACKET', name: 'WILSON BLADE v8', rarity: 'legendary', power: '+15 PWR' },
    { slot: 'STRING', name: 'LUXILON ALU', rarity: 'rare', power: '+8 CTRL' },
    { slot: 'SHOES', name: 'NIKE ZOOM', rarity: 'rare', power: '+12 SPD' },
    { slot: 'OUTFIT', name: 'RF PRO KIT', rarity: 'common', power: '+5 MNT' },
  ];

  const rarityColors = {
    common: '#9ca3af',
    rare: '#00e5ff',
    legendary: '#ffe600',
  };

  const rarityGlow = {
    common: '0 0 5px rgba(156, 163, 175, 0.3)',
    rare: '0 0 10px rgba(0, 229, 255, 0.5)',
    legendary: '0 0 15px rgba(255, 230, 0, 0.8)',
  };

  const xpPercentage = (xp / xpToNext) * 100;
  const segments = 20;

  return (
    <div className="min-h-screen bg-bg-main p-4 pt-6 font-mono pb-24">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-neon-cyan text-[10px] tracking-[0.3em] mb-2"
            style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-cyan)' }}>
          PLAYER STATS
        </h1>
        <div className="flex items-center gap-2">
          <div className="px-2 py-1 bg-neon-green text-black text-[8px] font-bold"
               style={{ fontFamily: 'var(--font-arcade)' }}>
            LVL {level}
          </div>
          <TrendingUp size={16} className="text-neon-green animate-pulse" />
        </div>
      </div>

      {/* XP Progress Bar - Segmented Street Fighter Style */}
      <div className="bg-bg-card border-2 border-neon-green p-4 mb-6"
           style={{ boxShadow: 'var(--glow-green)' }}>
        <div className="flex justify-between text-[8px] mb-2">
          <span className="text-neon-green">EXPERIENCE</span>
          <span className="text-neon-gold">{xp} / {xpToNext} XP</span>
        </div>

        {/* Segmented Bar */}
        <div className="flex gap-[2px] h-6 bg-black p-1">
          {[...Array(segments)].map((_, i) => {
            const segmentThreshold = ((i + 1) / segments) * 100;
            const isFilled = xpPercentage >= segmentThreshold;
            
            return (
              <motion.div
                key={i}
                className="flex-1"
                initial={{ scaleY: 0 }}
                animate={{ 
                  scaleY: isFilled ? 1 : 0,
                  backgroundColor: isFilled ? '#00ff88' : '#1a1a2e'
                }}
                transition={{ delay: i * 0.05, duration: 0.2 }}
                style={{
                  boxShadow: isFilled ? 'var(--glow-green)' : 'none',
                  transformOrigin: 'bottom',
                }}
              />
            );
          })}
        </div>

        <button
          onClick={() => setShowLevelUp(true)}
          className="w-full mt-3 bg-black border-2 border-neon-green text-neon-green py-2 text-[10px] hover:bg-neon-green hover:text-black transition-all"
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: 'var(--glow-green)' }}
        >
          VIEW PROGRESSION
        </button>
      </div>

      {/* Radar Chart - Skill Web */}
      <div className="bg-bg-card border-2 border-neon-cyan p-4 mb-6"
           style={{ boxShadow: 'var(--glow-cyan)' }}>
        <div className="text-center text-[10px] text-neon-cyan mb-4 tracking-widest"
             style={{ fontFamily: 'var(--font-arcade)' }}>
          SKILL WEB
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={stats}>
              <PolarGrid stroke="#444466" strokeWidth={1} />
              <PolarAngleAxis 
                dataKey="attribute" 
                tick={{ fill: '#00e5ff', fontSize: 9, fontFamily: 'Share Tech Mono' }}
              />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]}
                tick={{ fill: '#444466', fontSize: 8 }}
              />
              <Radar
                name="Base"
                dataKey="base"
                stroke="#444466"
                fill="#444466"
                fillOpacity={0.3}
              />
              <Radar
                name="Current"
                dataKey="current"
                stroke="#00e5ff"
                fill="#00e5ff"
                fillOpacity={0.6}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Stat Details */}
        <div className="grid grid-cols-2 gap-2 mt-4">
          {stats.map((stat) => (
            <div 
              key={stat.attribute}
              className="bg-black border border-neon-cyan p-2"
            >
              <div className="text-[8px] text-neon-cyan mb-1">{stat.attribute}</div>
              <div className="flex items-center gap-2">
                <span className="text-neon-green text-sm font-bold"
                      style={{ fontFamily: 'var(--font-arcade)' }}>
                  {stat.current}
                </span>
                <TrendingUp size={10} className="text-neon-green" />
                <span className="text-[8px] text-muted-gray">+{stat.current - stat.base}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Equipment / Inventory */}
      <div className="bg-bg-card border-2 border-neon-gold p-4"
           style={{ boxShadow: 'var(--glow-gold)' }}>
        <div className="flex items-center justify-between mb-4">
          <span className="text-neon-gold text-[10px] tracking-widest"
                style={{ fontFamily: 'var(--font-arcade)' }}>
            EQUIPMENT
          </span>
          <Award size={16} className="text-neon-gold animate-pulse" />
        </div>

        <div className="space-y-3">
          {equipment.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-black border-2 p-3 flex items-center gap-3"
              style={{ 
                borderColor: rarityColors[item.rarity],
                boxShadow: rarityGlow[item.rarity],
              }}
            >
              {/* Item Icon Slot */}
              <div 
                className="w-12 h-12 border-2 flex items-center justify-center"
                style={{ 
                  borderColor: rarityColors[item.rarity],
                  backgroundColor: `${rarityColors[item.rarity]}20`,
                }}
              >
                <span className="text-xl" style={{ fontFamily: 'var(--font-arcade)' }}>
                  {item.slot[0]}
                </span>
              </div>

              {/* Item Details */}
              <div className="flex-1">
                <div className="text-[8px] text-muted-gray mb-1">{item.slot}</div>
                <div className="text-[10px] font-bold mb-1"
                     style={{ color: rarityColors[item.rarity] }}>
                  {item.name}
                </div>
                <div className="text-[8px] text-neon-green">{item.power}</div>
              </div>

              {/* Rarity Badge */}
              <div 
                className="px-2 py-1 text-[7px] border"
                style={{ 
                  borderColor: rarityColors[item.rarity],
                  color: rarityColors[item.rarity],
                }}
              >
                {item.rarity.toUpperCase()}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Level Up Popup Overlay */}
      <AnimatePresence>
        {showLevelUp && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
            onClick={() => setShowLevelUp(false)}
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 180 }}
              transition={{ type: 'spring', duration: 0.7 }}
              className="bg-bg-card border-4 border-neon-gold p-6 max-w-[340px] relative"
              style={{ boxShadow: '0 0 40px rgba(255, 230, 0, 0.8)' }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Fireworks Effect */}
              <div className="absolute -top-2 left-1/4 text-neon-gold text-2xl animate-bounce">✦</div>
              <div className="absolute -top-3 right-1/4 text-neon-gold text-xl animate-bounce" style={{ animationDelay: '0.2s' }}>✦</div>
              <div className="absolute -top-1 left-1/2 text-neon-gold text-3xl animate-bounce" style={{ animationDelay: '0.1s' }}>★</div>

              <div className="text-center">
                <motion.h2 
                  className="text-neon-gold text-xl mb-4 tracking-wider"
                  style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-gold)' }}
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  LEVEL UP!
                </motion.h2>

                <div className="bg-black border-2 border-neon-gold p-4 mb-4">
                  <div className="text-neon-gold text-4xl mb-2"
                       style={{ fontFamily: 'var(--font-arcade)' }}>
                    {level} → {level + 1}
                  </div>
                  <div className="text-neon-cyan text-[8px]">NEW ABILITIES UNLOCKED</div>
                </div>

                <div className="space-y-2 text-left mb-4">
                  {[
                    { stat: 'SPEED', increase: '+3' },
                    { stat: 'POWER', increase: '+2' },
                    { stat: 'SERVE', increase: '+4' },
                  ].map((upgrade, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + i * 0.2 }}
                      className="flex justify-between items-center bg-black border border-neon-green p-2"
                    >
                      <span className="text-neon-cyan text-[10px]">{upgrade.stat}</span>
                      <div className="flex items-center gap-2">
                        <TrendingUp size={12} className="text-neon-green" />
                        <span className="text-neon-green text-sm font-bold"
                              style={{ fontFamily: 'var(--font-arcade)' }}>
                          {upgrade.increase}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <button
                  onClick={() => setShowLevelUp(false)}
                  className="w-full bg-neon-gold text-black py-3 text-[10px] hover:bg-black hover:text-neon-gold border-2 border-neon-gold transition-all"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  CONTINUE
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

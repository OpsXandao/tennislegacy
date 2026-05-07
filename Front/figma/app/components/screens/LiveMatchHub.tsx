import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Target, Crosshair } from 'lucide-react';

export default function LiveMatchHub() {
  const [momentum, setMomentum] = useState(65); // Player momentum (0-100)
  const [matchLog, setMatchLog] = useState([
    { time: '12:34', message: 'ACE! UNRETURNABLE!', type: 'success' },
    { time: '12:33', message: 'Winner - Forehand', type: 'success' },
    { time: '12:32', message: 'Unforced Error', type: 'error' },
    { time: '12:31', message: 'Winner - Backhand', type: 'success' },
  ]);
  
  const [courtSurface, setCourtSurface] = useState<'hard' | 'clay' | 'grass'>('hard');
  const [score, setScore] = useState({
    playerSets: 2,
    opponentSets: 1,
    playerGames: 5,
    opponentGames: 4,
    playerPoints: 40,
    opponentPoints: 30,
  });

  useEffect(() => {
    // Simulate momentum changes
    const interval = setInterval(() => {
      setMomentum(prev => {
        const change = (Math.random() - 0.5) * 10;
        return Math.max(0, Math.min(100, prev + change));
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const courtColors = {
    hard: '#1e40af',
    clay: '#dc2626',
    grass: '#166534',
  };

  const surfaceLabels = {
    hard: 'HARD COURT',
    clay: 'CLAY COURT',
    grass: 'GRASS COURT',
  };

  return (
    <div className="min-h-screen bg-bg-main p-4 pt-6 font-mono">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-neon-green text-[10px] tracking-[0.3em] mb-2 animate-pulse"
            style={{ fontFamily: 'var(--font-arcade)', textShadow: 'var(--glow-green)' }}>
          TENNIS LEGACY
        </h1>
      </div>

      {/* Scoreboard */}
      <div className="bg-bg-card border-2 border-neon-green p-4 mb-4 relative"
           style={{ boxShadow: 'var(--glow-green)' }}>
        {/* LIVE Indicator */}
        <div className="absolute -top-3 left-4 bg-neon-red px-3 py-1 animate-pulse"
             style={{ boxShadow: '0 0 15px rgba(255, 23, 68, 0.8)' }}>
          <span className="text-[8px] font-bold tracking-widest"
                style={{ fontFamily: 'var(--font-arcade)' }}>
            ● LIVE
          </span>
        </div>

        <div className="flex justify-between items-center text-[10px] mb-3">
          <span className="text-neon-cyan">QUARTERFINAL</span>
          <span className="text-neon-gold">{surfaceLabels[courtSurface]}</span>
        </div>

        {/* Player Scores */}
        <div className="space-y-2">
          {/* Player 1 */}
          <div className="flex items-center justify-between bg-black/30 p-2 border border-neon-green">
            <span className="text-neon-green text-xs font-bold">YOU</span>
            <div className="flex gap-3 items-center">
              <span className="text-neon-green text-2xl font-bold" style={{ fontFamily: 'var(--font-arcade)' }}>
                {score.playerSets}
              </span>
              <span className="text-neon-green text-xl">{score.playerGames}</span>
              <span className="text-neon-green text-xl w-10 text-center">{score.playerPoints}</span>
            </div>
          </div>

          {/* Opponent */}
          <div className="flex items-center justify-between bg-black/30 p-2 border border-neon-pink/50">
            <span className="text-neon-pink text-xs">OPPONENT</span>
            <div className="flex gap-3 items-center">
              <span className="text-neon-pink text-2xl font-bold" style={{ fontFamily: 'var(--font-arcade)' }}>
                {score.opponentSets}
              </span>
              <span className="text-neon-pink text-xl">{score.opponentGames}</span>
              <span className="text-neon-pink text-xl w-10 text-center">{score.opponentPoints}</span>
            </div>
          </div>
        </div>

        {/* Labels */}
        <div className="flex justify-end gap-3 mt-2 text-[8px] text-muted-gray">
          <span className="ml-8">SETS</span>
          <span>GMS</span>
          <span className="w-10 text-center">PTS</span>
        </div>
      </div>

      {/* Momentum Bar */}
      <div className="bg-bg-card border-2 border-neon-cyan p-3 mb-4"
           style={{ boxShadow: '0 0 10px rgba(0, 229, 255, 0.3)' }}>
        <div className="flex justify-between text-[8px] mb-2">
          <span className="text-neon-green">PLAYER</span>
          <span className="text-neon-cyan" style={{ fontFamily: 'var(--font-arcade)' }}>MOMENTUM</span>
          <span className="text-neon-pink">OPPONENT</span>
        </div>
        <div className="h-4 bg-black border border-neon-cyan relative overflow-hidden">
          <motion.div
            className="absolute top-0 left-0 h-full"
            style={{
              width: `${momentum}%`,
              background: momentum > 50 
                ? 'linear-gradient(90deg, #00ff88 0%, #00ff88 100%)'
                : 'linear-gradient(90deg, #ff0055 0%, #ff0055 100%)',
              boxShadow: momentum > 50 
                ? '0 0 15px rgba(0, 255, 136, 0.5)'
                : '0 0 15px rgba(255, 0, 85, 0.5)',
            }}
            animate={{ width: `${momentum}%` }}
            transition={{ duration: 0.5 }}
          />
          {/* Segment marks */}
          <div className="absolute inset-0 flex">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="flex-1 border-r border-bg-main/50" />
            ))}
          </div>
        </div>
      </div>

      {/* Live Court View */}
      <div className="bg-bg-card border-2 border-neon-gold p-4 mb-4"
           style={{ boxShadow: 'var(--glow-gold)' }}>
        <div className="text-center text-[8px] text-neon-gold mb-2 tracking-widest"
             style={{ fontFamily: 'var(--font-arcade)' }}>
          COURT VIEW
        </div>
        
        {/* Court Surface Selector */}
        <div className="flex gap-2 mb-3 justify-center">
          {(['hard', 'clay', 'grass'] as const).map((surface) => (
            <button
              key={surface}
              onClick={() => setCourtSurface(surface)}
              className={`px-2 py-1 text-[8px] border-2 transition-all ${
                courtSurface === surface 
                  ? 'border-neon-gold text-neon-gold'
                  : 'border-muted-gray text-muted-gray hover:border-neon-cyan hover:text-neon-cyan'
              }`}
              style={courtSurface === surface ? { boxShadow: 'var(--glow-gold)' } : {}}
            >
              {surface.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Pixel Art Tennis Court */}
        <div 
          className="relative w-full h-48 border-4 border-white mx-auto"
          style={{ 
            backgroundColor: courtColors[courtSurface],
            imageRendering: 'pixelated',
          }}
        >
          {/* Court Lines */}
          <div className="absolute inset-0">
            {/* Center Line */}
            <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-white -translate-x-1/2" />
            {/* Service Boxes */}
            <div className="absolute left-1/4 top-1/4 right-1/4 bottom-1/4 border-2 border-white" />
            {/* Baseline */}
            <div className="absolute left-0 right-0 top-[10%] h-1 bg-white" />
            <div className="absolute left-0 right-0 bottom-[10%] h-1 bg-white" />
          </div>

          {/* Player Sprites (Pixel Art) */}
          <motion.div
            className="absolute bottom-[15%] left-1/2 -translate-x-1/2"
            animate={{ x: [-5, 5, -5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="w-6 h-4 bg-neon-green border border-white"
                 style={{ boxShadow: 'var(--glow-green)' }} />
          </motion.div>

          {/* Opponent Sprite */}
          <motion.div
            className="absolute top-[15%] left-1/2 -translate-x-1/2"
            animate={{ x: [5, -5, 5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="w-6 h-4 bg-neon-pink border border-white"
                 style={{ boxShadow: 'var(--glow-pink)' }} />
          </motion.div>

          {/* Ball */}
          <motion.div
            className="absolute w-2 h-2 bg-neon-gold rounded-full"
            style={{ boxShadow: 'var(--glow-gold)' }}
            animate={{
              left: ['25%', '75%', '25%'],
              top: ['80%', '20%', '80%'],
            }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </div>
      </div>

      {/* Tactical Radar */}
      <div className="bg-bg-card border-2 border-neon-cyan p-4 mb-4"
           style={{ boxShadow: 'var(--glow-cyan)' }}>
        <div className="flex items-center justify-between mb-3">
          <span className="text-neon-cyan text-[10px] tracking-wider"
                style={{ fontFamily: 'var(--font-arcade)' }}>
            <Crosshair className="inline mr-2" size={12} />
            SHOT PLANNER
          </span>
          <Target size={16} className="text-neon-cyan animate-pulse" />
        </div>

        {/* Zone Selection Grid */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          {['LEFT', 'CENTER', 'RIGHT'].map((zone) => (
            <button
              key={zone}
              className="bg-black border-2 border-neon-cyan p-3 text-[8px] text-neon-cyan hover:bg-neon-cyan hover:text-black transition-all"
              style={{ boxShadow: '0 0 10px rgba(0, 229, 255, 0.3)' }}
            >
              {zone}
            </button>
          ))}
        </div>

        {/* Depth Selection */}
        <div className="grid grid-cols-3 gap-2">
          {['BASELINE', 'MID-COURT', 'NET'].map((depth) => (
            <button
              key={depth}
              className="bg-black border-2 border-neon-gold p-2 text-[8px] text-neon-gold hover:bg-neon-gold hover:text-black transition-all"
              style={{ boxShadow: '0 0 10px rgba(255, 230, 0, 0.3)' }}
            >
              {depth}
            </button>
          ))}
        </div>
      </div>

      {/* Match Log Terminal */}
      <div className="bg-black border-2 border-neon-green p-3"
           style={{ boxShadow: 'var(--glow-green)' }}>
        <div className="text-neon-green text-[8px] mb-2 tracking-widest"
             style={{ fontFamily: 'var(--font-arcade)' }}>
          &gt; MATCH LOG
        </div>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {matchLog.map((log, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`text-[9px] flex gap-2 ${
                log.type === 'success' ? 'text-neon-green' : 'text-neon-pink'
              }`}
              style={{ animation: 'flicker 3s infinite' }}
            >
              <span className="text-neon-cyan">[{log.time}]</span>
              <span>{log.message}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
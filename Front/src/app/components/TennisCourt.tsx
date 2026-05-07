import { motion } from 'motion/react'
import { AnimatePresence } from 'motion/react';
import { useEffect, useState } from 'react'

interface TennisCourtProps {
  surface?: string; // 'dura', 'saibro', 'grama'
  lastPointWinner?: 'jogador' | 'adversario';
  serving?: 'jogador' | 'adversario';
}

const SURFACE_COLORS: Record<string, { inner: string; outer: string }> = {
  dura: { inner: '#2a5ba7', outer: '#1e3a5f' },
  saibro: { inner: '#c24e00', outer: '#8b3a00' },
  grama: { inner: '#2d8a2d', outer: '#1e5f1e' },
  default: { inner: '#2a5ba7', outer: '#1e3a5f' },
};

export function TennisCourt({ surface = 'dura', lastPointWinner, serving }: TennisCourtProps) {
  const [ballPos, setBallPos] = useState({ x: 50, y: 50 });
  const [showBall, setShowBall] = useState(false);

  const colors = SURFACE_COLORS[surface.toLowerCase()] || SURFACE_COLORS.default;

  // Gera uma posição aleatória na quadra quando o ponto muda
  useEffect(() => {
    if (lastPointWinner) {
      // Jogador fica na esquerda e adversario na direita.
      // A bolinha aparece no lado do perdedor do ponto.
      const isPlayerWinner = lastPointWinner === 'jogador';
      const newX = isPlayerWinner ? 56 + Math.random() * 24 : 18 + Math.random() * 24;
      const newY = 22 + Math.random() * 56;

      setBallPos({ x: newX, y: newY });
      setShowBall(true);

      // Esconde a bola após um tempo para simular o intervalo entre pontos
      const timer = setTimeout(() => setShowBall(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [lastPointWinner, serving]);

  return (
    <div className="mx-auto w-full max-w-[420px] bg-[#1a1a2e] border-4 border-black p-2 shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      <div 
        className="relative aspect-[3/2] w-full overflow-hidden"
        style={{ backgroundColor: colors.outer }}
      >
        {/* Quadra Interna */}
        <div 
          className="absolute inset-[10%] border-2 border-white"
          style={{ backgroundColor: colors.inner }}
        >
          {/* Rede */}
          <div className="absolute bottom-0 left-1/2 top-0 w-1 -translate-x-1/2 bg-white/50 shadow-[0_0_5px_white]" />
          
          {/* Linhas de serviço */}
          <div className="absolute bottom-0 left-[25%] top-0 w-0.5 bg-white" />
          <div className="absolute bottom-0 right-[25%] top-0 w-0.5 bg-white" />
          <div className="absolute left-[25%] right-[25%] top-1/2 h-0.5 -translate-y-1/2 bg-white" />

          {/* Linhas laterais (simples/duplas) */}
          <div className="absolute left-0 right-0 top-[10%] h-0.5 bg-white/30" />
          <div className="absolute left-0 right-0 bottom-[10%] h-0.5 bg-white/30" />
        </div>

        {/* Bolinha de Tênis */}
        <AnimatePresence>
          {showBall && (
            <motion.div
              initial={{ scale: 3, opacity: 0, y: -20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="absolute w-3 h-3 bg-[#ccff00] rounded-full z-10"
              style={{ 
                left: `${ballPos.x}%`, 
                top: `${ballPos.y}%`,
                boxShadow: '0 0 8px #ccff00, 1px 1px 0px black'
              }}
            >
              {/* Detalhe da bola (pixel) */}
              <div className="absolute top-0 left-1/2 w-0.5 h-full bg-black/20 -translate-x-1/2 rotate-45" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Indicador de Saque */}
        {!showBall && serving && (
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="absolute top-1/2 h-4 w-4 -translate-y-1/2 text-xl"
            style={{ left: serving === 'jogador' ? '10%' : '86%' }}
          >
            🎾
          </motion.div>
        )}

        <div className="absolute left-[10%] top-1/2 -translate-y-1/2 arcade-font text-[10px] text-white">
          VOCE
        </div>
        <div className="absolute right-[7%] top-1/2 -translate-y-1/2 arcade-font text-[10px] text-white text-right">
          ADV
        </div>
      </div>

      <div className="mt-2 text-center">
        <span className="arcade-font text-[10px] text-[#888] uppercase tracking-tighter">
          SURFACE: <span style={{ color: colors.inner }}>{surface}</span>
        </span>
      </div>
    </div>
  );
}

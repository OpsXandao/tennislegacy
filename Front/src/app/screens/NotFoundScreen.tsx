import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { NeonButton } from '../components/NeonButton';
import { TronGrid } from '../components/TronGrid';

export function NotFoundScreen() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative">
      <TronGrid />
      
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center relative z-10"
      >
        {/* 404 Error */}
        <motion.div
          animate={{ 
            textShadow: [
              '0 0 10px #ff0055, 0 0 20px #ff0055',
              '0 0 20px #ff0055, 0 0 40px #ff0055',
              '0 0 10px #ff0055, 0 0 20px #ff0055'
            ]
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className="pixel-font text-8xl text-[#ff0055] mb-6"
        >
          404
        </motion.div>

        {/* Error Message */}
        <div className="mb-8">
          <h2 className="text-neon-yellow pixel-font text-2xl mb-4">
            GAME OVER
          </h2>
          <div className="arcade-font text-sm text-[#888] mb-2">
            PÁGINA NÃO ENCONTRADA
          </div>
          <div className="arcade-font text-xs text-[#666]">
            Esta tela não existe no jogo
          </div>
        </div>

        {/* Glitching Tennis Ball */}
        <motion.div
          animate={{
            x: [-10, 10, -10],
            rotate: [0, 360],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "linear"
          }}
          className="text-6xl mb-8 opacity-50"
        >
          🎾
        </motion.div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3 w-full max-w-xs">
          <NeonButton onClick={() => navigate('/')} variant="green">
            TELA INICIAL
          </NeonButton>
          <NeonButton onClick={() => navigate('/hub')} variant="cyan">
            VOLTAR AO HUB
          </NeonButton>
          <NeonButton onClick={() => navigate(-1)} variant="pink">
            PÁGINA ANTERIOR
          </NeonButton>
        </div>

        {/* Insert Coin */}
        <motion.div
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="mt-12 arcade-font text-xs text-[#888]"
        >
          ERROR CODE: 404_NOT_FOUND
        </motion.div>
      </motion.div>
    </div>
  );
}

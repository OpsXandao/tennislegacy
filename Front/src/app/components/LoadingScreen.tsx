import { motion } from 'motion/react';

export function LoadingScreen() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center"
      >
        {/* Tennis Ball Loading Animation */}
        <motion.div
          animate={{
            rotate: 360,
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "linear"
          }}
          className="text-8xl mb-8"
        >
          🎾
        </motion.div>

        {/* Loading Text */}
        <motion.h2
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="pixel-font text-lg text-neon-green mb-4"
        >
          LOADING...
        </motion.h2>

        {/* Loading Bar */}
        <div className="w-64 h-4 border-2 border-[#00ff88] mx-auto">
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear"
            }}
            className="h-full bg-[#00ff88]"
            style={{
              boxShadow: '0 0 10px #00ff88, inset 0 0 10px #00ff88'
            }}
          />
        </div>

        <div className="arcade-font text-xs text-[#888] mt-6">
          PREPARING YOUR TENNIS LEGACY...
        </div>
      </motion.div>
    </div>
  );
}

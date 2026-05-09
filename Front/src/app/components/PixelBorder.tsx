import { motion } from 'motion/react';

interface PixelBorderProps {
  children: React.ReactNode;
  color?: string;
  animated?: boolean;
  className?: string;
}

export function PixelBorder({ 
  children, 
  color = 'var(--neon-green)',
  animated = false,
  className = ''
}: PixelBorderProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={animated ? {
        boxShadow: [
          `0 0 5px ${color}`,
          `0 0 20px ${color}`,
          `0 0 5px ${color}`
        ]
      } : {}}
      transition={animated ? {
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut'
      } : {}}
    >
      {/* Corner decorations - top left */}
      <div 
        className="absolute top-0 left-0 w-3 h-3 border-l-2 border-t-2"
        style={{ borderColor: color }}
      />
      
      {/* Corner decorations - top right */}
      <div 
        className="absolute top-0 right-0 w-3 h-3 border-r-2 border-t-2"
        style={{ borderColor: color }}
      />
      
      {/* Corner decorations - bottom left */}
      <div 
        className="absolute bottom-0 left-0 w-3 h-3 border-l-2 border-b-2"
        style={{ borderColor: color }}
      />
      
      {/* Corner decorations - bottom right */}
      <div 
        className="absolute bottom-0 right-0 w-3 h-3 border-r-2 border-b-2"
        style={{ borderColor: color }}
      />

      {/* Main border */}
      <div 
        className="border-2 h-full"
        style={{ borderColor: color }}
      >
        {children}
      </div>
    </motion.div>
  );
}

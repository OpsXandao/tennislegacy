import { motion } from 'motion/react';

interface NeonCardProps {
  children: React.ReactNode;
  variant?: 'green' | 'pink' | 'yellow' | 'cyan';
  className?: string;
  onClick?: () => void;
  hover?: boolean;
}

const COLORS = {
  green:  { border: 'var(--neon-green)', glow: 'var(--glow-green-sm)', glowHover: 'var(--glow-green)', tint: 'color-mix(in srgb, var(--neon-green) 6%, transparent)' },
  pink:   { border: 'var(--neon-pink)', glow: 'var(--glow-pink-sm)', glowHover: 'var(--glow-pink)', tint: 'color-mix(in srgb, var(--neon-pink) 6%, transparent)' },
  yellow: { border: 'var(--neon-yellow)', glow: 'var(--glow-gold-sm)', glowHover: 'var(--glow-gold)', tint: 'color-mix(in srgb, var(--neon-yellow) 6%, transparent)' },
  cyan:   { border: 'var(--neon-cyan)', glow: 'var(--glow-cyan-sm)', glowHover: 'var(--glow-cyan)', tint: 'color-mix(in srgb, var(--neon-cyan) 6%, transparent)' },
} as const;

export function NeonCard({
  children,
  variant = 'green',
  className = '',
  onClick,
  hover = true,
}: NeonCardProps) {
  const c = COLORS[variant];
  const isInteractive = hover && !!onClick;

  return (
    <motion.div
      onClick={onClick}
      whileHover={isInteractive ? { scale: 1.015 } : {}}
      whileTap={onClick ? { scale: 0.985 } : {}}
      className={`
        app-panel border-2 p-4
        transition-[box-shadow,background-color] duration-200
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      style={{
        borderColor: c.border,
        boxShadow: c.glow,
        backgroundImage: `linear-gradient(135deg, ${c.tint} 0%, transparent 60%)`,
      }}
      onHoverStart={() => {
        if (isInteractive) {
          (document.activeElement as HTMLElement)?.blur?.();
        }
      }}
      whileFocus={{}}
    >
      {children}
    </motion.div>
  );
}

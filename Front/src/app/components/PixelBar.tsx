import { motion } from 'motion/react';

interface PixelBarProps {
  value: number; // 0-100
  maxBlocks?: number;
  variant?: 'green' | 'pink' | 'yellow' | 'cyan';
  label?: string;
  showValue?: boolean;
}

const COLORS: Record<string, string> = {
  green:  'var(--neon-green)',
  pink:   'var(--neon-pink)',
  yellow: 'var(--neon-yellow)',
  cyan:   'var(--neon-cyan)',
};

export function PixelBar({
  value,
  maxBlocks = 10,
  variant = 'green',
  label,
  showValue = false,
}: PixelBarProps) {
  const color = COLORS[variant];
  const filled = Math.round((Math.max(0, Math.min(100, value)) / 100) * maxBlocks);

  return (
    <div className="w-full">
      {label && (
        <div className="flex items-center justify-between mb-1.5">
          <span className="arcade-font text-[9px] uppercase tracking-wider text-[#777]">{label}</span>
          {showValue && (
            <span className="arcade-font text-[9px] tabular-nums" style={{ color }}>{value}</span>
          )}
        </div>
      )}
      <div className="flex gap-[3px]">
        {Array.from({ length: maxBlocks }).map((_, i) => {
          const isFilled = i < filled;
          // Last filled block gets extra glow for a "power" feel
          const isLast = i === filled - 1;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, scaleY: 0.4 }}
              animate={{ opacity: 1, scaleY: 1 }}
              transition={{ delay: i * 0.03, duration: 0.2, ease: 'easeOut' }}
              className="h-[14px] flex-1 border"
              style={{
                backgroundColor: isFilled ? color : 'transparent',
                borderColor: isFilled ? color : '#2a2a2a',
                boxShadow: isLast
                  ? `0 0 8px ${color}, inset 0 0 4px ${color}`
                  : isFilled
                  ? `0 0 3px ${color}`
                  : 'none',
                opacity: isFilled ? 1 : 0.5,
              }}
            />
          );
        })}
      </div>
    </div>
  );
}

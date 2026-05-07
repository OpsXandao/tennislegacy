import { motion } from 'motion/react';
import { useState } from 'react';
import { triggerHaptic } from '../utils/feedback';

interface NeonButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'green' | 'pink' | 'yellow' | 'cyan';
  className?: string;
  blink?: boolean;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

const COLORS = {
  green:  { border: 'var(--neon-green)', bg: 'var(--neon-green)', text: '#08131a', glow: 'var(--glow-green-sm)', hoverBg: 'color-mix(in srgb, var(--neon-green) 14%, transparent)' },
  pink:   { border: 'var(--neon-pink)', bg: 'var(--neon-pink)', text: '#08131a', glow: 'var(--glow-pink-sm)', hoverBg: 'color-mix(in srgb, var(--neon-pink) 14%, transparent)' },
  yellow: { border: 'var(--neon-yellow)', bg: 'var(--neon-yellow)', text: '#08131a', glow: 'var(--glow-gold-sm)', hoverBg: 'color-mix(in srgb, var(--neon-yellow) 14%, transparent)' },
  cyan:   { border: 'var(--neon-cyan)', bg: 'var(--neon-cyan)', text: '#08131a', glow: 'var(--glow-cyan-sm)', hoverBg: 'color-mix(in srgb, var(--neon-cyan) 14%, transparent)' },
} as const;

export function NeonButton({
  children,
  onClick,
  variant = 'green',
  className = '',
  blink = false,
  disabled = false,
  type = 'button',
}: NeonButtonProps) {
  const [isPressed, setIsPressed] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const c = COLORS[variant];

  const handleClick = () => {
    if (disabled) return;
    triggerHaptic('medium');
    onClick?.();
  };

  const bgColor = isPressed
    ? c.bg
    : isHovered && !disabled
    ? c.hoverBg
    : 'transparent';

  const textColor = isPressed ? c.text : c.border;

  return (
    <motion.button
      type={type}
      onClick={handleClick}
      disabled={disabled}
      onTouchStart={() => { if (!disabled) { setIsPressed(true); triggerHaptic('light'); } }}
      onTouchEnd={() => setIsPressed(false)}
      onMouseDown={() => { if (!disabled) setIsPressed(true); }}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => { setIsPressed(false); setIsHovered(false); }}
      onMouseEnter={() => { if (!disabled) setIsHovered(true); }}
      whileTap={disabled ? {} : { scale: 0.97 }}
      className={`
        relative min-h-[44px] px-4 py-3
        border-2 transition-colors duration-150
        arcade-font text-center uppercase tracking-wider leading-tight whitespace-normal break-words
        select-none
        ${disabled ? 'opacity-35 cursor-not-allowed' : 'cursor-pointer'}
        ${blink && !disabled ? 'animate-pulse' : ''}
        ${className}
      `}
      style={{
        borderColor: disabled ? `${c.border}55` : c.border,
        backgroundColor: bgColor,
        color: disabled ? `${c.border}88` : textColor,
        boxShadow: disabled ? 'none' : isPressed ? `var(--glow-${variant === 'yellow' ? 'gold' : variant})` : c.glow,
        transition: 'background-color 0.12s, color 0.12s, box-shadow 0.12s',
      }}
    >
      <span className="relative z-10">{children}</span>
    </motion.button>
  );
}

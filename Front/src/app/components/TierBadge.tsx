interface TierBadgeProps {
  tier: 'grand-slam' | 'masters-1000' | 'atp-500' | 'atp-250';
  size?: 'sm' | 'md' | 'lg';
}

export function TierBadge({ tier, size = 'md' }: TierBadgeProps) {
  const configs = {
    'grand-slam': {
      icon: '★',
      color: 'var(--neon-yellow)',
      label: 'GRAND SLAM'
    },
    'masters-1000': {
      icon: '●',
      color: 'var(--neon-green)',
      label: 'MASTERS 1000'
    },
    'atp-500': {
      icon: '●',
      color: 'var(--neon-cyan)',
      label: 'ATP 500'
    },
    'atp-250': {
      icon: '●',
      color: '#ffffff',
      label: 'ATP 250'
    }
  };

  const sizes = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  const config = configs[tier];

  return (
    <div 
      className={`
        inline-flex max-w-full items-center gap-2
        border-2 arcade-font uppercase leading-tight
        ${sizes[size]}
      `}
      style={{
        borderColor: config.color,
        color: config.color,
        boxShadow: `0 0 5px ${config.color}`
      }}
    >
      <span className="pixel-font shrink-0">{config.icon}</span>
      <span className="break-words">{config.label}</span>
    </div>
  );
}

import { PixelFlag } from './PixelFlag';

interface PlayerRowProps {
  rank: number;
  name: string;
  points: number;
  nationality?: string;
  isCurrentPlayer?: boolean;
  change?: number;
}

export function PlayerRow({ 
  rank, 
  name, 
  points, 
  nationality,
  isCurrentPlayer = false,
  change
}: PlayerRowProps) {
  const isTop10 = rank <= 10;
  const rankColor = rank <= 3 ? 'var(--neon-yellow)' : isTop10 ? 'var(--neon-green)' : '#ffffff';

  return (
    <div 
      className={`
        grid grid-cols-[72px_minmax(0,1fr)_88px] gap-3 items-center
        px-4 py-3 border transition-all duration-200 min-h-[70px]
        ${isCurrentPlayer ? 'bg-[#1a1a2e]' : 'bg-transparent'}
      `}
      style={{
        borderColor: isCurrentPlayer ? 'var(--neon-green)' : 'transparent',
        boxShadow: isCurrentPlayer ? '0 0 10px #00ff88' : 'none'
      }}
    >
      {/* Rank */}
      <div className="text-left">
        <div 
          className="pixel-font text-2xl leading-none"
          style={{ color: rankColor }}
        >
          {rank <= 3 ? (
            rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉'
          ) : (
            `#${rank}`
          )}
        </div>
        {change !== undefined && change !== 0 && (
          <div className={`text-xs arcade-font ${change > 0 ? 'text-neon-green' : 'text-neon-pink'}`}>
            {change > 0 ? '▲' : '▼'}{Math.abs(change)}
          </div>
        )}
      </div>

      {/* Name and Flag */}
      <div className="min-w-0 flex items-center gap-3">
        <div className="shrink-0">
          <PixelFlag countryCode={nationality} size="md" />
        </div>
        <div className="min-w-0">
          <span className="arcade-font uppercase truncate block text-sm leading-tight">{name}</span>
        </div>
      </div>

      {/* Points */}
      <div className="text-right shrink-0">
        <div 
          className="arcade-font text-lg leading-none"
          style={{ color: 'var(--neon-cyan)' }}
        >
          {points.toLocaleString('pt-BR')}
        </div>
        <div className="text-[10px] text-[#888] arcade-font mt-1">PTS</div>
      </div>
    </div>
  );
}

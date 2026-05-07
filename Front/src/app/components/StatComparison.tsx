import { PixelBar } from './PixelBar';

interface StatComparisonProps {
  player1Stats: {
    name: string;
    stats: {
      speed: number;
      power: number;
      mental: number;
    };
  };
  player2Stats: {
    name: string;
    stats: {
      speed: number;
      power: number;
      mental: number;
    };
  };
}

export function StatComparison({ player1Stats, player2Stats }: StatComparisonProps) {
  const statLabels = [
    { key: 'speed' as const, label: 'SPEED' },
    { key: 'power' as const, label: 'POWER' },
    { key: 'mental' as const, label: 'MENTAL' }
  ];

  return (
    <div className="bg-[#1a1a2e] border-2 border-[#00e5ff] p-4">
      <div className="arcade-font text-xs text-center text-[#00e5ff] mb-4">
        STAT COMPARISON
      </div>

      {/* Player Names */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center arcade-font text-sm text-[#ff0055]">
          {player1Stats.name}
        </div>
        <div className="text-center arcade-font text-sm text-[#00ff88]">
          {player2Stats.name}
        </div>
      </div>

      {/* Stats */}
      <div className="space-y-4">
        {statLabels.map(({ key, label }) => (
          <div key={key}>
            <div className="arcade-font text-xs text-center text-[#888] mb-2">
              {label}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <PixelBar
                value={player1Stats.stats[key]}
                variant="pink"
                maxBlocks={6}
              />
              <PixelBar
                value={player2Stats.stats[key]}
                variant="green"
                maxBlocks={6}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

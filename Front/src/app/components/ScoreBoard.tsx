interface ScoreBoardProps {
  player1Name: string;
  player2Name: string;
  sets1: number;
  sets2: number;
  games1: number;
  games2: number;
  points1: string;
  points2: string;
}

export function ScoreBoard({
  player1Name,
  player2Name,
  sets1,
  sets2,
  games1,
  games2,
  points1,
  points2
}: ScoreBoardProps) {
  return (
    <div className="w-full">
      {/* Player Names */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="bg-[#1a1a2e] border-2 border-neon-pink p-3 text-center">
          <div className="arcade-font text-xs text-neon-pink mb-1">OPPONENT</div>
          <div className="pixel-font text-sm text-neon-pink truncate">{player1Name}</div>
        </div>
        <div className="bg-[#1a1a2e] border-2 border-neon-green p-3 text-center">
          <div className="arcade-font text-xs text-neon-green mb-1">YOU</div>
          <div className="pixel-font text-sm text-neon-green truncate">{player2Name}</div>
        </div>
      </div>

      {/* Scoreboard */}
      <div className="bg-black border-4 border-neon-green p-4 neon-glow-green">
        <div className="grid grid-cols-3 gap-4">
          {/* Sets */}
          <div className="text-center">
            <div className="arcade-font text-xs text-[#888] mb-2">SETS</div>
            <div className="pixel-font text-3xl text-neon-pink mb-1">{sets1}</div>
            <div className="text-[#888]">|</div>
            <div className="pixel-font text-3xl text-neon-green mt-1">{sets2}</div>
          </div>

          {/* Games */}
          <div className="text-center">
            <div className="arcade-font text-xs text-[#888] mb-2">GAMES</div>
            <div className="pixel-font text-3xl text-neon-pink mb-1">{games1}</div>
            <div className="text-[#888]">-</div>
            <div className="pixel-font text-3xl text-neon-green mt-1">{games2}</div>
          </div>

          {/* Points */}
          <div className="text-center">
            <div className="arcade-font text-xs text-[#888] mb-2">POINTS</div>
            <div className="pixel-font text-2xl text-neon-pink mb-1">{points1}</div>
            <div className="text-[#888]">-</div>
            <div className="pixel-font text-2xl text-neon-green mt-1">{points2}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

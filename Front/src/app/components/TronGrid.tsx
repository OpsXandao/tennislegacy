export function TronGrid() {
  return (
    <div className="fixed inset-0 pointer-events-none opacity-10 z-0">
      <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="var(--neon-green)"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
      
      {/* Horizontal lines */}
      <div className="absolute inset-0">
        {Array.from({ length: 10 }).map((_, i) => (
          <div
            key={`h-${i}`}
            className="absolute left-0 right-0 h-px"
            style={{
              top: `${(i + 1) * 10}%`,
              background: 'linear-gradient(90deg, transparent, #00ff88, transparent)',
              opacity: 0.2
            }}
          />
        ))}
      </div>

      {/* Vertical lines */}
      <div className="absolute inset-0">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={`v-${i}`}
            className="absolute top-0 bottom-0 w-px"
            style={{
              left: `${(i + 1) * 12.5}%`,
              background: 'linear-gradient(180deg, transparent, #00ff88, transparent)',
              opacity: 0.2
            }}
          />
        ))}
      </div>
    </div>
  );
}

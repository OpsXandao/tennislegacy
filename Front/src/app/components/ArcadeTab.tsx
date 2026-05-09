interface ArcadeTabProps {
  tabs: string[];
  activeTab: number;
  onChange: (index: number) => void;
  color?: 'green' | 'pink' | 'yellow' | 'cyan';
}

const COLORS = {
  green:  { active: 'var(--neon-green)', glow: '0 0 8px #00ff88, 0 0 16px rgba(0,255,136,0.4)' },
  pink:   { active: 'var(--neon-pink)', glow: '0 0 8px #ff0055, 0 0 16px rgba(255,0,85,0.4)'  },
  yellow: { active: 'var(--neon-yellow)', glow: '0 0 8px #ffe600, 0 0 16px rgba(255,230,0,0.4)' },
  cyan:   { active: 'var(--neon-cyan)', glow: '0 0 8px #00e5ff, 0 0 16px rgba(0,229,255,0.4)' },
} as const;

export function ArcadeTab({ tabs, activeTab, onChange, color = 'green' }: ArcadeTabProps) {
  const c = COLORS[color];

  return (
    <div className="flex gap-1.5 overflow-x-auto pb-0.5" style={{ scrollbarWidth: 'none' }}>
      {tabs.map((tab, index) => {
        const isActive = index === activeTab;
        return (
          <button
            key={index}
            onClick={() => onChange(index)}
            className="flex items-center gap-1.5 px-3 py-2 min-h-[40px] border-2 arcade-font uppercase text-[10px] whitespace-nowrap transition-all duration-150 select-none"
            style={{
              borderColor: isActive ? c.active : `${c.active}33`,
              backgroundColor: isActive ? c.active : 'transparent',
              color: isActive ? '#000' : `${c.active}99`,
              boxShadow: isActive ? c.glow : 'none',
              letterSpacing: '0.08em',
            }}
          >
            {isActive && <span className="pixel-font text-[6px]">▶</span>}
            {tab}
          </button>
        );
      })}
    </div>
  );
}

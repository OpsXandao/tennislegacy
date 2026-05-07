import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  color?: 'green' | 'pink' | 'yellow' | 'cyan';
  backTo?: string;
  onBack?: () => void;
  right?: React.ReactNode;
  children?: React.ReactNode; // slot para tabs, etc.
}

const COLORS = {
  green:  { text: 'var(--neon-green)', border: 'border-b-2', glow: 'var(--text-glow-green)' },
  pink:   { text: 'var(--neon-pink)', border: 'border-b-2', glow: 'var(--text-glow-pink)'  },
  yellow: { text: 'var(--neon-yellow)', border: 'border-b-2', glow: 'var(--text-glow-gold)'  },
  cyan:   { text: 'var(--neon-cyan)', border: 'border-b-2', glow: 'var(--text-glow-cyan)'  },
} as const;

export function PageHeader({
  title,
  subtitle,
  color = 'green',
  backTo,
  onBack,
  right,
  children,
}: PageHeaderProps) {
  const navigate = useNavigate();
  const c = COLORS[color];

  function handleBack() {
    if (onBack) { onBack(); return; }
    if (backTo) { navigate(backTo); return; }
    navigate(-1);
  }

  return (
    <div className={`app-shell sticky top-0 z-20 backdrop-blur-sm ${c.border} px-4 pt-4 pb-0`} style={{ borderColor: c.text }}>
      <div className="flex items-start gap-3 pb-3">
        <button
          onClick={handleBack}
          className="mt-0.5 shrink-0 transition-opacity hover:opacity-70"
          style={{ color: c.text }}
        >
          <ArrowLeft size={20} />
        </button>

        <div className="flex-1 min-w-0">
          <h1
            className="text-[11px] tracking-[0.25em] font-bold truncate"
            style={{
              fontFamily: 'var(--font-arcade)',
              color: c.text,
              textShadow: c.glow,
            }}
          >
            {title}
          </h1>
          {subtitle && (
            <div className="app-muted mt-0.5 truncate text-[8px]" style={{ fontFamily: 'var(--font-arcade)' }}>
              {subtitle}
            </div>
          )}
        </div>

        {right && <div className="shrink-0">{right}</div>}
      </div>

      {children && <div className="pb-3">{children}</div>}
    </div>
  );
}

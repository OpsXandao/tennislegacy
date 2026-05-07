import { motion } from 'motion/react'

interface SurfaceBackgroundProps {
  surface: string;
}

const COLORS: Record<string, { main: string; accent: string; pattern: string }> = {
  dura: { 
    main: '#1e3a5f', 
    accent: '#2a5ba7',
    pattern: 'linear-gradient(45deg, rgba(255,255,255,0.05) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.05) 75%, transparent 75%, transparent)'
  },
  saibro: { 
    main: '#8b3a00', 
    accent: '#c24e00',
    pattern: 'radial-gradient(rgba(0,0,0,0.1) 1px, transparent 1px)'
  },
  grama: { 
    main: '#1e5f1e', 
    accent: '#2d8a2d',
    pattern: 'linear-gradient(90deg, rgba(255,255,255,0.05) 50%, transparent 50%)'
  },
  default: { 
    main: '#1a1a2e', 
    accent: '#16213e',
    pattern: ''
  }
};

export function SurfaceBackground({ surface }: SurfaceBackgroundProps) {
  const type = surface.toLowerCase();
  const config = COLORS[type] || COLORS.default;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30 select-none">
      {/* Cor Base */}
      <div 
        className="absolute inset-0" 
        style={{ backgroundColor: config.main }} 
      />
      
      {/* Padrão de Textura */}
      <div 
        className="absolute inset-0" 
        style={{ 
          backgroundImage: config.pattern,
          backgroundSize: type === 'grama' ? '40px 100%' : type === 'saibro' ? '10px 10px' : '20px 20px',
          backgroundColor: config.accent
        }} 
      />

      {/* Sombras de profundidade (estilo pixel art) */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/60" />
    </div>
  );
}

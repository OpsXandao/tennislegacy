import { motion } from 'motion/react'

interface CityPixelBackgroundProps {
  cityName: string;
}

// Silhuetas em paths simplificados (estilo pixel/low-poly)
const SILHOUETTES: Record<string, JSX.Element> = {
  Melbourne: (
    <path d="M10,80 L30,40 L50,80 L70,30 L90,80 L110,40 L130,80 L150,30 L170,80" stroke="currentColor" strokeWidth="4" fill="none" />
  ),
  Paris: (
    <path d="M80,80 L90,60 L90,20 L100,20 L100,60 L110,80 M70,80 Q90,75 120,80 M85,55 H105 M92,35 H98" stroke="currentColor" strokeWidth="3" fill="none" />
  ),
  London: (
    <path d="M40,80 V30 H60 V80 M45,30 V20 H55 V30 M80,80 V50 Q100,20 120,50 V80 M100,50 V80" stroke="currentColor" strokeWidth="3" fill="none" />
  ),
  'New York': (
    <path d="M20,80 V40 H40 V80 M50,80 V20 H70 V80 M80,80 V50 H100 V80 M110,80 V30 H130 V80" stroke="currentColor" strokeWidth="4" fill="none" />
  ),
  Madrid: (
    <path d="M40,80 V40 H160 V80 M60,40 V30 H140 V40 M90,40 V20 H110 V40" stroke="currentColor" strokeWidth="3" fill="none" />
  ),
  Rome: (
    <path d="M30,80 Q30,30 100,30 Q170,30 170,80 M60,80 V50 M100,80 V50 M140,80 V50" stroke="currentColor" strokeWidth="4" fill="none" />
  ),
  Rio: (
    <path d="M100,80 V40 M80,50 H120 M90,40 L100,30 L110,40" stroke="currentColor" strokeWidth="4" fill="none" />
  ),
  Generic: (
    <path d="M0,80 L20,60 L20,40 L40,40 L40,70 L60,50 L80,50 L80,20 L100,20 L100,60 L120,40 L140,40 L140,80" stroke="currentColor" strokeWidth="2" fill="none" />
  )
}

export function CityPixelBackground({ cityName }: CityPixelBackgroundProps) {
  const name = Object.keys(SILHOUETTES).find(k => cityName.includes(k)) || 'Generic';
  const silhouette = SILHOUETTES[name];

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20 select-none">
      <svg 
        viewBox="0 0 200 100" 
        className="absolute bottom-0 w-full h-full"
        preserveAspectRatio="none"
        style={{ imageRendering: 'pixelated' }}
      >
        <motion.g
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 1 }}
          className="text-neon-cyan"
        >
          {silhouette}
          {/* Adiciona uns "pixels" extras no fundo */}
          <rect x="10" y="20" width="4" height="4" fill="currentColor" opacity="0.5" />
          <rect x="180" y="40" width="4" height="4" fill="currentColor" opacity="0.3" />
          <rect x="150" y="10" width="2" height="2" fill="currentColor" opacity="0.2" />
        </motion.g>
      </svg>
      
      {/* Scanlines apenas no fundo da cidade */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#1a1a2e] to-transparent" />
    </div>
  );
}

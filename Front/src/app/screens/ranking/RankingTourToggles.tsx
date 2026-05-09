type Tour = 'atp' | 'wta' | 'davis'
type Modalidade = 'simples' | 'duplas' | 'clay' | 'hard' | 'grass'

const SUPERFICIES: { id: Modalidade; label: string; color: string }[] = [
  { id: 'clay', label: 'ARGILA', color: '#cd7f32' },
  { id: 'hard', label: 'DURO', color: 'var(--neon-cyan)' },
  { id: 'grass', label: 'GRAMA', color: 'var(--neon-green)' },
]

interface RankingTourTogglesProps {
  tour: Tour
  modalidade: Modalidade
  onTourChange: (tour: Tour) => void
  onModalidadeChange: (modalidade: Modalidade) => void
}

export function RankingTourToggles({
  tour,
  modalidade,
  onTourChange,
  onModalidadeChange,
}: RankingTourTogglesProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex gap-1.5">
        <button
          onClick={() => onTourChange('atp')}
          className={`border-2 px-2 py-1.5 text-[7px] transition-all ${tour === 'atp' ? 'border-neon-green bg-neon-green text-black' : 'border-neon-green bg-black text-neon-green'}`}
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: tour === 'atp' ? 'var(--glow-green-sm)' : 'none' }}
        >
          ATP
        </button>
        <button
          onClick={() => onTourChange('wta')}
          className={`border-2 px-2 py-1.5 text-[7px] transition-all ${tour === 'wta' ? 'border-neon-pink bg-neon-pink text-black' : 'border-neon-pink bg-black text-neon-pink'}`}
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: tour === 'wta' ? 'var(--glow-pink-sm)' : 'none' }}
        >
          WTA
        </button>
        <button
          onClick={() => { onTourChange('davis'); onModalidadeChange('simples') }}
          className={`border-2 px-2 py-1.5 text-[7px] transition-all ${tour === 'davis' ? 'border-neon-yellow bg-neon-yellow text-black' : 'border-neon-yellow bg-black text-neon-yellow'}`}
          style={{ fontFamily: 'var(--font-arcade)', boxShadow: tour === 'davis' ? 'var(--glow-gold)' : 'none' }}
        >
          DAVIS
        </button>
      </div>

      <div className={`flex gap-1 ${tour === 'davis' ? 'pointer-events-none opacity-40' : ''}`}>
        {(['simples', 'duplas'] as const).map((m) => (
          <button
            key={m}
            onClick={() => onModalidadeChange(m)}
            className={`flex-1 border px-1 py-1 text-[6px] transition-all ${modalidade === m ? 'border-white bg-white text-black' : 'border-white/30 text-white/60'}`}
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {m === 'simples' ? 'SIM' : 'DUP'}
          </button>
        ))}
        {SUPERFICIES.map((s) => (
          <button
            key={s.id}
            onClick={() => onModalidadeChange(s.id)}
            className="flex-1 border px-1 py-1 text-[6px] transition-all"
            style={{
              fontFamily: 'var(--font-arcade)',
              borderColor: modalidade === s.id ? s.color : `${s.color}44`,
              background: modalidade === s.id ? s.color : 'transparent',
              color: modalidade === s.id ? '#000' : `${s.color}99`,
            }}
          >
            {s.label.slice(0, 3)}
          </button>
        ))}
      </div>
    </div>
  )
}

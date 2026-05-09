import { NeonCard } from '../../components'

const ATRIB_TECNICOS: [string, string][] = [
  ['saque', 'SAQUE'], ['forehand', 'FOREHAND'], ['backhand', 'BACKHAND'],
  ['voleio', 'VOLEIO'], ['topspin', 'TOPSPIN'], ['slice', 'SLICE'],
  ['lob', 'LOB'], ['winner', 'WINNER'],
]
const ATRIB_FISICOS: [string, string][] = [
  ['movimento', 'MOVIMENTO'], ['fisico', 'FÍSICO'],
]
const ATRIB_MENTAIS: [string, string][] = [
  ['concentracao', 'CONCENTRAÇÃO'], ['agressividade', 'AGRESSIVIDADE'],
  ['leitura_de_jogo', 'LEIT. JOGO'], ['determinacao', 'DETERMINAÇÃO'],
]

interface Props {
  atributos: Record<string, number>
  atributosMentais: Record<string, number>
}

export function AtributosTab({ atributos, atributosMentais }: Props) {
  return (
    <div className="space-y-3">
      <NeonCard variant="cyan" hover={false}>
        <div className="arcade-font text-[9px] text-neon-cyan tracking-widest mb-3">TÉCNICOS</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {ATRIB_TECNICOS.map(([key, label]) =>
            atributos[key] !== undefined ? (
              <div key={key} className="border border-[#163041] bg-[#0b1821] px-4 py-3">
                <div className="arcade-font text-[9px] text-[#8eb5c8] tracking-widest">{label}</div>
                <div className="pixel-font text-2xl text-neon-cyan mt-2">{atributos[key]}</div>
              </div>
            ) : null
          )}
        </div>
      </NeonCard>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <NeonCard variant="green" hover={false}>
          <div className="arcade-font text-[9px] text-neon-green tracking-widest mb-3">FÍSICOS</div>
          <div className="grid grid-cols-2 gap-3">
            {ATRIB_FISICOS.map(([key, label]) =>
              atributos[key] !== undefined ? (
                <div key={key} className="border border-[#173520] bg-[#0c160f] px-4 py-3">
                  <div className="arcade-font text-[9px] text-[#9fd8b2] tracking-widest">{label}</div>
                  <div className="pixel-font text-2xl text-neon-green mt-2">{atributos[key]}</div>
                </div>
              ) : null
            )}
          </div>
        </NeonCard>

        <NeonCard variant="yellow" hover={false}>
          <div className="arcade-font text-[9px] text-neon-yellow tracking-widest mb-3">MENTAIS</div>
          <div className="grid grid-cols-2 gap-3">
            {ATRIB_MENTAIS.map(([key, label]) =>
              atributosMentais[key] !== undefined ? (
                <div key={key} className="border border-[#3a3516] bg-[#171407] px-4 py-3">
                  <div className="arcade-font text-[9px] text-[#d8ca7a] tracking-widest">{label}</div>
                  <div className="pixel-font text-2xl text-neon-yellow mt-2">{atributosMentais[key]}</div>
                </div>
              ) : null
            )}
          </div>
        </NeonCard>
      </div>
    </div>
  )
}

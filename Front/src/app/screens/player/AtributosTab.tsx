import { NeonCard } from '../../components'

const ATRIB_SAQUE: [string, string][] = [
  ['vel_saque', 'VEL. SAQUE'],
  ['pre_saque', 'PREP. SAQUE'],
  ['segundo_saque', '2º SAQUE'],
  ['retorno', 'RETORNO'],
]
const ATRIB_GOLPES: [string, string][] = [
  ['forehand', 'FOREHAND'],
  ['backhand', 'BACKHAND'],
  ['voleio', 'VOLEIO'],
  ['smash', 'SMASH'],
  ['topspin', 'TOPSPIN'],
  ['slice', 'SLICE'],
  ['lob', 'LOB'],
  ['winner', 'WINNER'],
]
const ATRIB_FISICOS: [string, string][] = [
  ['velocidade', 'VELOCIDADE'],
  ['aceleracao', 'ACELERAÇÃO'],
  ['resistencia', 'RESISTÊNCIA'],
  ['forca', 'FORÇA'],
  ['agilidade', 'AGILIDADE'],
]
const ATRIB_MENTAIS: [string, string][] = [
  ['determinacao', 'DETERMINAÇÃO'],
  ['compostura', 'COMPOSTURA'],
  ['agressividade', 'AGRESSIVIDADE'],
  ['leitura_de_jogo', 'LEITURA'],
  ['clutch', 'CLUTCH'],
  ['consistencia', 'CONSISTÊNCIA'],
]

function AtribCard({
  label, value, borderColor, textColor, bgColor,
}: {
  label: string; value: number; borderColor: string; textColor: string; bgColor: string
}) {
  const color = value >= 80 ? 'var(--neon-yellow)' : value >= 70 ? textColor : '#7a8fa0'
  return (
    <div className="border px-3 py-3" style={{ borderColor, background: bgColor }}>
      <div className="arcade-font text-ui-tag tracking-widest" style={{ color: textColor }}>{label}</div>
      <div className="pixel-font text-2xl mt-2" style={{ color }}>{value}</div>
    </div>
  )
}

interface Props {
  atributos: Record<string, number>
  atributosMentais: Record<string, number>
}

export function AtributosTab({ atributos, atributosMentais }: Props) {
  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <NeonCard variant="cyan" hover={false}>
          <div className="arcade-font text-ui-tag text-neon-cyan tracking-widest mb-3">SAQUE</div>
          <div className="grid grid-cols-2 gap-3">
            {ATRIB_SAQUE.map(([key, label]) =>
              atributos[key] !== undefined ? (
                <AtribCard key={key} label={label} value={atributos[key]}
                  borderColor="#163041" textColor="#8eb5c8" bgColor="#0b1821" />
              ) : null
            )}
          </div>
        </NeonCard>

        <NeonCard variant="cyan" hover={false}>
          <div className="arcade-font text-ui-tag text-neon-cyan tracking-widest mb-3">GOLPES</div>
          <div className="grid grid-cols-2 gap-3">
            {ATRIB_GOLPES.map(([key, label]) =>
              atributos[key] !== undefined ? (
                <AtribCard key={key} label={label} value={atributos[key]}
                  borderColor="#163041" textColor="#8eb5c8" bgColor="#0b1821" />
              ) : null
            )}
          </div>
        </NeonCard>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <NeonCard variant="green" hover={false}>
          <div className="arcade-font text-ui-tag text-neon-green tracking-widest mb-3">FÍSICOS</div>
          <div className="grid grid-cols-2 gap-3">
            {ATRIB_FISICOS.map(([key, label]) =>
              atributos[key] !== undefined ? (
                <AtribCard key={key} label={label} value={atributos[key]}
                  borderColor="#173520" textColor="#9fd8b2" bgColor="#0c160f" />
              ) : null
            )}
          </div>
        </NeonCard>

        <NeonCard variant="yellow" hover={false}>
          <div className="arcade-font text-ui-tag text-neon-yellow tracking-widest mb-3">MENTAIS</div>
          <div className="grid grid-cols-2 gap-3">
            {ATRIB_MENTAIS.map(([key, label]) =>
              atributosMentais[key] !== undefined ? (
                <AtribCard key={key} label={label} value={atributosMentais[key]}
                  borderColor="#3a3516" textColor="#d8ca7a" bgColor="#171407" />
              ) : null
            )}
          </div>
        </NeonCard>
      </div>
    </div>
  )
}

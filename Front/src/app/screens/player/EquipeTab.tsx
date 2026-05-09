import { useNavigate } from 'react-router'
import { NeonCard, NeonButton } from '../../components'
import type { MembroEquipe } from '../../../types'

interface Props {
  equipe: {
    treinador: MembroEquipe | null
    fisio: MembroEquipe | null
    psicologo: MembroEquipe | null
    empresario: MembroEquipe | null
  } | null
}

function bonusLines(bonus: Record<string, any>): string[] {
  const lines: string[] = []
  if (bonus.bonus_progressao) lines.push(`+${Math.round(bonus.bonus_progressao * 100)}% chance de evoluir no treino`)
  if (bonus.bonus_recuperacao) lines.push(`+${bonus.bonus_recuperacao} energia recuperada/semana`)
  if (bonus.bonus_xp && bonus.bonus_xp !== 1) lines.push(`×${bonus.bonus_xp.toFixed(1)} XP por partida`)
  if (bonus.bonus_mental) lines.push(`+${bonus.bonus_mental} em atributos mentais`)
  if (bonus.bonus_fadiga) lines.push(`-${bonus.bonus_fadiga}% fadiga acumulada`)
  if (bonus.bonus_fisico_pct) lines.push(`+${Math.round(bonus.bonus_fisico_pct * 100)}% atributos físicos`)
  if (bonus.bonus_patrocinio) lines.push(`+${Math.round(bonus.bonus_patrocinio * 100)}% valor de patrocínios`)
  return lines
}

const SLOTS: [string, keyof NonNullable<Props['equipe']>, string][] = [
  ['TÉCNICO', 'treinador', '🏋️'],
  ['FISIOTERAPEUTA', 'fisio', '🩺'],
  ['PSICÓLOGO', 'psicologo', '🧠'],
  ['EMPRESÁRIO', 'empresario', '💼'],
]

export function EquipeTab({ equipe }: Props) {
  const navigate = useNavigate()

  return (
    <div className="space-y-3">
      {SLOTS.map(([cargo, key, icon]) => {
        const m = equipe?.[key] as any
        const lines = bonusLines(m?.bonus ?? {})
        return (
          <NeonCard key={cargo} variant="green" hover={false}>
            <div className="flex justify-between items-start">
              <div className="flex items-start gap-3 flex-1">
                <span className="text-xl mt-0.5">{icon}</span>
                <div className="flex-1">
                  <div className="arcade-font text-[10px] text-neon-green">{cargo}</div>
                  <div className="arcade-font text-[9px] text-[#888] mt-1">{m ? m.nome : 'VAGO'}</div>
                  {m && lines.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {lines.map((line, i) => (
                        <div key={i} className="arcade-font text-[8px] text-neon-yellow flex items-center gap-1">
                          <span>▸</span> {line}
                        </div>
                      ))}
                    </div>
                  )}
                  {m && lines.length === 0 && (
                    <div className="mt-1 arcade-font text-[8px] text-[#555]">bônus não carregados</div>
                  )}
                </div>
              </div>
              {m && (
                <div className="flex gap-1 ml-2 mt-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className={`w-2 h-2 border ${i < m.nivel ? 'bg-neon-yellow border-neon-yellow' : 'border-[#333]'}`} />
                  ))}
                </div>
              )}
            </div>
          </NeonCard>
        )
      })}
      <NeonButton variant="green" className="w-full" onClick={() => navigate('/market')}>
        MERCADO DE PROFISSIONAIS
      </NeonButton>
    </div>
  )
}

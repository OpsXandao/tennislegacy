import { motion, AnimatePresence } from 'motion/react'
import { NeonButton } from '../../../components/NeonButton'
import { StatLine } from '../components'
import { destaquePartida } from '../model'
import type { PlacarState, JogadorState, AdversarioInfo } from '../types'

interface PostMatchViewProps {
  fase: 'pos-stats' | 'pos-consequencias'
  placar: PlacarState
  nomeJogador: string
  adversario: AdversarioInfo
  log: string[]
  jogadorPosjogo: JogadorState | null
  jogador: JogadorState | null
  jogadorAntesRef: { current: JogadorState | null }
  setFase: (fase: any) => void
  handleContinuarPosJogo: () => void
}

export function PostMatchView({
  fase,
  placar,
  nomeJogador,
  adversario,
  log,
  jogadorPosjogo,
  jogador,
  jogadorAntesRef,
  setFase,
  handleContinuarPosJogo,
}: PostMatchViewProps) {
  if (fase === 'pos-stats') {
    const sj = placar.stats_j
    const sa = placar.stats_a
    const editorial = destaquePartida(placar, nomeJogador, adversario.nome, log)
    return (
      <div className="app-shell min-h-screen flex flex-col">
        <div className="p-4 border-b-2 border-neon-cyan app-panel shrink-0">
          <div className="arcade-font text-[9px] text-neon-cyan tracking-widest">RESUMO DA PARTIDA</div>
          <div className="arcade-font text-lg text-white mt-1">
            {placar.placar_final || `${placar.sets[0]} × ${placar.sets[1]} sets`}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="border border-neon-cyan/25 bg-[#04101b] p-4">
            <div className="arcade-font text-[10px] text-[#4bb8d1] tracking-widest mb-2">PONTO DE VIRADA</div>
            <div className="arcade-font text-[12px] text-[#d7f3ff] leading-relaxed">{editorial}</div>
          </div>
          {sj && sa ? (
            <div className="border border-neon-cyan/20 bg-[#020611] p-4 space-y-2">
              <div className="grid grid-cols-[1fr_auto_1fr] gap-2 arcade-font text-[12px] mb-4">
                <div className="text-neon-green truncate">{nomeJogador}</div>
                <div className="text-[#d7f3ff] text-center text-[14px] tracking-wide">STAT</div>
                <div className="text-right text-[#ff8d6d] truncate">{adversario.nome}</div>
              </div>
              <StatLine label="Aces" j={sj.aces} a={sa.aces} />
              <StatLine label="Duplas faltas" j={sj.duplas_faltas} a={sa.duplas_faltas} />
              <StatLine label="1º saque %" j={sj.primeiro_saque_pct} a={sa.primeiro_saque_pct} />
              <StatLine label="Winners" j={sj.winners} a={sa.winners} />
              <StatLine label="Erros N/F" j={sj.erros_nao_forcados} a={sa.erros_nao_forcados} />
              <StatLine label="Pts saque" j={sj.pontos_saque_pct} a={sa.pontos_saque_pct} />
              <StatLine label="Break pts" j={sj.break_points} a={sa.break_points} />
            </div>
          ) : (
            <div className="arcade-font text-[#555] text-center py-8">
              Estatísticas não disponíveis.
            </div>
          )}
          {log.length > 0 && (
            <div className="border border-[#1a1a2e] p-3">
              <div className="arcade-font text-[14px] text-[#d7f3ff] mb-3 tracking-wide text-center">
                MOMENTOS
              </div>
              <div className="space-y-1 max-h-40 overflow-y-auto">
                {[...log].reverse().slice(0, 20).map((linha, i) => (
                  <div
                    key={i}
                    className="arcade-font text-[12px] flex gap-2 leading-relaxed"
                    style={{ color: i === 0 ? '#d7f3ff' : '#9cb4c7' }}
                  >
                    <span className="text-neon-cyan">▸</span>
                    <span>{linha}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="p-4 border-t border-[#1a1a2e] shrink-0">
          <NeonButton 
            variant="cyan" 
            className="w-full" 
            disabled={!jogadorPosjogo}
            onClick={() => setFase('pos-consequencias')}
          >
            {jogadorPosjogo ? 'VER CONSEQUÊNCIAS →' : 'CARREGANDO DADOS...'}
          </NeonButton>
        </div>
      </div>
    )
  }

  if (fase === 'pos-consequencias') {
    const j = jogadorPosjogo || jogador
    const antes = jogadorAntesRef.current
    const xpGanho = j && antes ? j.xp - antes.xp : null
    const rankingDelta = j && antes ? antes.ranking - (j.ranking ?? antes.ranking) : null
    const subiuNivel = j && antes ? j.nivel > antes.nivel : false

    return (
      <div className="app-shell min-h-screen flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {subiuNivel && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="border-2 border-neon-yellow bg-[#0f0c00] p-5 text-center"
              style={{ boxShadow: '0 0 30px rgba(255,230,0,0.4)' }}
            >
              <div className="pixel-font text-2xl text-neon-yellow">SUBIU DE NÍVEL!</div>
              <div className="arcade-font text-[10px] text-[#888] mt-2">
                NÍVEL {j?.nivel}
              </div>
            </motion.div>
          )}

          <div className="border-2 border-neon-green bg-[#050e05] p-4">
            <div className="arcade-font text-[9px] text-neon-green mb-4 tracking-widest">
              RESULTADO FINAL
            </div>
            <div className="space-y-3">
              {xpGanho !== null && (
                <div className="flex items-center justify-between">
                  <span className="arcade-font text-[10px] text-[#8aa0b5]">XP GANHO</span>
                  <motion.span
                    initial={{ opacity: 0, x: 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="arcade-font text-[13px] text-neon-green"
                  >
                    +{Math.max(0, xpGanho)}
                  </motion.span>
                </div>
              )}
              {rankingDelta !== null && rankingDelta !== 0 && (
                <div className="flex items-center justify-between">
                  <span className="arcade-font text-[10px] text-[#8aa0b5]">RANKING</span>
                  <span
                    className="arcade-font text-[13px]"
                    style={{ color: rankingDelta > 0 ? 'var(--neon-green)' : 'var(--neon-pink)' }}
                  >
                    {rankingDelta > 0 ? `↑ ${rankingDelta}` : `↓ ${Math.abs(rankingDelta)}`}
                  </span>
                </div>
              )}
              {j && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="arcade-font text-[10px] text-[#8aa0b5]">NÍVEL</span>
                    <span className="arcade-font text-[13px] text-neon-yellow">{j.nivel}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="arcade-font text-[10px] text-[#8aa0b5]">SALDO</span>
                    <span className="arcade-font text-[13px] text-neon-cyan">
                      ${j.dinheiro?.toLocaleString('pt-BR') ?? '-'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="p-4 border-t border-[#1a1a2e] shrink-0">
          <NeonButton variant="green" className="w-full" onClick={handleContinuarPosJogo}>
            CONTINUAR →
          </NeonButton>
        </div>
      </div>
    )
  }

  return null
}

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { NeonButton } from '../../../components/NeonButton'
import { StatLine } from '../components'
import { gerarTituloPartida, gerarNarrativaPartida } from '../matchNarrative'
import { NewspaperModal } from '../../../components/NewspaperModal'
import type { PlacarState, JogadorState, AdversarioInfo } from '../types'

interface PostMatchViewProps {
  themeClass: string
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
  faseTorneio?: string
  nomeTorneio?: string
  tipoTorneio?: string
  comentarioParceiro?: string | null
}

export function PostMatchView({
  themeClass,
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
  faseTorneio,
  nomeTorneio,
  tipoTorneio,
  comentarioParceiro,
}: PostMatchViewProps) {
  const [showNewspaper, setShowNewspaper] = useState(false)
  const ganhou = placar.vencedor === 'jogador'
  const isFinal = faseTorneio?.toLowerCase() === 'final'

  useEffect(() => {
    if (!ganhou || !isFinal) return
    const t = setTimeout(() => setShowNewspaper(true), 1500)
    return () => clearTimeout(t)
  }, [ganhou, isFinal])

  if (fase === 'pos-stats') {
    const sj = placar.stats_j
    const sa = placar.stats_a
    const titulo = gerarTituloPartida(placar, nomeJogador, adversario.nome)
    const narrativa = gerarNarrativaPartida(placar, nomeJogador, adversario.nome, log)

    return (
      <div className={`app-shell match-theme-screen ${themeClass} min-h-screen flex flex-col`}>
        {showNewspaper && (
          <NewspaperModal
            headline={`${nomeJogador.toUpperCase()} É O CAMPEÃO EM ${nomeTorneio?.toUpperCase() || 'GRAND SLAM'}!`}
            subheadline={`O jovem talento supera ${adversario.nome} em uma final histórica para conquistar o título.`}
            category="TÍTULO CONQUISTADO"
            torneio={nomeTorneio}
            tipoTorneio={tipoTorneio}
            nacionalidadeJogador={jogador?.nacionalidade}
            onClose={() => setShowNewspaper(false)}
          />
        )}
        {/* Header narrativo */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="match-topbar p-4 border-b-2 app-panel shrink-0"
          style={{ borderColor: 'var(--match-accent)' }}
        >
          <div className="pixel-font text-xs text-neon-yellow mb-1 uppercase tracking-widest">
            {titulo}
          </div>
          <div className="arcade-font text-[12px] text-[#eaf4ff] leading-[1.7] italic">
            "{narrativa}"
          </div>
        </motion.div>

        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          {/* Stats Grid */}
          <div className="space-y-4">
            <h3 className="arcade-font text-[13px] text-neon-cyan tracking-widest border-b border-white/20 pb-2">
              ESTATÍSTICAS DA PARTIDA
            </h3>
            <div className="space-y-3">
              <StatLine label="ACES" j={sj?.aces} a={sa?.aces} />
              <StatLine label="DUPLAS FALTAS" j={sj?.duplas_faltas} a={sa?.duplas_faltas} />
              <StatLine label="1º SAQUE IN" j={sj?.primeiro_saque_pct} a={sa?.primeiro_saque_pct} />
              <StatLine label="WINNERS" j={sj?.winners} a={sa?.winners} />
              <StatLine label="ERROS NÃO FORÇ." j={sj?.erros_nao_forcados} a={sa?.erros_nao_forcados} />
              <StatLine label="BREAK POINTS" j={sj?.break_points} a={sa?.break_points} />
            </div>
          </div>

          {/* Rallies */}
          <div className="grid grid-cols-3 gap-2">
            <div className="app-panel border p-2 text-center border-white/5">
              <div className="text-[10px] arcade-font text-[#b7c7d8] mb-1">CURTOS</div>
              <div className="text-[10px] arcade-font text-white">{sj?.rallies_curtos}</div>
            </div>
            <div className="app-panel border p-2 text-center border-white/5">
              <div className="text-[10px] arcade-font text-[#b7c7d8] mb-1">MÉDIOS</div>
              <div className="text-[10px] arcade-font text-white">{sj?.rallies_medios}</div>
            </div>
            <div className="app-panel border p-2 text-center border-white/5">
              <div className="text-[10px] arcade-font text-[#b7c7d8] mb-1">LONGOS</div>
              <div className="text-[10px] arcade-font text-white">{sj?.rallies_longos}</div>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-white/5 shrink-0">
          <NeonButton
            variant={ganhou ? 'green' : 'cyan'}
            className="w-full"
            disabled={!jogadorPosjogo}
            onClick={() => setFase('pos-consequencias')}
          >
            {jogadorPosjogo ? 'VER CONSEQUÊNCIAS →' : 'CARREGANDO...'}
          </NeonButton>
        </div>
      </div>
    )
  }

  if (fase === 'pos-consequencias') {
    const j = jogadorPosjogo || jogador
    const antes = jogadorAntesRef.current
    const xpGanho = j && antes ? Math.max(0, j.xp - antes.xp) : null
    const rankingDelta = j && antes ? antes.ranking - (j.ranking ?? antes.ranking) : null
    const subiuNivel = j && antes ? j.nivel > antes.nivel : false
    // Usa variáveis CSS do tema de piso
    const accentVar = ganhou ? 'var(--match-accent)' : 'var(--match-rival)'
    const accentDim = ganhou ? 'var(--match-accent-dim)' : 'var(--match-rival-dim)'

    return (
      <div className={`app-shell match-theme-screen ${themeClass} min-h-screen flex flex-col ${ganhou ? 'postmatch-win' : 'postmatch-loss'}`}>
        <div className="flex-1 overflow-y-auto p-4 space-y-4 pt-8">

          {/* Level up — destaque máximo */}
          {subiuNivel && (
            <motion.div
              initial={{ opacity: 0, scale: 0.88 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ type: 'spring', stiffness: 260, damping: 20 }}
              className="border-2 border-neon-yellow p-6 text-center"
              style={{ boxShadow: '0 0 32px rgba(255,230,0,0.35)', background: '#0f0c00' }}
            >
              <div
                className="pixel-font text-xl text-neon-yellow"
                style={{ textShadow: '0 0 12px var(--neon-yellow)' }}
              >
                SUBIU DE NÍVEL!
              </div>
              <div className="arcade-font text-ui-caption text-[#888] mt-2 tracking-widest">
                NÍVEL {j?.nivel} DESBLOQUEADO
              </div>
            </motion.div>
          )}

          {/* Comentário do Parceiro de Duplas */}
          {comentarioParceiro && (
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-black/40 border-l-4 border-neon-cyan p-4 mb-2"
            >
              <div className="text-[7px] arcade-font text-neon-cyan mb-1 uppercase tracking-[0.2em]">PARCEIRO DE DUPLAS</div>
              <div className="text-[11px] arcade-font text-white italic leading-relaxed">
                "{comentarioParceiro}"
              </div>
            </motion.div>
          )}

          {/* Consequências principais */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: subiuNivel ? 0.3 : 0.1 }}
            className="border-2 p-5"
            style={{ borderColor: accentVar, background: accentDim }}
          >
            <div
              className="arcade-font text-ui-tag tracking-widest mb-4"
              style={{ color: accentVar }}
            >
              {ganhou ? 'PROGRESSÃO' : 'CONSEQUÊNCIAS'}
            </div>

            <div className="space-y-4">
              {xpGanho !== null && (
                <motion.div
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15 }}
                  className="flex items-center justify-between"
                >
                  <span className="arcade-font text-ui-caption text-[#8aa0b5]">EXPERIÊNCIA</span>
                  <span
                    className="arcade-font text-ui-lead"
                    style={{ color: accentVar }}
                  >
                    +{xpGanho} XP
                  </span>
                </motion.div>
              )}

              {rankingDelta !== null && rankingDelta !== 0 && (
                <motion.div
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.22 }}
                  className="flex items-center justify-between"
                >
                  <span className="arcade-font text-ui-caption text-[#8aa0b5]">RANKING</span>
                  <div className="text-right">
                    <div
                      className="arcade-font text-ui-lead"
                      style={{ color: rankingDelta > 0 ? 'var(--match-accent)' : 'var(--match-rival)' }}
                    >
                      {rankingDelta > 0 ? `↑ ${rankingDelta}` : `↓ ${Math.abs(rankingDelta)}`}
                    </div>
                    {j?.ranking && (
                      <div className="arcade-font text-ui-label text-[#666] mt-0.5">
                        Nº {j.ranking} no mundo
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {j && (
                <>
                  <div className="border-t border-white/5 pt-3 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="arcade-font text-ui-caption text-[#8aa0b5]">NÍVEL</span>
                      <span className="arcade-font text-ui-value text-neon-yellow">{j.nivel}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="arcade-font text-ui-caption text-[#8aa0b5]">SALDO</span>
                      <span className="arcade-font text-ui-value text-neon-cyan">
                        ${j.dinheiro?.toLocaleString('pt-BR') ?? '—'}
                      </span>
                    </div>
                  </div>
                </>
              )}
            </div>
          </motion.div>

          {/* Mensagem de encerramento contextual */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center arcade-font text-ui-caption text-[#4a5f6b] leading-relaxed px-4"
          >
            {ganhou
              ? 'Cada vitória escreve um parágrafo da sua história. Continue.'
              : 'As derrotas que dói são as que ensinam mais. Próximo round.'}
          </motion.div>
        </div>

        <div className="p-4 border-t border-white/5 shrink-0">
          <NeonButton variant="green" className="w-full" onClick={handleContinuarPosJogo}>
            CONTINUAR →
          </NeonButton>
        </div>
      </div>
    )
  }

  return null
}

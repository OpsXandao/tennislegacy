import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { Globe } from 'lucide-react'
import { PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

type NacaoEntry = {
  posicao: number
  pais: string
  codigo: string
  pontos: number
  flag: string
}

const POSICAO_COLOR: Record<number, string> = {
  1: '#ffe600',
  2: '#c0c0c0',
  3: '#cd7f32',
}

export function NationsRankingScreen() {
  const { jogador } = useGameStore()
  const [nacoes, setNacoes] = useState<NacaoEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    api.mundo
      .rankingNacoes()
      .then((r) => setNacoes(r.nacoes))
      .catch((e) => setErro(e.message ?? 'Erro ao carregar ranking de nações.'))
      .finally(() => setLoading(false))
  }, [])

  const nomeJogadorNacao = jogador?.nacionalidade ?? ''

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="RANKING DE NAÇÕES" color="cyan" backTo="/world">
        <p className="text-[9px] text-[#00e5ff]/60 mt-1" style={{ fontFamily: 'var(--font-mono)' }}>
          COPA DAVIS / BILLIE JEAN KING CUP
        </p>
      </PageHeader>

      <div className="p-4">
        {loading && (
          <div
            className="text-[10px] text-[#00e5ff]/60 text-center py-12"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            CARREGANDO...
          </div>
        )}

        {erro && (
          <div
            className="text-[10px] text-[#ff0055] text-center py-12 border border-[#ff0055]/30 bg-[#ff0055]/5 p-4"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {erro}
          </div>
        )}

        {!loading && !erro && nacoes.length === 0 && (
          <div
            className="text-[10px] text-white/30 text-center py-12"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            <Globe size={24} className="mx-auto mb-3 opacity-30" />
            NENHUM DADO DISPONÍVEL
          </div>
        )}

        {!loading && nacoes.length > 0 && (
          <div className="space-y-1">
            {/* Header */}
            <div
              className="grid grid-cols-[36px_1fr_auto] gap-2 px-3 py-1 text-[8px] text-white/30 border-b border-white/10"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              <span>#</span>
              <span>NAÇÃO</span>
              <span>PTS</span>
            </div>

            {nacoes.map((nacao, i) => {
              const isPlayer =
                nomeJogadorNacao &&
                (nacao.pais?.toLowerCase().includes(nomeJogadorNacao.toLowerCase()) ||
                  nacao.codigo?.toLowerCase() === nomeJogadorNacao.toLowerCase())
              const color = POSICAO_COLOR[nacao.posicao] ?? (isPlayer ? '#00e5ff' : '#ffffff')

              return (
                <motion.div
                  key={nacao.codigo ?? nacao.pais}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: Math.min(i * 0.02, 0.3) }}
                  className={`grid grid-cols-[36px_1fr_auto] gap-2 px-3 py-2.5 border-b items-center ${
                    isPlayer
                      ? 'border-[#00e5ff]/30 bg-[#00e5ff]/8'
                      : nacao.posicao <= 3
                      ? 'border-white/10 bg-white/3'
                      : 'border-white/5'
                  }`}
                >
                  {/* Posição */}
                  <span
                    className="text-[10px] font-bold tabular-nums"
                    style={{
                      fontFamily: 'var(--font-arcade)',
                      color,
                    }}
                  >
                    {nacao.posicao <= 3 ? (
                      <span>
                        {nacao.posicao === 1 ? '🥇' : nacao.posicao === 2 ? '🥈' : '🥉'}
                      </span>
                    ) : (
                      nacao.posicao
                    )}
                  </span>

                  {/* País */}
                  <div className="flex items-center gap-2 min-w-0">
                    {nacao.flag && (
                      <span className="text-base leading-none">{nacao.flag}</span>
                    )}
                    <span
                      className="text-[10px] truncate"
                      style={{
                        fontFamily: 'var(--font-arcade)',
                        color: isPlayer ? '#00e5ff' : nacao.posicao <= 3 ? color : '#ffffff',
                      }}
                    >
                      {nacao.pais}
                    </span>
                    {nacao.codigo && (
                      <span className="text-[8px] text-white/30 shrink-0">
                        {nacao.codigo}
                      </span>
                    )}
                    {isPlayer && (
                      <span
                        className="text-[7px] text-[#00e5ff] border border-[#00e5ff]/50 px-1 py-0.5 shrink-0"
                        style={{ fontFamily: 'var(--font-arcade)' }}
                      >
                        YOU
                      </span>
                    )}
                  </div>

                  {/* Pontos */}
                  <span
                    className="text-[10px] tabular-nums text-right"
                    style={{
                      fontFamily: 'var(--font-mono)',
                      color: isPlayer ? '#00e5ff' : nacao.posicao <= 3 ? color : '#ffffff99',
                    }}
                  >
                    {nacao.pontos?.toLocaleString('pt-BR')}
                  </span>
                </motion.div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

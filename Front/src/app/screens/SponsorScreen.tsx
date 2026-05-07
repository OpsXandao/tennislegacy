import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { DollarSign, Lock, CheckCircle } from 'lucide-react'
import { PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

type PatrocinioDisponivel = {
  id: string
  nome: string
  nivel: string
  valor_mensal: number
  valor_semanal: number
  requisito_ranking: number
  requisito_seguidores: number
  elegivel: boolean
  motivo_bloqueio: string
  descricao: string
}

const NIVEL_COLOR: Record<string, string> = {
  bronze: '#cd7f32',
  silver: '#c0c0c0',
  prata: '#c0c0c0',
  gold: '#ffe600',
  ouro: '#ffe600',
  platinum: '#00e5ff',
  platina: '#00e5ff',
  diamond: '#ff0055',
  diamante: '#ff0055',
}

function nivelColor(nivel: string) {
  return NIVEL_COLOR[nivel?.toLowerCase()] ?? '#aaaaaa'
}

export function SponsorScreen() {
  const { jogador } = useGameStore()
  const [disponiveis, setDisponiveis] = useState<PatrocinioDisponivel[]>([])
  const [loading, setLoading] = useState(true)
  const [mensagem, setMensagem] = useState<{ texto: string; ok: boolean } | null>(null)
  const [assinando, setAssinando] = useState<string | null>(null)

  useEffect(() => {
    api.jogador
      .patrociniosDisponiveis()
      .then((r) => setDisponiveis(r.patrocinadores))
      .catch(() => setDisponiveis([]))
      .finally(() => setLoading(false))
  }, [])

  async function handleAssinar(id: string) {
    setAssinando(id)
    setMensagem(null)
    try {
      const res = await api.jogador.assinarPatrocinio(id)
      setMensagem({ texto: res.mensagem, ok: res.ok })
      if (res.ok) {
        const updated = await api.jogador.patrociniosDisponiveis()
        setDisponiveis(updated.patrocinadores)
      }
    } catch (e: any) {
      setMensagem({ texto: e.message ?? 'Erro ao assinar patrocínio.', ok: false })
    } finally {
      setAssinando(null)
    }
  }

  const ativos = jogador?.patrocinios ?? []
  const elegiveis = disponiveis.filter((p) => p.elegivel)
  const bloqueados = disponiveis.filter((p) => !p.elegivel)

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="PATROCÍNIOS" color="gold" backTo="/player">
        <p className="text-[9px] text-[#ffe600]/60 mt-1" style={{ fontFamily: 'var(--font-mono)' }}>
          GERENCIE CONTRATOS E ASSINE NOVOS PATROCINADORES
        </p>
      </PageHeader>

      <div className="p-4 space-y-6">
        {/* Feedback message */}
        {mensagem && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className={`border-2 p-3 text-center text-[10px] ${
              mensagem.ok
                ? 'border-[#00ff88] bg-[#00ff88]/10 text-[#00ff88]'
                : 'border-[#ff0055] bg-[#ff0055]/10 text-[#ff0055]'
            }`}
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {mensagem.texto}
          </motion.div>
        )}

        {/* Patrocínios ativos */}
        {ativos.length > 0 && (
          <section>
            <h2
              className="text-[10px] text-[#ffe600] mb-3 flex items-center gap-2"
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              <CheckCircle size={12} />
              CONTRATOS ATIVOS ({ativos.length})
            </h2>
            <div className="space-y-2">
              {ativos.map((p: any) => (
                <div
                  key={p.nome}
                  className="border border-[#ffe600]/40 bg-[#ffe600]/5 p-3 flex items-center justify-between"
                >
                  <div>
                    <p
                      className="text-[10px] text-[#ffe600]"
                      style={{ fontFamily: 'var(--font-arcade)' }}
                    >
                      {p.nome}
                    </p>
                    <p className="text-[9px] text-[#ffe600]/50 mt-0.5">
                      {p.semanas_restantes} semanas restantes
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] text-[#00ff88]">R$ {p.valor?.toLocaleString('pt-BR')}</p>
                    <p className="text-[9px] text-white/40">/semana</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Disponíveis */}
        {loading ? (
          <div
            className="text-[10px] text-[#ffe600]/60 text-center py-8"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            CARREGANDO...
          </div>
        ) : (
          <>
            {/* Elegíveis */}
            {elegiveis.length > 0 && (
              <section>
                <h2
                  className="text-[10px] text-[#00ff88] mb-3 flex items-center gap-2"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  <DollarSign size={12} />
                  DISPONÍVEIS ({elegiveis.length})
                </h2>
                <div className="space-y-3">
                  {elegiveis.map((p) => (
                    <PatrocinioCard
                      key={p.id}
                      p={p}
                      assinando={assinando}
                      onAssinar={handleAssinar}
                    />
                  ))}
                </div>
              </section>
            )}

            {/* Bloqueados */}
            {bloqueados.length > 0 && (
              <section>
                <h2
                  className="text-[10px] text-white/30 mb-3 flex items-center gap-2"
                  style={{ fontFamily: 'var(--font-arcade)' }}
                >
                  <Lock size={12} />
                  BLOQUEADOS ({bloqueados.length})
                </h2>
                <div className="space-y-2">
                  {bloqueados.map((p) => (
                    <PatrocinioCard
                      key={p.id}
                      p={p}
                      assinando={assinando}
                      onAssinar={handleAssinar}
                    />
                  ))}
                </div>
              </section>
            )}

            {disponiveis.length === 0 && (
              <div
                className="text-[10px] text-white/30 text-center py-12"
                style={{ fontFamily: 'var(--font-arcade)' }}
              >
                NENHUM PATROCINADOR DISPONÍVEL
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

function PatrocinioCard({
  p,
  assinando,
  onAssinar,
}: {
  p: PatrocinioDisponivel
  assinando: string | null
  onAssinar: (id: string) => void
}) {
  const cor = nivelColor(p.nivel)
  const loading = assinando === p.id

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className={`border p-3 ${
        p.elegivel
          ? 'border-[#ffe600]/50 bg-[#ffe600]/5'
          : 'border-white/10 bg-white/2 opacity-60'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className="text-[10px]"
              style={{ fontFamily: 'var(--font-arcade)', color: cor }}
            >
              {p.nome}
            </span>
            <span
              className="text-[8px] px-1.5 py-0.5 border uppercase"
              style={{
                fontFamily: 'var(--font-arcade)',
                color: cor,
                borderColor: cor + '60',
                background: cor + '15',
              }}
            >
              {p.nivel}
            </span>
          </div>

          {p.descricao && (
            <p className="text-[9px] text-white/50 mt-1 leading-relaxed">{p.descricao}</p>
          )}

          <div className="flex flex-wrap gap-x-4 gap-y-0.5 mt-1.5">
            <span className="text-[9px] text-[#00ff88]">
              R$ {p.valor_semanal?.toLocaleString('pt-BR')}/sem
            </span>
            {p.requisito_ranking > 0 && (
              <span className="text-[9px] text-white/40">
                Req: top {p.requisito_ranking}
              </span>
            )}
          </div>

          {!p.elegivel && p.motivo_bloqueio && (
            <p className="text-[9px] text-[#ff0055]/70 mt-1">⚠ {p.motivo_bloqueio}</p>
          )}
        </div>

        {p.elegivel && (
          <button
            onClick={() => onAssinar(p.id)}
            disabled={!!assinando}
            className="shrink-0 border border-[#ffe600] px-3 py-1.5 text-[8px] text-[#ffe600] hover:bg-[#ffe600]/20 disabled:opacity-40 transition-colors"
            style={{ fontFamily: 'var(--font-arcade)' }}
          >
            {loading ? '...' : 'ASSINAR'}
          </button>
        )}
      </div>
    </motion.div>
  )
}

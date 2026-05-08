import { useEffect, useState } from 'react'
import { Star, DollarSign, TrendingUp } from 'lucide-react'
import { motion } from 'motion/react'
import { ArcadeTab, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

const TABS = ['TREINADOR', 'FISIO', 'PSICÓLOGO', 'MARKETING', 'EMPRESÁRIO']
const CAT_MAP: Record<number, string> = {
  0: 'treinador',
  1: 'fisioterapeuta',
  2: 'psicologo',
  3: 'marketing',
  4: 'empresario',
}

export function MarketScreen() {
  const { jogador, setJogador } = useGameStore()
  const [activeTab, setActiveTab] = useState(0)
  const [profissionais, setProfissionais] = useState<Record<string, any[]>>({})
  const [loading, setLoading] = useState(true)
  const [mensagem, setMensagem] = useState({ texto: '', tipo: 'info' })

  useEffect(() => {
    setLoading(true)
    Promise.all([api.staff.profissionais(), api.jogador.get()])
      .then(([profs, jog]) => {
        setProfissionais(profs)
        setJogador(jog)
      })
      .finally(() => setLoading(false))
  }, [setJogador])

  const categoriaAtual = CAT_MAP[activeTab]
  const lista = profissionais[categoriaAtual] || []
  const contratoAtual =
    categoriaAtual === 'empresario'
      ? jogador?.empresario
      : jogador?.equipe?.find((c: any) => lista.some((prof) => prof.id === c.id))

  async function handleContratar(id: string) {
    try {
      const res = await api.staff.contratar(id)
      setMensagem({ texto: res.mensagem, tipo: 'success' })
    } catch (e: any) {
      setMensagem({ texto: e.message, tipo: 'error' })
    }
  }

  async function handleDemitir(id: string) {
    if (!confirm('Deseja realmente demitir este profissional?')) return
    try {
      const res = await api.staff.demitir(id)
      setMensagem({ texto: res.mensagem, tipo: 'success' })
    } catch (e: any) {
      setMensagem({ texto: e.message, tipo: 'error' })
    }
  }

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="MERCADO DE EQUIPE" color="pink" backTo="/hub">
        <ArcadeTab tabs={TABS} activeTab={activeTab} onChange={setActiveTab} color="pink" />
      </PageHeader>

      <div className="p-4">

      {mensagem.texto && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`mb-4 border-2 p-3 text-center text-[10px] ${
            mensagem.tipo === 'success'
              ? 'border-[#00ff88] bg-[#00ff88]/10 text-[#00ff88]'
              : mensagem.tipo === 'error'
              ? 'border-[#ff0055] bg-[#ff0055]/10 text-[#ff0055]'
              : 'border-[#00e5ff] text-[#00e5ff]'
          }`}
          style={{ fontFamily: 'var(--font-arcade)' }}
        >
          {mensagem.texto.toUpperCase()}
        </motion.div>
      )}

      {loading ? (
        <div className="py-20 text-center pixel-font text-[#00ff88] animate-pulse">CARREGANDO...</div>
      ) : (
        <div className="space-y-3">
          {lista.map((prof, i) => {
            const isContratado = contratoAtual?.id === prof.id
            const outroContratado = contratoAtual && contratoAtual.id !== prof.id

            return (
              <motion.div
                key={prof.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className={`border-2 bg-[#1a1a2e] p-4 ${outroContratado ? 'opacity-40' : ''}`}
                style={{
                  borderColor: isContratado ? '#ffe600' : activeTab % 2 === 0 ? '#00ff88' : '#00e5ff',
                  boxShadow: isContratado ? 'var(--glow-gold)' : activeTab % 2 === 0 ? 'var(--glow-green)' : 'var(--glow-cyan)',
                }}
              >
                <div className="flex items-start gap-3">
                  <div
                    className="flex h-16 w-16 items-center justify-center border-2 bg-black text-3xl"
                    style={{
                      borderColor: isContratado ? '#ffe600' : activeTab % 2 === 0 ? '#00ff88' : '#00e5ff',
                    }}
                  >
                    {String(prof.nome || '?').charAt(0)}
                  </div>

                  <div className="flex-1">
                    <h3
                      className="mb-1 text-[11px]"
                      style={{
                        color: isContratado ? '#ffe600' : activeTab % 2 === 0 ? '#00ff88' : '#00e5ff',
                        fontFamily: 'var(--font-arcade)',
                      }}
                    >
                      {String(prof.nome).toUpperCase()}
                    </h3>
                    <div className="mb-2 text-[8px] text-[#888]">{prof.descricao}</div>

                    <div className="mb-2 flex gap-1">
                      {Array.from({ length: 5 }).map((_, starIdx) => (
                        <Star
                          key={starIdx}
                          size={10}
                          className={starIdx < prof.estrelas ? 'text-[#ffe600]' : 'text-[#555]'}
                          fill={starIdx < prof.estrelas ? '#ffe600' : 'none'}
                        />
                      ))}
                    </div>

                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="mb-1 flex items-center gap-1 text-[10px] text-[#ffe600]">
                          <TrendingUp size={10} />
                          <span>{prof.bonus || 'BONUS DE EQUIPE'}</span>
                        </div>
                        <div className="flex items-center gap-1 text-[9px] text-[#888]">
                          <DollarSign size={10} />
                          <span>{prof.salario_semanal}/SEM</span>
                        </div>
                      </div>

                      {isContratado ? (
                        <button
                          onClick={() => handleDemitir(prof.id)}
                          className="border-2 border-[#ff0055] bg-black px-4 py-2 text-[8px] text-[#ff0055] transition-all hover:bg-[#ff0055] hover:text-black"
                          style={{ fontFamily: 'var(--font-arcade)' }}
                        >
                          DEMITIR
                        </button>
                      ) : (
                        <button
                          onClick={() => handleContratar(prof.id)}
                          disabled={!!outroContratado}
                          className="border-2 border-[#00e5ff] bg-black px-4 py-2 text-[8px] text-[#00e5ff] transition-all enabled:hover:bg-[#00e5ff] enabled:hover:text-black disabled:cursor-not-allowed disabled:opacity-50"
                          style={{ fontFamily: 'var(--font-arcade)' }}
                        >
                          CONTRATAR
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
      </div>
    </div>
  )
}

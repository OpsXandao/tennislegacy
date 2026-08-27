import { useEffect, useState } from 'react'
import { DollarSign, TrendingUp, X, UserCheck } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import {
  ContractConfirmModal,
  EMPTY_EQUIPE,
  SlotAtualPanel,
  SlotVagoPanel,
  Stars,
  TABS,
  TabBar,
  bonusString,
  type ConfirmModal,
  type Equipe,
  type Prof,
} from './MarketScreenComponents'

export function MarketScreen() {
  const { setJogador } = useGameStore()
  const [activeTab, setActiveTab] = useState(0)
  const [profissionais, setProfissionais] = useState<Record<string, Prof[]>>({})
  const [equipe, setEquipe] = useState<Equipe>(EMPTY_EQUIPE)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [mensagem, setMensagem] = useState<{ texto: string; tipo: string } | null>(null)
  const [confirmModal, setConfirmModal] = useState<ConfirmModal | null>(null)

  async function recarregar() {
    const [profs, eq, jog] = await Promise.all([
      api.staff.profissionais(),
      api.staff.equipe(),
      api.jogador.get(),
    ])
    setProfissionais(profs)
    setEquipe(eq)
    setJogador(jog)
  }

  useEffect(() => {
    setLoading(true)
    recarregar().finally(() => setLoading(false))
  }, [])

  const tab = TABS[activeTab]
  const lista: Prof[] = profissionais[tab.cat] ?? []
  const slotAtual = tab.equipeKey ? equipe[tab.equipeKey] : null
  const candidatos = slotAtual
    ? lista.filter(p => p.nome !== slotAtual.nome)
    : lista
  const slotProfNaLista = slotAtual ? lista.find(p => p.nome === slotAtual.nome) : undefined

  const custoSemanal = Object.values(equipe).reduce((t, m) => t + (m?.custo_semanal ?? 0), 0)
  const slotsPreenchidos = Object.values(equipe).filter(Boolean).length
  const filled = TABS.map(t => t.equipeKey ? !!equipe[t.equipeKey] : false)

  async function handleContratar(prof: Prof) {
    setActionLoading(true)
    try {
      const res = await api.staff.contratar(prof.id)
      setMensagem({ texto: res.mensagem, tipo: res.ok ? 'success' : 'error' })
      await recarregar()
    } catch (e: any) {
      setMensagem({ texto: e.message, tipo: 'error' })
    } finally {
      setActionLoading(false)
      setConfirmModal(null)
    }
  }

  async function handleDemitir(prof: Prof) {
    setActionLoading(true)
    try {
      const res = await api.staff.demitir(prof.id)
      setMensagem({ texto: res.mensagem, tipo: res.ok ? 'success' : 'error' })
      await recarregar()
    } catch (e: any) {
      setMensagem({ texto: e.message, tipo: 'error' })
    } finally {
      setActionLoading(false)
      setConfirmModal(null)
    }
  }

  const sorted = [...candidatos].sort((a, b) => b.estrelas - a.estrelas)

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      <PageHeader title="MERCADO DE EQUIPE" color="pink" backTo="/hub">
        {/* Budget summary */}
        {!loading && (
          <div className="flex items-center gap-3 mt-1">
            <span className="arcade-font text-[8px] text-[#555]">
              {slotsPreenchidos}/4 SLOTS
            </span>
            {custoSemanal > 0 && (
              <span className="arcade-font text-[8px] text-neon-yellow">
                R$ {custoSemanal.toLocaleString('pt-BR')}/sem
              </span>
            )}
          </div>
        )}
      </PageHeader>

      {/* Tab bar */}
      <TabBar activeTab={activeTab} onChange={setActiveTab} filled={filled} />

      <div className="p-4">
        {/* Feedback */}
        <AnimatePresence>
          {mensagem && (
            <motion.div
              key="msg"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`mb-4 border-2 p-3 flex items-center justify-between text-[10px] ${
                mensagem.tipo === 'success'
                  ? 'border-neon-green bg-neon-green/10 text-neon-green'
                  : 'border-neon-pink bg-neon-pink/10 text-neon-pink'
              }`}
              style={{ fontFamily: 'var(--font-arcade)' }}
            >
              {mensagem.texto.toUpperCase()}
              <button onClick={() => setMensagem(null)} className="opacity-60 hover:opacity-100">
                <X size={12} />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {loading ? (
          <div className="py-20 text-center pixel-font animate-pulse" style={{ color: tab.cor }}>
            CARREGANDO...
          </div>
        ) : (
          <>
            {/* Slot atual */}
            {slotAtual ? (
              <SlotAtualPanel
                membro={slotAtual}
                cor={tab.cor}
                cargo={tab.label}
                profNaLista={slotProfNaLista}
                onDemitir={(prof) => setConfirmModal({ tipo: 'demitir', prof })}
              />
            ) : (
              <SlotVagoPanel cor={tab.cor} />
            )}

            {/* Rótulo de candidatos */}
            {sorted.length > 0 && (
              <div className="arcade-font text-[8px] tracking-widest mb-3" style={{ color: tab.cor + '88' }}>
                {slotAtual ? 'ALTERNATIVAS DISPONÍVEIS' : 'DISPONÍVEIS NO MERCADO'} ({sorted.length})
              </div>
            )}

            {/* Lista de candidatos */}
            <div className="space-y-3">
              {sorted.map((prof, i) => {
                const linhas = bonusString(prof.bonus)

                return (
                  <motion.div
                    key={prof.id}
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="border bg-[#08090f] p-4"
                    style={{ borderColor: tab.cor + '33' }}
                  >
                    <div className="flex items-start gap-3">
                      {/* Avatar */}
                      <div
                        className="shrink-0 w-12 h-12 flex items-center justify-center border arcade-font text-[13px]"
                        style={{ borderColor: tab.cor + '55', color: tab.cor, background: tab.cor + '0d' }}
                      >
                        {prof.nome.charAt(0).toUpperCase()}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="arcade-font text-[10px] text-white mb-1 truncate">
                          {prof.nome.toUpperCase()}
                        </div>

                        {prof.descricao && (
                          <div className="arcade-font text-[8px] text-[#555] leading-relaxed mb-1.5">
                            {prof.descricao}
                          </div>
                        )}

                        {/* Stars + salary inline */}
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <Stars count={prof.estrelas} size={9} />
                          <div className="flex items-center gap-1 arcade-font text-[9px] text-[#666]">
                            <DollarSign size={9} />
                            R$ {prof.salario_semanal.toLocaleString('pt-BR')}/sem
                          </div>
                        </div>

                        {/* Comparação de estrelas com o slot atual */}
                        {slotAtual && (
                          <div className="arcade-font text-[7px] mb-2" style={{
                            color: prof.estrelas > slotAtual.nivel
                              ? 'var(--neon-green)'
                              : prof.estrelas < slotAtual.nivel
                              ? 'var(--neon-pink)'
                              : '#555',
                          }}>
                            {prof.estrelas > slotAtual.nivel
                              ? `▲ ${prof.estrelas - slotAtual.nivel} estrela(s) melhor`
                              : prof.estrelas < slotAtual.nivel
                              ? `▼ ${slotAtual.nivel - prof.estrelas} estrela(s) pior`
                              : '= Mesmo nível do atual'}
                          </div>
                        )}

                        <div className="flex flex-wrap gap-1.5 mb-2">
                          {typeof prof.surface_fit === 'number' && (
                            <span className="border border-neon-cyan/40 px-1.5 py-0.5 arcade-font text-[7px] text-neon-cyan">
                              FIT {prof.surface_fit}
                            </span>
                          )}
                          {typeof prof.contrato_semanas === 'number' && prof.contrato_semanas > 0 && (
                            <span className="border border-white/20 px-1.5 py-0.5 arcade-font text-[7px] text-[#bbb]">
                              {prof.contrato_semanas} SEMANAS
                            </span>
                          )}
                        </div>

                        {/* Bonus lines */}
                        {linhas.length > 0 && (
                          <div className="space-y-0.5 mb-2">
                            {linhas.map((l, j) => (
                              <div key={j} className="arcade-font text-[8px] flex items-center gap-1" style={{ color: tab.cor + 'aa' }}>
                                <TrendingUp size={8} />{l}
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Ação */}
                        <div className="flex justify-end">
                          <button
                            onClick={() => setConfirmModal({ tipo: 'contratar', prof })}
                            disabled={actionLoading}
                            className="flex items-center gap-1.5 border px-3 py-1.5 arcade-font text-[8px] hover:opacity-80 disabled:opacity-40 transition-opacity"
                            style={{ borderColor: tab.cor, color: tab.cor }}
                          >
                            <UserCheck size={10} />
                            {slotAtual ? 'SUBSTITUIR' : 'CONTRATAR'}
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}

              {sorted.length === 0 && (
                <div className="py-12 text-center arcade-font text-[9px] text-[#333]">
                  NENHUM CANDIDATO DISPONÍVEL
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <AnimatePresence>
        {confirmModal && (
          <ContractConfirmModal
            modal={confirmModal}
            onConfirm={() =>
              confirmModal.tipo === 'demitir'
                ? handleDemitir(confirmModal.prof)
                : handleContratar(confirmModal.prof)
            }
            onCancel={() => setConfirmModal(null)}
            loading={actionLoading}
            accentColor={tab.cor}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

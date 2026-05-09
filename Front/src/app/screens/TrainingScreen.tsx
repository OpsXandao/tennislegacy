import { useState, useEffect } from 'react'
import { Dumbbell, Zap, Brain, Target } from 'lucide-react'
import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router'
import { NeonCard, PixelBar, NeonButton, PageHeader, BottomNav } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

interface TreinoOpcao {
  id: string
  nome: string
  descricao: string
  custo_energia: number
}

export function TrainingScreen() {
  const navigate = useNavigate()
  const { jogador, setJogador, setSemana, ano, semana } = useGameStore()
  const [opcoes, setOpcoes] = useState<TreinoOpcao[]>([])
  const [loading, setLoading] = useState(false)
  const [treinando, setTreinando] = useState(false)
  const [melhorias, setMelhorias] = useState<Record<string, number> | null>(null)
  const [erro, setErro] = useState('')
  const [descansando, setDescansando] = useState(false)
  const [aviso, setAviso] = useState('')

  useEffect(() => {
    api.treinamento.opcoes()
      .then(res => setOpcoes(res.opcoes))
      .catch(() => setErro('Erro ao carregar opções de treino.'))
  }, [])

  function _navegarWeekAdvance(res: any, motivo: 'treino' | 'descanso', melhoriasList?: Record<string, number>) {
    if (res.jogador_status) setJogador({ ...jogador, ...res.jogador_status } as any)
    const toSemana = res.semana ?? semana + 1
    const toAno = res.ano ?? ano
    setSemana(toSemana, toAno)
    const eventosTreino = melhoriasList && Object.keys(melhoriasList).length > 0
      ? Object.entries(melhoriasList).map(([attr, val]) => `📈 ${attr.toUpperCase()} +${val}`)
      : []
    const eventosApi: string[] = res.eventos ?? []
    navigate('/week-advance', {
      replace: true,
      state: {
        fromSemana: semana,
        fromAno: ano,
        toSemana,
        toAno,
        campeoes: res.resumo_mundial?.campeoes ?? [],
        eventos: [...eventosTreino, ...eventosApi],
        motivo,
      },
    })
  }

  async function handleTreinar(focoId: string) {
    if (treinando) return
    setErro('')
    setAviso('')
    setMelhorias(null)
    setTreinando(true)

    try {
      const res = await api.treinamento.executar(focoId)
      if (res.ok) {
        _navegarWeekAdvance(res, 'treino', res.melhorias)
      }
    } catch (e: any) {
      setErro(e.message || 'Falha no treinamento.')
      setTreinando(false)
    }
  }

  async function handleDescansar() {
    if (descansando) return
    setErro('')
    setAviso('')
    setMelhorias(null)
    setDescansando(true)
    try {
      const res = await api.treinamento.descanso()
      _navegarWeekAdvance(res, 'descanso')
    } catch (e: any) {
      setErro(e.message || 'Falha ao descansar.')
      setDescansando(false)
    }
  }

  const energia = jogador?.energia ?? 0
  const fadiga = jogador?.fadiga ?? 0

  return (
    <div className="app-shell min-h-screen flex flex-col">
      <PageHeader title="ACADEMIA" color="green" backTo="/hub" />

      <div className="flex-1 p-4 space-y-6 overflow-y-auto pb-24">
        {/* Status do Jogador */}
        <NeonCard variant="cyan" hover={false}>
          <div className="grid grid-cols-2 gap-4">
            <PixelBar value={energia} variant="green" label="ENERGIA" showValue />
            <PixelBar value={fadiga} variant="pink" label="FADIGA" showValue />
          </div>
        </NeonCard>

        {/* Mensagens de Feedback */}
        <AnimatePresence>
          {melhorias && Object.keys(melhorias).length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="bg-neon-green/20 border-2 border-neon-green p-3 text-center"
            >
              <div className="arcade-font text-[10px] text-neon-green mb-2 uppercase font-bold">
                EVOLUÇÃO CONCLUÍDA!
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {Object.entries(melhorias).map(([attr, valor]) => (
                  <span key={attr} className="arcade-font text-[9px] text-white bg-black/40 px-2 py-1">
                    {attr.toUpperCase()}: {valor}
                  </span>
                ))}
              </div>
            </motion.div>
          )}
          {melhorias && Object.keys(melhorias).length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="arcade-font text-[10px] text-[#888] text-center"
            >
              Treino finalizado, mas nenhum atributo subiu desta vez.
            </motion.div>
          )}
          {erro && (
            <motion.div className="arcade-font text-[10px] text-neon-pink text-center border border-neon-pink p-2">
              {erro}
            </motion.div>
          )}
          {aviso && (
            <motion.div className="arcade-font text-[10px] text-neon-green text-center border border-neon-green p-2">
              {aviso}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Opções de Treino */}
        <div className="space-y-4">
          {opcoes.map((opcao) => (
            <NeonCard 
              key={opcao.id} 
              variant={opcao.id === 'psicologico' ? 'yellow' : 'green'}
              className={treinando ? 'opacity-50 pointer-events-none' : ''}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  {opcao.id === 'tecnico' && <Target className="text-neon-green" size={20} />}
                  {opcao.id === 'fisico' && <Dumbbell className="text-neon-cyan" size={20} />}
                  {opcao.id === 'psicologico' && <Brain className="text-neon-yellow" size={20} />}
                  <span className="pixel-font text-sm text-white">{opcao.nome.toUpperCase()}</span>
                </div>
                <div className="flex items-center gap-1 text-neon-pink">
                  <Zap size={12} fill="currentColor" />
                  <span className="arcade-font text-[10px]">-{opcao.custo_energia}</span>
                </div>
              </div>
              <p className="arcade-font text-[9px] text-[#888] mb-4 leading-tight">
                {opcao.descricao}
              </p>
              <NeonButton 
                variant={opcao.id === 'psicologico' ? 'yellow' : 'cyan'} 
                className="w-full py-2 text-[10px]"
                onClick={() => handleTreinar(opcao.id)}
                blink={treinando}
              >
                TREINAR AGORA
              </NeonButton>
            </NeonCard>
          ))}
        </div>

        <NeonCard variant="pink" hover={false}>
          <div className="mb-3 arcade-font text-[10px] text-neon-pink uppercase">Recuperação</div>
          <p className="mb-4 arcade-font text-[9px] text-[#888] leading-tight">
            Pule a semana para recuperar energia e reduzir fadiga.
          </p>
          <NeonButton variant="pink" className="w-full py-2 text-[10px]" onClick={handleDescansar} blink={descansando}>
            {descansando ? 'DESCANSANDO...' : 'DESCANSAR E AVANCAR'}
          </NeonButton>
        </NeonCard>
      </div>

      {/* Overlay de animação de treino */}
      <AnimatePresence>
        {(treinando || descansando) && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/90 flex flex-col items-center justify-center"
          >
            <div className="relative">
              <Dumbbell className="text-neon-green w-24 h-24 animate-bounce" />
              <motion.div 
                animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="absolute inset-0 bg-neon-green/20 blur-3xl rounded-full"
              />
            </div>
            <div className="pixel-font text-neon-green mt-8 text-xl tracking-widest animate-pulse">
              {treinando ? 'TREINANDO...' : 'RECUPERANDO...'}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

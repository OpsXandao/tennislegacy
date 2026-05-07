import { useEffect, useState } from 'react'
import { Shield, Swords, AlertTriangle, Trophy, Play, SkipForward } from 'lucide-react'
import { NeonButton, NeonCard, PageHeader, PixelFlag } from '../components'
import { api } from '../../api/client'
import { useNavigate } from 'react-router'
import { useGameStore } from '../../store/gameStore'

interface DavisState {
  nome: string
  tipo: string
  fase_atual: string
  jogador_ativo: boolean
  jogador_convocado: boolean
  partida_disponivel: boolean
  info_partida?: any
  confronto_atual?: any
  estado: any
}

export function DavisScreen() {
  const navigate = useNavigate()
  const { setPartidaId } = useGameStore()
  const [data, setData] = useState<DavisState | null>(null)
  const [loading, setLoading] = useState(true)
  const [simulando, setSimulando] = useState(false)
  const [status, setStatus] = useState('')

  async function carregar() {
    setLoading(true)
    try {
      const estado = await api.davis.estado()
      setData(estado as any)
      setStatus('')
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Falha ao carregar confronto nacional.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregar()
  }, [])

  async function handleSimular() {
    setSimulando(true)
    try {
      await api.davis.simular()
      await carregar()
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Falha ao simular.')
    } finally {
      setSimulando(false)
    }
  }

  async function handleJogar() {
    try {
      const ativa = await api.partida.ativa()
      if (ativa?.partida_id) {
        setPartidaId(ativa.partida_id)
      } else {
        setPartidaId(null)
      }
      navigate('/match')
    } catch {
      setPartidaId(null)
      navigate('/match')
    }
  }

  if (loading) {
    return (
      <div className="app-shell min-h-screen flex items-center justify-center">
        <div className="pixel-font text-[#ffe600] animate-pulse">SINCRONIZANDO COM A FEDERAÇÃO...</div>
      </div>
    )
  }

  const confronto = data?.confronto_atual || {}
  const rawA = confronto.equipe_a || '??'
  const rawB = confronto.equipe_b || '??'
  
  // Função auxiliar para extrair código [BR] de "[BR] Brasil"
  const extractCode = (name: string) => {
    const match = name.match(/\[(.*?)\]/)
    return match ? match[1] : name
  }
  
  const cleanName = (name: string) => {
    return name.replace(/\[.*?\]\s*/, '').toUpperCase()
  }

  const equipeA = extractCode(rawA)
  const equipeB = extractCode(rawB)
  const labelA = cleanName(rawA)
  const labelB = cleanName(rawB)
  
  const placarTie = confronto.placar_tie || [0, 0]
  const partidas = confronto.partidas || []

  return (
    <div className="app-shell min-h-screen pb-24">
      <PageHeader
        title={data?.nome || 'DAVIS CUP'}
        subtitle={data?.fase_atual.toUpperCase()}
        color="yellow"
        backTo="/hub"
      />

      <div className="p-4 max-w-md mx-auto space-y-6">
        {/* Placar do Tie */}
        <NeonCard variant="yellow" hover={false}>
          <div className="flex justify-around items-center py-4">
            <div className="text-center">
              <PixelFlag countryCode={equipeA} size="lg" className="mx-auto mb-2" />
              <div className="arcade-font text-[10px] text-white">{labelA}</div>
            </div>
            
            <div className="text-center">
              <div className="pixel-font text-3xl text-[#ffe600]">
                {placarTie[0]} - {placarTie[1]}
              </div>
              <div className="arcade-font text-[8px] text-[#666] mt-1">PLACAR TIE</div>
            </div>

            <div className="text-center">
              <PixelFlag countryCode={equipeB} size="lg" className="mx-auto mb-2" />
              <div className="arcade-font text-[10px] text-white">{labelB}</div>
            </div>
          </div>
        </NeonCard>

        {/* Lista de Partidas */}
        <div className="space-y-3">
          <div className="arcade-font text-[8px] text-[#444] tracking-widest px-1">HISTÓRICO DO CONFRONTO</div>
          {partidas.length === 0 && (
            <div className="text-center py-8 arcade-font text-[10px] text-[#333] border-2 border-dashed border-[#333]">
              NENHUMA PARTIDA DISPUTADA AINDA
            </div>
          )}
          {partidas.map((p: any, i: number) => (
            <div key={i} className="bg-[#111] border-2 border-[#333] p-3 flex justify-between items-center">
              <div className="flex-1">
                <div className="arcade-font text-[9px] text-white truncate">{p.jogador_a}</div>
                <div className="arcade-font text-[9px] text-white truncate mt-1">{p.jogador_b}</div>
              </div>
              <div className="text-right ml-4">
                <div className="pixel-font text-xs text-[#ffe600]">{p.placar}</div>
                <div className="arcade-font text-[7px] text-[#00ff88] mt-1">{p.vencedor.toUpperCase()}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Notificações/Status */}
        {status && (
          <div className="p-3 bg-[#ff0055]/10 border-2 border-[#ff0055] arcade-font text-[9px] text-[#ff0055]">
            {status.toUpperCase()}
          </div>
        )}
      </div>

      {/* Controles Fixos */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-black/80 backdrop-blur-md border-t-2 border-[#ffe600]/20">
        <div className="max-w-md mx-auto space-y-3">
          {data?.partida_disponivel ? (
            <NeonButton variant="yellow" className="w-full py-4" onClick={handleJogar} blink>
              <Play size={20} className="mr-2 inline" /> JOGAR MINHA PARTIDA
            </NeonButton>
          ) : (
            <NeonButton 
              variant="green" 
              className="w-full py-4" 
              onClick={handleSimular} 
              disabled={simulando || !data?.jogador_ativo}
              blink={simulando}
            >
              <SkipForward size={20} className="mr-2 inline" /> 
              {simulando ? 'SIMULANDO...' : 'SIMULAR PARTIDAS DOS BOTS'}
            </NeonButton>
          )}
        </div>
      </div>
    </div>
  )
}

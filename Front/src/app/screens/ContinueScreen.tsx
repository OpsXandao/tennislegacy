import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useLocation, useNavigate } from 'react-router'
import { CheckSquare, Square, Trash2 } from 'lucide-react'
import { NeonCard, NeonButton, PageHeader } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'
import type { SavePreview } from '../../types'

export function ContinueScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const { setSaveAtivo, setJogador, setSemana, setTorneio, reset } = useGameStore()
  const deleteMode = new URLSearchParams(location.search).get('mode') === 'delete'

  const [saves, setSaves] = useState<string[]>([])
  const [previews, setPreviews] = useState<Record<string, SavePreview>>({})
  const [loading, setLoading] = useState(true)
  const [carregando, setCarregando] = useState<string | null>(null)
  const [apagando, setApagando] = useState<string | null>(null)
  const [selecionados, setSelecionados] = useState<string[]>([])
  const [erro, setErro] = useState('')

  async function carregarSaves() {
    setLoading(true)
    setErro('')
    try {
      const r = await api.saves.listar()
      setSaves(r.saves)
      const results = await Promise.allSettled(
        r.saves.map((nome) => api.saves.preview(nome).then((p) => ({ nome, p })))
      )
      const map: Record<string, SavePreview> = {}
      for (const res of results) {
        if (res.status === 'fulfilled') map[res.value.nome] = res.value.p
      }
      setPreviews(map)
      setSelecionados((atual) => atual.filter((nome) => r.saves.includes(nome)))
    } catch {
      setErro('Erro ao listar saves. Backend rodando?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregarSaves()
  }, [])

  async function handleApagar(nome: string) {
    const confirmar = window.confirm(`Apagar o save "${nome}"? Essa ação não pode ser desfeita.`)
    if (!confirmar) return
    setApagando(nome)
    setErro('')
    api.saves
      .deletar(nome)
      .then(async () => {
        await carregarSaves()
      })
      .catch(() => setErro(`Erro ao apagar "${nome}".`))
      .finally(() => setApagando(null))
  }

  function toggleSelecionado(nome: string) {
    setSelecionados((atual) =>
      atual.includes(nome) ? atual.filter((item) => item !== nome) : [...atual, nome]
    )
  }

  async function handleApagarSelecionados() {
    if (selecionados.length === 0) return
    const confirmar = window.confirm(
      `Apagar ${selecionados.length} save(s) selecionado(s)? Essa ação não pode ser desfeita.`
    )
    if (!confirmar) return
    setErro('')
    for (const nome of selecionados) {
      setApagando(nome)
      try {
        await api.saves.deletar(nome)
      } catch {
        setErro(`Erro ao apagar "${nome}".`)
        break
      }
    }
    setApagando(null)
    await carregarSaves()
  }

  async function handleCarregar(nome: string) {
    setCarregando(nome)
    setErro('')
    try {
      const r = await api.saves.carregar(nome)
      if (!r.ok) { setErro(`Erro ao carregar "${nome}".`); return }
      reset()
      setSaveAtivo(nome)
      setJogador(r.jogador)
      setSemana(r.semana, r.ano)
      setTorneio(r.torneio ?? null)
      navigate('/hub')
    } catch {
      setErro('Falha de conexão com o servidor.')
    } finally {
      setCarregando(null)
    }
  }

  return (
    <div className="min-h-screen">
      <PageHeader title="CARREGAR" subtitle="SELECIONE UM SAVE" color="green" backTo="/" />

      <div className="p-4 space-y-4">
        {deleteMode && (
          <NeonCard variant="pink" hover={false}>
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="pixel-font text-sm text-neon-pink">MODO APAGAR</div>
                <div className="arcade-font text-xs text-[#888]">
                  Clique nos saves para selecionar e apagar sem carregar
                </div>
              </div>
              <NeonButton
                variant="pink"
                className="shrink-0"
                onClick={handleApagarSelecionados}
                disabled={selecionados.length === 0 || !!apagando}
              >
                APAGAR {selecionados.length > 0 ? `(${selecionados.length})` : ''}
              </NeonButton>
            </div>
          </NeonCard>
        )}

        {loading && (
          <div className="text-center py-12">
            <motion.div
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="pixel-font text-sm text-neon-green"
            >
              CARREGANDO...
            </motion.div>
          </div>
        )}

        {!loading && saves.length === 0 && !erro && (
          <NeonCard variant="cyan" hover={false}>
            <div className="text-center py-8">
              <div className="pixel-font text-4xl mb-4">💤</div>
              <div className="arcade-font text-sm text-[#888]">
                Nenhum save encontrado
              </div>
              <div className="arcade-font text-xs text-[#444] mt-2">
                Inicie um novo jogo na tela inicial
              </div>
            </div>
          </NeonCard>
        )}

        {!loading &&
          saves.map((nome, index) => (
            <motion.div
              key={nome}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.08 }}
            >
              <NeonCard
                variant="green"
                onClick={() => (deleteMode ? toggleSelecionado(nome) : handleCarregar(nome))}
                className="relative"
              >
                <div className="absolute top-2 right-12 pixel-font text-xs text-[#888]">
                  SLOT {index + 1}
                </div>
                {deleteMode ? (
                  <div className="absolute right-2 top-2 text-neon-pink">
                    {selecionados.includes(nome) ? <CheckSquare size={14} /> : <Square size={14} />}
                  </div>
                ) : (
                  <button
                    type="button"
                    aria-label={`Apagar save ${nome}`}
                    className="absolute right-2 top-2 border border-neon-pink p-1 text-neon-pink transition-colors hover:bg-neon-pink/10 disabled:opacity-50"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleApagar(nome)
                    }}
                    disabled={apagando === nome || carregando === nome}
                  >
                    <Trash2 size={12} />
                  </button>
                )}

                <div className="mb-2">
                  <div className="pixel-font text-xl text-neon-green">{nome}</div>
                </div>

                {previews[nome] ? (
                  <div className="grid grid-cols-3 gap-2 mt-2 mb-3">
                    <div>
                      <div className="arcade-font text-xs text-[#888]">JOGADOR</div>
                      <div className="arcade-font text-xs text-white truncate">
                        {previews[nome].jogador_nome}
                      </div>
                    </div>
                    <div>
                      <div className="arcade-font text-xs text-[#888]">TOUR</div>
                      <div className="arcade-font text-xs text-neon-cyan uppercase">
                        {previews[nome].tour}
                      </div>
                    </div>
                    <div>
                      <div className="arcade-font text-xs text-[#888]">SEMANA</div>
                      <div className="arcade-font text-xs text-neon-yellow">
                        {previews[nome].semana}/52
                      </div>
                    </div>
                  </div>
                ) : null}

                <div className="mt-2 text-center">
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="arcade-font text-xs text-neon-green"
                  >
                    {apagando === nome
                      ? '✖ APAGANDO...'
                      : deleteMode
                      ? selecionados.includes(nome)
                        ? '☑ SELECIONADO PARA APAGAR'
                        : '☐ TOQUE PARA SELECIONAR'
                      : carregando === nome
                      ? '▶ CARREGANDO...'
                      : '▶ TOQUE PARA CONTINUAR'}
                  </motion.div>
                </div>
              </NeonCard>
            </motion.div>
          ))}

        {erro && (
          <div className="text-center arcade-font text-xs text-neon-pink py-4">
            {erro}
          </div>
        )}

        <NeonButton
          variant="pink"
          className="w-full"
          onClick={() => navigate('/')}
        >
          {deleteMode ? 'CANCELAR' : 'VOLTAR'}
        </NeonButton>
      </div>
    </div>
  )
}

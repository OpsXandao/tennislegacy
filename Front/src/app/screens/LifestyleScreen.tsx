import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { ArrowLeft, Crown, CheckCircle2, ShoppingCart } from 'lucide-react'
import { PageHeader, NeonButton } from '../components'
import { api } from '../../api/client'
import { useGameStore } from '../../store/gameStore'

export function LifestyleScreen() {
  const navigate = useNavigate()
  const { jogador, fetchJogador } = useGameStore()
  const [itens, setItens] = useState<Record<string, any[]>>({})
  const [loading, setLoading] = useState(true)
  const [buying, setBuying] = useState<string | null>(null)
  const [mensagem, setMensagem] = useState<{ texto: string; tipo: 'success' | 'error' } | null>(null)

  const carregar = async () => {
    try {
      const data = await api.lifestyle.itens()
      setItens(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    carregar()
  }, [])

  const handleComprar = async (itemId: string) => {
    setBuying(itemId)
    setMensagem(null)
    try {
      const res = await api.lifestyle.comprar(itemId)
      if (res.ok) {
        setMensagem({ texto: res.mensagem, tipo: 'success' })
        await fetchJogador()
        await carregar()
      }
    } catch (e: any) {
      setMensagem({ texto: e.message || 'Erro ao comprar item.', tipo: 'error' })
    } finally {
      setBuying(null)
    }
  }

  const fmtMoney = (v: number) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v)
  }

  return (
    <div className="app-shell flex flex-col min-h-screen bg-[#050505]">
      <PageHeader title="LIFESTYLE & INVESTIMENTOS" color="pink" backTo="/hub">
        <div className="flex items-center gap-2 px-2 py-1 bg-[#ffb7c61a] border border-[#ffb7c633]">
          <span className="text-[10px] text-[#ffb7c6] arcade-font">SALDO: {fmtMoney(jogador?.dinheiro ?? 0)}</span>
        </div>
      </PageHeader>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-24">
        {mensagem && (
          <div className={`p-3 border-2 arcade-font text-[10px] ${mensagem.tipo === 'success' ? 'border-[#00ff88] bg-[#00ff881a] text-[#00ff88]' : 'border-[#ff0055] bg-[#ff00551a] text-[#ff0055]'}`}>
            {mensagem.texto.toUpperCase()}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12 arcade-font text-[#444] text-[10px] animate-pulse">CARREGANDO ITENS...</div>
        ) : (
          Object.entries(itens).map(([categoria, lista]) => (
            <div key={categoria} className="space-y-3">
              <div className="flex items-center gap-2 border-b border-white/10 pb-1">
                <Crown size={14} className="text-[#ffb7c6]" />
                <h2 className="arcade-font text-[12px] text-white tracking-widest uppercase">{categoria.replace('_', ' ')}</h2>
              </div>

              <div className="grid gap-3">
                {lista.map((item) => (
                  <div 
                    key={item.id} 
                    className={`app-panel p-4 border-2 transition-all ${item.comprado ? 'border-[#00ff8833] bg-[#00ff8805]' : 'border-[#333] bg-[#111]'}`}
                  >
                    <div className="flex justify-between items-start gap-4">
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`arcade-font text-[12px] ${item.comprado ? 'text-[#00ff88]' : 'text-white'}`}>{item.nome.toUpperCase()}</span>
                          {item.comprado && <CheckCircle2 size={12} className="text-[#00ff88]" />}
                        </div>
                        <p className="text-[9px] text-[#9fb0bf] leading-relaxed italic">{item.descricao}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="arcade-font text-[12px] text-[#ffb7c6] mb-2">{fmtMoney(item.preco)}</div>
                        <NeonButton
                          variant={item.comprado ? 'green' : 'pink'}
                          disabled={item.comprado || !item.pode_comprar || buying !== null}
                          onClick={() => handleComprar(item.id)}
                          className="!px-3 !py-1.5 !min-h-0"
                        >
                          <div className="flex items-center gap-2 text-[8px]">
                            {item.comprado ? 'ADQUIRIDO' : buying === item.id ? 'PROCESSANDO...' : 'COMPRAR'}
                            {!item.comprado && <ShoppingCart size={10} />}
                          </div>
                        </NeonButton>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer deco */}
      <div className="fixed bottom-0 left-0 w-full h-16 pointer-events-none bg-gradient-to-t from-black to-transparent z-10" />
    </div>
  )
}

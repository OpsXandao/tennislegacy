import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { motion, AnimatePresence } from 'motion/react'
import {
  Settings, Save, LogOut, ChevronRight,
  Globe, ShoppingBag, Shield, Users, History, CalendarDays, Play,
} from 'lucide-react'
import { FutCard, BottomNav } from '../components'
import { useGameStore } from '../../store/gameStore'
import { api } from '../../api/client'
import { useTheme } from '../hooks/useTheme'

const MATCH_AUTOSAVE_KEY = 'tennislegacy.match.autosave'

function fmt(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`
  return `$${v}`
}

function PixelMeter({ value, color }: { value: number; color: string }) {
  const blocks = 12
  const filled = Math.round((Math.min(100, Math.max(0, value)) / 100) * blocks)
  return (
    <div className="flex gap-[2px]">
      {Array.from({ length: blocks }).map((_, i) => (
        <div
          key={i}
          className="flex-1 h-[8px]"
          style={{
            background: i < filled ? color : 'var(--muted, #1a1a1a)',
            boxShadow: i < filled && i === filled - 1 ? `0 0 6px ${color}` : 'none',
          }}
        />
      ))}
    </div>
  )
}

const QUICK = [
  { icon: CalendarDays, label: 'JOGAR',    route: '/calendar', color: '#00ff88' },
  { icon: ShoppingBag,  label: 'MERCADO',  route: '/market',   color: '#ff0055' },
  { icon: Users,        label: 'DUPLAS',   route: '/duplas',   color: '#00e5ff' },
  { icon: Shield,       label: 'DAVIS',    route: '/davis',    color: '#ffe600' },
  { icon: History,      label: 'HISTORICO',route: '/history',  color: '#ffe600' },
  { icon: Globe,        label: 'MUNDO',    route: '/world',    color: '#ffe600' },
]

function QuickBtn({ item, onClick }: { item: typeof QUICK[number]; onClick: () => void }) {
  const [hovered, setHovered] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="flex items-center gap-2 p-3 border-2 active:scale-95 transition-all text-left"
      style={{
        borderColor: hovered ? item.color : `${item.color}33`,
        background: hovered ? `${item.color}0d` : 'var(--card)',
        boxShadow: hovered ? `0 0 10px ${item.color}44` : 'none',
        transition: 'border-color 0.15s, background 0.15s, box-shadow 0.15s',
      }}
    >
      <item.icon size={15} style={{ color: item.color, flexShrink: 0 }} />
      <span
        className="text-[9px] truncate"
        style={{ fontFamily: 'var(--font-pixel)', color: hovered ? item.color : '#444' }}
      >
        {item.label}
      </span>
    </button>
  )
}

export function HubScreen() {
  const navigate  = useNavigate()
  const { jogador, semana, ano, setJogador, fetchJogador, torneio, reset } = useGameStore()
  const [saving, setSaving]   = useState(false)
  const [saveMsg, setSaveMsg] = useState('')
  const [mostrarPromptAutoSave, setMostrarPromptAutoSave] = useState(false)
  const [unreadEmails, setUnreadEmails] = useState(0)
  const [loadError, setLoadError] = useState(false)

  const [hoveringConfig, setHoveringConfig] = useState(false)
  const [hoveringSave, setHoveringSave] = useState(false)
  const [hoveringExit, setHoveringExit] = useState(false)
  const [hoveringActiveTournament, setHoveringActiveTournament] = useState(false)
  const [hoveringNextStep, setHoveringNextStep] = useState(false)

  useEffect(() => {
    fetchJogador().catch(() => { setLoadError(true) })
    api.email.unreadCount().then(res => setUnreadEmails(res.unread_count || 0)).catch(() => {})
    if (typeof window !== 'undefined' && window.localStorage.getItem(MATCH_AUTOSAVE_KEY) === null) {
      setMostrarPromptAutoSave(true)
    }
  }, [])

  const { isLight } = useTheme()
  const nome      = jogador?.nome      ?? '...'
  const rank      = jogador?.ranking   ?? 0
  const money     = jogador?.dinheiro  ?? 0
  const energia   = jogador?.energia   ?? 0
  const fadiga    = jogador?.fadiga    ?? 0
  const overall   = jogador?.overall   ?? 0
  const tour      = (jogador?.tour     ?? 'atp') as 'atp' | 'wta'
  const isAtp     = tour === 'atp'
  const accent    = isAtp ? '#00ff88' : '#ff0055'
  const accentVar = isAtp ? 'var(--neon-green)' : 'var(--neon-pink)'
  const glowVar   = isAtp ? 'var(--glow-green-sm)' : 'var(--glow-pink-sm)'
  const lesionado = !!jogador?.status_lesao

  async function handleSalvar() {
    setSaving(true)
    setSaveMsg('')
    try {
      const r = await api.saves.salvar()
      if (r.ok) setSaveMsg('SALVO')
    } catch {
      setSaveMsg('ERRO')
    } finally {
      setSaving(false)
      setTimeout(() => setSaveMsg(''), 2500)
    }
  }

  function definirAutoSave(ativo: boolean) {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(MATCH_AUTOSAVE_KEY, String(ativo))
    }
    setMostrarPromptAutoSave(false)
  }

  return (
    <div className="app-shell min-h-screen overflow-y-auto pb-28">
      {loadError && (
        <div className="flex items-center justify-between gap-3 bg-[#1a0008] border-b-2 border-[#ff0055] px-4 py-2">
          <span className="arcade-font text-[10px] text-[#ff0055] tracking-wider">ERRO AO CARREGAR DADOS — SERVIDOR OFFLINE?</span>
          <button
            type="button"
            onClick={() => { setLoadError(false); fetchJogador().catch(() => setLoadError(true)) }}
            className="arcade-font text-[10px] text-[#ff7d9e] border border-[#ff0055] px-2 py-1"
          >
            TENTAR NOVAMENTE
          </button>
        </div>
      )}
      {mostrarPromptAutoSave && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/82 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md border-2 border-[#00ff88] bg-[#06110c] p-5 shadow-[0_0_24px_rgba(0,255,136,0.18)]">
            <div className="arcade-font text-[10px] tracking-[0.2em] text-[#00ff88]">SALVAMENTO AUTOMÁTICO</div>
            <div className="pixel-font mt-3 text-lg text-white">Deseja ativar o salvamento automático?</div>
            <div className="arcade-font mt-3 text-[11px] leading-relaxed text-[#9bc7af]">
              Essa configuração é definida no hub e usada quando uma nova partida começar.
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => definirAutoSave(false)}
                className="min-h-[44px] border-2 border-[#ff0055] px-4 py-3 arcade-font text-[10px] text-[#ff7d9e]"
              >
                NÃO
              </button>
              <button
                type="button"
                onClick={() => definirAutoSave(true)}
                className="min-h-[44px] border-2 border-[#00ff88] px-4 py-3 arcade-font text-[10px] text-[#00ff88]"
              >
                SIM
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top bar */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b-2 border-[#00ff88]"
        style={{ boxShadow: '0 2px 12px rgba(0,255,136,0.12)' }}
      >
        <div>
          <div
            className="text-[10px] text-[#00ff88]"
            style={{ fontFamily: 'var(--font-pixel)', textShadow: '0 0 6px #00ff88' }}
          >
            TENNIS LEGACY
          </div>
          <div className="text-[9px] text-[#555] mt-0.5" style={{ fontFamily: 'var(--font-arcade)' }}>
            TEMPORADA {ano} | SEMANA {semana}/52
          </div>
        </div>
        <div className="flex items-center gap-1">
          <AnimatePresence>
            {saveMsg && (
              <motion.span
                initial={{ opacity: 0, x: 6 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="text-[9px] mr-2"
                style={{
                  fontFamily: 'var(--font-pixel)',
                  color: saveMsg === 'SALVO' ? '#00ff88' : '#ff0055',
                  textShadow: `0 0 6px ${saveMsg === 'SALVO' ? '#00ff88' : '#ff0055'}`,
                }}
              >
                {saveMsg}
              </motion.span>
            )}
          </AnimatePresence>
          <button
            onClick={() => navigate('/settings')}
            onMouseEnter={() => setHoveringConfig(true)}
            onMouseLeave={() => setHoveringConfig(false)}
            className="p-2 transition-colors"
            style={{
              color: hoveringConfig ? '#00e5ff' : '#333',
              textShadow: hoveringConfig ? '0 0 8px rgba(0,229,255,0.8)' : '0 0 6px rgba(0,229,255,0.18)',
              filter: hoveringConfig ? 'drop-shadow(0 0 6px rgba(0,229,255,0.55))' : 'none',
            }}
            aria-label="Configurações"
          >
            <Settings size={16} />
          </button>
          <button
            onClick={handleSalvar}
            disabled={saving}
            onMouseEnter={() => setHoveringSave(true)}
            onMouseLeave={() => setHoveringSave(false)}
            className="p-2 transition-colors"
            style={{
              color: hoveringSave ? '#00ff88' : '#333',
              textShadow: hoveringSave ? '0 0 8px rgba(0,255,136,0.8)' : '0 0 6px rgba(0,255,136,0.18)',
              filter: hoveringSave ? 'drop-shadow(0 0 6px rgba(0,255,136,0.55))' : 'none',
            }}
            aria-label="Salvar"
          >
            <Save size={16} />
          </button>
          <button
            onClick={() => { reset(); navigate('/') }}
            onMouseEnter={() => setHoveringExit(true)}
            onMouseLeave={() => setHoveringExit(false)}
            className="p-2 transition-colors"
            style={{
              color: hoveringExit ? '#ff0055' : '#333',
              textShadow: hoveringExit ? '0 0 8px rgba(255,0,85,0.8)' : '0 0 6px rgba(255,0,85,0.18)',
              filter: hoveringExit ? 'drop-shadow(0 0 6px rgba(255,0,85,0.55))' : 'none',
            }}
            aria-label="Sair"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      {/* FUT Card */}
      <div className="px-4 pt-4 relative">
        <div onClick={() => navigate('/player')}>
          <FutCard
            nome={nome}
            nacionalidade={jogador?.nacionalidade}
            overall={overall}
            tour={tour}
            ranking={rank}
            nivel={jogador?.nivel}
            atributos={jogador?.atributos ?? {}}
            atributosPsicologicos={jogador?.atributos_psicologicos ?? {}}
            cartaTipo={jogador?.carta?.tipo}
            cartaRaridade={jogador?.carta?.raridade}
            cartaCor={jogador?.carta?.cor_primaria}
          />
        </div>
        {unreadEmails > 0 && (
          <motion.div 
            initial={{ scale: 0 }} animate={{ scale: 1 }}
            className="absolute top-2 right-2 bg-[#ff0055] text-white pixel-font text-[9px] w-6 h-6 flex items-center justify-center rounded-full border-2 border-white shadow-[0_0_10px_#ff0055] z-10 animate-bounce cursor-pointer"
            onClick={() => navigate('/player', { state: { tab: 6 } })}
          >
            {unreadEmails}
          </motion.div>
        )}
      </div>

      {/* Status meters */}
      <div className="mx-4 mt-3 grid grid-cols-3 gap-2">
        <div
          className="app-panel border-2 p-3"
          style={{ borderColor: accentVar, boxShadow: glowVar }}
        >
          <div className="text-[9px] mb-2" style={{ fontFamily: 'var(--font-pixel)', color: accentVar }}>ENERGIA</div>
          <PixelMeter value={energia} color={accentVar} />
          <div className="text-[10px] mt-2 text-right tabular-nums" style={{ fontFamily: 'var(--font-pixel)', color: accentVar }}>{energia}%</div>
        </div>

        <div
          className="app-panel border-2 p-3"
          style={{
            borderColor: fadiga > 70 ? 'var(--neon-pink)' : 'var(--neon-yellow)',
            boxShadow: fadiga > 70 ? 'var(--glow-pink-sm)' : 'var(--glow-gold-sm)',
          }}
        >
          <div className="text-[9px] mb-2" style={{ fontFamily: 'var(--font-pixel)', color: fadiga > 70 ? 'var(--neon-pink)' : 'var(--neon-yellow)' }}>FADIGA</div>
          <PixelMeter value={fadiga} color={fadiga > 70 ? 'var(--neon-pink)' : 'var(--neon-yellow)'} />
          <div className="text-[10px] mt-2 text-right tabular-nums" style={{ fontFamily: 'var(--font-pixel)', color: fadiga > 70 ? 'var(--neon-pink)' : 'var(--neon-yellow)' }}>{fadiga}%</div>
        </div>

        <div className="app-panel border-2 p-3" style={{ borderColor: 'var(--neon-yellow)', boxShadow: 'var(--glow-gold-sm)' }}>
          <div className="text-[9px] mb-2" style={{ fontFamily: 'var(--font-pixel)', color: 'var(--neon-yellow)' }}>PRÊMIO</div>
          <div className="text-[12px] mt-2" style={{ fontFamily: 'var(--font-pixel)', color: 'var(--neon-yellow)' }}>{fmt(money)}</div>
        </div>
      </div>

      {/* Injury alert */}
      <AnimatePresence>
        {lesionado && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mx-4 mt-2 border-2 border-[#ff0055] bg-black px-3 py-2"
            style={{ boxShadow: '0 0 12px rgba(255,0,85,0.25)' }}
          >
            <div className="text-[10px] text-[#ff0055] animate-pulse" style={{ fontFamily: 'var(--font-pixel)' }}>
              !! LESIONADO - {jogador?.status_lesao?.toUpperCase()}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Active tournament banner */}
      <AnimatePresence>
        {torneio && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => navigate((torneio as any).davis ? '/davis' : '/tournament')}
            onMouseEnter={() => setHoveringActiveTournament(true)}
            onMouseLeave={() => setHoveringActiveTournament(false)}
            className="mx-4 mt-3 w-[calc(100%-2rem)] flex items-center justify-between p-3 border-2 border-[#ffe600] bg-black text-left active:scale-[0.98] transition-transform"
            style={{
              boxShadow: hoveringActiveTournament
                ? '0 0 24px rgba(255,230,0,0.35), inset 0 0 28px rgba(255,230,0,0.08)'
                : '0 0 16px rgba(255,230,0,0.2), inset 0 0 20px rgba(255,230,0,0.04)',
              background: hoveringActiveTournament ? 'rgba(255,230,0,0.06)' : '#000',
            }}
          >
            <div>
              <div className="text-[8px] text-[#ffe600] animate-pulse mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>
                &gt; {(torneio as any).davis ? 'CONFRONTO NACIONAL' : 'TORNEIO EM CURSO'}
              </div>
              <div className="text-[12px] text-white" style={{ fontFamily: 'var(--font-pixel)' }}>{torneio.nome}</div>
              <div className="text-[9px] text-[#666] mt-0.5" style={{ fontFamily: 'var(--font-arcade)' }}>{torneio.fase_atual?.toUpperCase()}</div>
            </div>
            <div
              className="flex items-center gap-1 border-2 border-[#ffe600] px-3 py-1.5 text-[9px] shrink-0 ml-2"
              style={{
                color: '#ffe600',
                fontFamily: 'var(--font-pixel)',
                background: hoveringActiveTournament ? 'rgba(255,230,0,0.14)' : 'transparent',
                boxShadow: hoveringActiveTournament ? '0 0 10px rgba(255,230,0,0.22)' : 'none',
              }}
            >
              PLAY <ChevronRight size={10} />
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Quick access */}
      <div className="px-4 mt-4">
        {!torneio && (
          <button
            onClick={() => navigate('/calendar')}
            onMouseEnter={() => setHoveringNextStep(true)}
            onMouseLeave={() => setHoveringNextStep(false)}
            className="app-next-step mb-3 flex w-full items-center justify-between border-2 border-[#00ff88] bg-[#00ff88]/10 p-3 text-left active:scale-[0.98] transition-transform"
            style={{
              boxShadow: hoveringNextStep
                ? '0 0 24px rgba(0,255,136,0.28)'
                : '0 0 14px rgba(0,255,136,0.18)',
              background: hoveringNextStep ? 'rgba(0,255,136,0.16)' : 'rgba(0,255,136,0.1)',
            }}
          >
            <div className="flex items-center gap-3">
              <div
                className="flex h-9 w-9 items-center justify-center border-2 border-[#00ff88] text-[#00ff88]"
                style={{
                  boxShadow: hoveringNextStep ? '0 0 12px rgba(0,255,136,0.35)' : 'none',
                  background: hoveringNextStep ? 'rgba(0,255,136,0.08)' : 'transparent',
                }}
              >
                <Play size={14} fill="#00ff88" />
              </div>
              <div>
                <div className="text-[9px] text-[#00ff88]" style={{ fontFamily: 'var(--font-pixel)' }}>
                  PRÓXIMO PASSO
                </div>
                <div className="app-next-step-title text-[14px] text-white" style={{ fontFamily: 'var(--font-pixel)' }}>
                  COMEÇAR A JOGAR
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1 text-[10px] text-[#00ff88]" style={{ fontFamily: 'var(--font-pixel)' }}>
              TEMPORADA <ChevronRight size={10} />
            </div>
          </button>
        )}
        <div className="text-[9px] text-[#444] mb-2" style={{ fontFamily: 'var(--font-pixel)' }}>&gt;&gt; MENU</div>
        <div className="grid grid-cols-3 gap-2">
          {QUICK.map((item) => (
            <QuickBtn key={item.route} item={item} onClick={() => navigate(item.route)} />
          ))}
        </div>
      </div>

      {/* Pixel deco bottom */}
      <div className="mx-4 mt-5 flex gap-[3px]">
        {Array.from({ length: 30 }).map((_, i) => (
          <div key={i} className="flex-1 h-[2px]" style={{ background: i % 3 === 0 ? accent : 'transparent' }} />
        ))}
      </div>

      <BottomNav />
    </div>
  )
}

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { motion, AnimatePresence } from 'motion/react'
import {
  Settings, Save, LogOut, ChevronRight,
  Globe, ShoppingBag, Shield, Users, History, CalendarDays, Play, Mic, Crown,
} from 'lucide-react'
import { FutCard, BottomNav } from '../components'
import { useGameStore } from '../../store/gameStore'
import { api } from '../../api/client'
import { useTheme } from '../hooks/useTheme'
import { HubRadioCard } from './hub/HubRadioCard'
import { useHubRadio } from './hub/radio/useHubRadio'

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
  { icon: CalendarDays, label: 'JOGAR',    route: '/calendar',  color: 'var(--neon-green)',  rgb: 'var(--neon-green-rgb)' },
  { icon: ShoppingBag,  label: 'MERCADO',  route: '/market',    color: 'var(--neon-pink)',   rgb: 'var(--neon-pink-rgb)' },
  { icon: Users,        label: 'DUPLAS',   route: '/duplas',    color: 'var(--neon-cyan)',   rgb: 'var(--neon-cyan-rgb)' },
  { icon: Shield,       label: 'DAVIS',    route: '/davis',     color: 'var(--neon-yellow)', rgb: 'var(--neon-yellow-rgb)' },
  { icon: History,      label: 'HISTORICO',route: '/history',   color: 'var(--neon-yellow)', rgb: 'var(--neon-yellow-rgb)' },
  { icon: Globe,        label: 'MUNDO',    route: '/world',     color: 'var(--neon-yellow)', rgb: 'var(--neon-yellow-rgb)' },
  { icon: Mic,          label: 'IMPRENSA', route: '/imprensa',  color: 'var(--neon-purple)', rgb: 'var(--neon-purple-rgb)' },
  { icon: Crown,        label: 'LIFESTYLE',route: '/lifestyle', color: '#ffb7c6',            rgb: '255,183,198' },
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
        borderColor: hovered ? item.color : `rgba(${item.rgb},0.20)`,
        background: hovered ? `rgba(${item.rgb},0.05)` : 'var(--card)',
        boxShadow: hovered ? `0 0 10px rgba(${item.rgb},0.27)` : 'none',
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
  const radio = useHubRadio()

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
  
  // Landmarks Visuais (Ranking-based UI levels)
  const isTop10   = rank > 0 && rank <= 10
  const isTop100  = rank > 0 && rank <= 100
  
  const accent    = isTop10 ? 'var(--neon-yellow)' : isTop100 ? 'var(--neon-cyan)' : isAtp ? 'var(--neon-green)' : 'var(--neon-pink)'
  const accentVar = isTop10 ? 'var(--neon-yellow)' : isTop100 ? 'var(--neon-cyan)' : isAtp ? 'var(--neon-green)' : 'var(--neon-pink)'
  const glowVar   = isTop10 ? 'var(--glow-gold-sm)' : isTop100 ? 'var(--glow-cyan-sm)' : isAtp ? 'var(--glow-green-sm)' : 'var(--glow-pink-sm)'
  const shadowVar = isTop10 ? '0 2px 12px rgba(255,230,0,0.22)' : isTop100 ? '0 2px 12px rgba(0,229,255,0.22)' : isAtp ? '0 2px 12px rgba(0,255,136,0.12)' : '0 2px 12px rgba(255,0,85,0.12)'
  
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
        <div className="flex items-center justify-between gap-3 bg-[#1a0008] border-b-2 border-neon-pink px-4 py-2">
          <span className="arcade-font text-[10px] text-neon-pink tracking-wider">ERRO AO CARREGAR DADOS — SERVIDOR OFFLINE?</span>
          <button
            type="button"
            onClick={() => { setLoadError(false); fetchJogador().catch(() => setLoadError(true)) }}
            className="arcade-font text-[10px] text-[#ff7d9e] border border-neon-pink px-2 py-1"
          >
            TENTAR NOVAMENTE
          </button>
        </div>
      )}
      {mostrarPromptAutoSave && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/82 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md border-2 border-neon-green bg-[#06110c] p-5 shadow-[0_0_24px_rgba(0,255,136,0.18)]">
            <div className="arcade-font text-[10px] tracking-[0.2em] text-neon-green">SALVAMENTO AUTOMÁTICO</div>
            <div className="pixel-font mt-3 text-lg text-white">Deseja ativar o salvamento automático?</div>
            <div className="arcade-font mt-3 text-[11px] leading-relaxed text-[#9bc7af]">
              Essa configuração é definida no hub e usada quando uma nova partida começar.
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => definirAutoSave(false)}
                className="min-h-[44px] border-2 border-neon-pink px-4 py-3 arcade-font text-[10px] text-[#ff7d9e]"
              >
                NÃO
              </button>
              <button
                type="button"
                onClick={() => definirAutoSave(true)}
                className="min-h-[44px] border-2 border-neon-green px-4 py-3 arcade-font text-[10px] text-neon-green"
              >
                SIM
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top bar */}
      <div
        className="flex items-center justify-between px-4 py-3 border-b-2"
        style={{ borderColor: accent, boxShadow: shadowVar }}
      >
        <div>
          <div
            className="text-[10px]"
            style={{ fontFamily: 'var(--font-pixel)', color: accent, textShadow: `0 0 6px ${accent}` }}
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
                  color: saveMsg === 'SALVO' ? 'var(--neon-green)' : 'var(--neon-pink)',
                  textShadow: `0 0 6px ${saveMsg === 'SALVO' ? 'var(--neon-green)' : 'var(--neon-pink)'}`,
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
              color: hoveringConfig ? 'var(--neon-cyan)' : '#333',
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
              color: hoveringSave ? 'var(--neon-green)' : '#333',
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
              color: hoveringExit ? 'var(--neon-pink)' : '#333',
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
            className="absolute top-2 right-2 bg-neon-pink text-white pixel-font text-[9px] w-6 h-6 flex items-center justify-center rounded-full border-2 border-white shadow-[0_0_10px_#ff0055] z-10 animate-bounce cursor-pointer"
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
            className="mx-4 mt-2 border-2 border-neon-pink bg-black px-3 py-2"
            style={{ boxShadow: '0 0 12px rgba(255,0,85,0.25)' }}
          >
            <div className="text-[10px] text-neon-pink animate-pulse" style={{ fontFamily: 'var(--font-pixel)' }}>
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
            animate={{ 
              opacity: 1,
              boxShadow: [
                '0 0 16px rgba(255,230,0,0.2)', 
                '0 0 32px rgba(255,230,0,0.45)', 
                '0 0 16px rgba(255,230,0,0.2)'
              ]
            }}
            transition={{ 
              opacity: { duration: 0.3 },
              boxShadow: { duration: 2, repeat: Infinity, ease: "easeInOut" }
            }}
            exit={{ opacity: 0 }}
            onClick={() => navigate((torneio as any).davis ? '/davis' : '/tournament')}
            onMouseEnter={() => setHoveringActiveTournament(true)}
            onMouseLeave={() => setHoveringActiveTournament(false)}
            className="mx-4 mt-3 w-[calc(100%-2rem)] flex items-center justify-between p-3 border-2 border-neon-yellow bg-black text-left active:scale-[0.98] transition-transform"
            style={{
              background: hoveringActiveTournament ? 'rgba(255,230,0,0.06)' : '#000',
            }}
          >
            <div>
              <div className="text-[8px] text-neon-yellow animate-pulse mb-1" style={{ fontFamily: 'var(--font-pixel)' }}>
                &gt; {(torneio as any).davis ? 'CONFRONTO NACIONAL' : 'TORNEIO EM CURSO'}
              </div>
              <div className="text-[12px] text-white" style={{ fontFamily: 'var(--font-pixel)' }}>{torneio.nome}</div>
              <div className="text-[9px] text-[#666] mt-0.5" style={{ fontFamily: 'var(--font-arcade)' }}>{torneio.fase_atual?.toUpperCase()}</div>
            </div>
            <div
              className="flex items-center gap-1 border-2 border-neon-yellow px-3 py-1.5 text-[9px] shrink-0 ml-2"
              style={{
                color: 'var(--neon-yellow)',
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
          <motion.button
            animate={{ 
              boxShadow: [
                '0 0 14px rgba(0,255,136,0.18)', 
                '0 0 28px rgba(0,255,136,0.4)', 
                '0 0 14px rgba(0,255,136,0.18)'
              ],
              scale: [1, 1.005, 1]
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            onClick={() => navigate('/calendar')}
            onMouseEnter={() => setHoveringNextStep(true)}
            onMouseLeave={() => setHoveringNextStep(false)}
            className="app-next-step mb-3 flex w-full items-center justify-between border-2 border-neon-green bg-neon-green/10 p-3 text-left active:scale-[0.98] transition-transform"
            style={{
              background: hoveringNextStep ? 'rgba(0,255,136,0.16)' : 'rgba(0,255,136,0.1)',
            }}
          >
            <div className="flex items-center gap-3">
              <div
                className="flex h-9 w-9 items-center justify-center border-2 border-neon-green text-neon-green"
                style={{
                  boxShadow: hoveringNextStep ? '0 0 12px rgba(0,255,136,0.35)' : 'none',
                  background: hoveringNextStep ? 'rgba(0,255,136,0.08)' : 'transparent',
                }}
              >
                <Play size={14} fill="var(--neon-green)" />
              </div>
              <div>
                <div className="text-[9px] text-neon-green" style={{ fontFamily: 'var(--font-pixel)' }}>
                  PRÓXIMO PASSO
                </div>
                <div className="app-next-step-title text-[14px] text-white" style={{ fontFamily: 'var(--font-pixel)' }}>
                  COMEÇAR A JOGAR
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1 text-[10px] text-neon-green" style={{ fontFamily: 'var(--font-pixel)' }}>
              TEMPORADA <ChevronRight size={10} />
            </div>
          </motion.button>
        )}
        <div className="text-[9px] text-[#444] mb-2" style={{ fontFamily: 'var(--font-pixel)' }}>&gt;&gt; MENU</div>
        <div className="grid grid-cols-3 gap-2">
          {QUICK.map((item) => (
            <QuickBtn key={item.route} item={item} onClick={() => navigate(item.route)} />
          ))}
        </div>
      </div>

      <HubRadioCard
        currentTrack={radio.currentTrack}
        erro={radio.erro}
        playing={radio.playing}
        sourceType={radio.sourceType}
        station={radio.station}
        stations={radio.stations}
        volume={radio.volume}
        setVolume={radio.setVolume}
        togglePlay={radio.togglePlay}
        trocarEstacao={radio.trocarEstacao}
        avancarFaixaOuEstacao={radio.avancarFaixaOuEstacao}
      />

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

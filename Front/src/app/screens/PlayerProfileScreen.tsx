import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router'
import { ArcadeTab, NeonButton, PageHeader, PixelFlag } from '../components'
import { api } from '../../api/client'
import type { CartaJogador, PlayerIdentity, PlayerProfile } from '../../types'
import { getDuplasRating, getOverallTierLabel, getSpecialCardPalette, isDoublesSpecialist } from '../utils/playerRatings'

const TABS = ['VISÃO GERAL', 'ATRIBUTOS', 'HISTÓRIA']

const ATRIB_TECNICOS: [string, string][] = [
  ['vel_saque', 'V.SAQUE'],
  ['retorno', 'RETORNO'],
  ['forehand', 'FOREHAND'],
  ['backhand', 'BACKHAND'],
  ['voleio', 'VOLEIO'],
  ['winner', 'WINNER'],
  ['topspin', 'TOPSPIN'],
  ['resistencia', 'RESISTÊN.'],
]

const ATRIB_MENTAIS: [string, string][] = [
  ['determinacao', 'DETERMINAÇÃO'],
  ['compostura', 'COMPOSTURA'],
  ['agressividade', 'AGRESSIVIDADE'],
  ['leitura_de_jogo', 'LEITURA'],
  ['clutch', 'CLUTCH'],
  ['consistencia', 'CONSISTÊNCIA'],
]

const FASE_LABEL: Record<string, string> = {
  campeao: 'CAMPEÃO',
  final: 'FINAL',
  semifinal: 'SEMIFINAL',
  quartas: 'QUARTAS',
  oitavas: 'OITAVAS',
  r16: 'OITAVAS',
  r32: 'R32',
  r64: 'R64',
  r128: 'R128',
}

const HIDDEN_LABELS: Record<string, string> = {
  clutch: 'CLUTCH',
  positioning: 'POSIC.',
  anticipation: 'ANTIC.',
  rally_tolerance: 'RALLY',
  transition: 'TRANS.',
  doubles_iq: 'DUB IQ',
}

function fmtNumero(valor: number) {
  return valor.toLocaleString('pt-BR')
}

function faseLabel(valor: unknown) {
  const chave = String(valor ?? '').trim().toLowerCase()
  return FASE_LABEL[chave] ?? String(valor ?? '—').toUpperCase()
}

function resumoTitulos(trofeus: Array<Record<string, unknown>>) {
  const gs = trofeus.filter(item => String(item.categoria ?? '').includes('Grand Slam')).length
  const mil = trofeus.filter(item => String(item.categoria ?? '').includes('1000')).length
  return { total: trofeus.length, gs, mil }
}

function cardColor(tour: string) {
  return tour === 'wta' ? '#ff4466' : 'var(--neon-cyan)'
}

function InfoCard({
  label,
  value,
  color,
  boostedValue,
}: {
  label: string
  value: string | number
  color: string
  boostedValue?: string | number
}) {
  return (
    <div className="border bg-[#0c1016] px-3 py-3 text-center" style={{ borderColor: `${color}55` }}>
      <div className="arcade-font text-[8px] tracking-widest text-[#728293]">{label}</div>
      <div className="pixel-font mt-2 text-[18px]" style={{ color }}>{boostedValue ?? value}</div>
      {boostedValue !== undefined && boostedValue !== value && (
        <div className="arcade-font text-[7px] mt-0.5" style={{ color: '#00FF88' }}>
          +{Number(boostedValue) - Number(value)} BOOST
        </div>
      )}
    </div>
  )
}

function CartaBadge({ carta }: { carta: CartaJogador }) {
  const isBase = ['gold', 'silver', 'bronze', 'iconic'].includes(carta.tipo)
  if (isBase && carta.raridade !== 'iconic') return null
  return (
    <div
      className="border px-2 py-1 arcade-font text-[8px]"
      style={{ borderColor: carta.cor_primaria, color: carta.cor_primaria }}
    >
      {carta.label}
    </div>
  )
}

function IdentityChip({ label, value, color = '#8aa0b2' }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="border px-2 py-1 arcade-font text-[8px]" style={{ borderColor: `${color}66`, color }}>
      {label}: {value}
    </div>
  )
}

function HiddenStatCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="border border-white/10 bg-black/30 px-2 py-2">
      <div className="arcade-font text-[8px] text-[#7f95a7]">{label}</div>
      <div className="pixel-font mt-1 text-[15px]" style={{ color }}>{value}</div>
    </div>
  )
}

function PlaystyleBadge({ label, tier }: { label: string; tier: 'base' | 'plus' }) {
  const color = tier === 'plus' ? '#f6c453' : 'var(--neon-cyan)'
  return (
    <div
      className="border px-2 py-1 arcade-font text-[8px]"
      style={{ borderColor: color, color, background: tier === 'plus' ? 'rgba(246,196,83,0.08)' : 'rgba(0,229,255,0.08)' }}
    >
      {label}
    </div>
  )
}

export function PlayerProfileScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const params = useParams()
  const nome = decodeURIComponent(params.nome ?? '')
  const tour = (params.tour === 'wta' ? 'wta' : 'atp') as 'atp' | 'wta'
  const modalidade = new URLSearchParams(location.search).get('modalidade') === 'duplas' ? 'duplas' : 'simples'

  const [activeTab, setActiveTab] = useState(0)
  const [perfil, setPerfil] = useState<PlayerProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    let ativo = true
    setLoading(true)
    setErro(null)
    api.ranking.jogador(nome, tour, modalidade)
      .then((data) => {
        if (!ativo) return
        setPerfil(data)
      })
      .catch((e: Error) => {
        if (!ativo) return
        setErro(e.message || 'Erro ao carregar perfil.')
      })
      .finally(() => {
        if (ativo) setLoading(false)
      })
    return () => { ativo = false }
  }, [nome, tour, modalidade])

  const cor = cardColor(tour)
  const trofeus = perfil?.trofeus ?? []
  const historicoTorneios = perfil?.historico_torneios ?? []
  const historicoPartidas = perfil?.historico_partidas ?? []
  const sumario = useMemo(() => resumoTitulos(trofeus), [trofeus])
  const duplas = getDuplasRating(perfil?.atributos)
  const especialistaDuplas = isDoublesSpecialist(perfil?.atributos, modalidade)
  const palette = getSpecialCardPalette(especialistaDuplas, tour)
  const tier = getOverallTierLabel(perfil?.overall ?? 0, perfil?.ranking ?? null)
  const carta = perfil?.carta ?? null
  const identity: PlayerIdentity | null = perfil?.identity ?? null
  // When carta has bonus, use cor_primaria to tint the UI
  const cartaAccent = carta?.cor_primaria ?? palette.accent
  const cartaGlow = carta?.cor_primaria
    ? `0 0 18px ${carta.cor_primaria}44`
    : palette.glow
  // Boosted atributos: apply bonus on top of base atributos
  const atributosBoosted = useMemo(() => {
    if (!carta?.bonus || Object.keys(carta.bonus).length === 0) return undefined
    const base = perfil?.atributos ?? {}
    const result: Record<string, number> = { ...base }
    for (const [k, v] of Object.entries(carta.bonus)) {
      if (k in result) result[k] = Math.min(99, result[k] + v)
    }
    return result
  }, [carta, perfil?.atributos])
  const atributosPsiBoosted = useMemo(() => {
    if (!carta?.bonus || Object.keys(carta.bonus).length === 0) return undefined
    const base = perfil?.atributos_psicologicos ?? {}
    const result: Record<string, number> = { ...base }
    for (const [k, v] of Object.entries(carta.bonus)) {
      if (k in result) result[k] = Math.min(99, result[k] + v)
    }
    return result
  }, [carta, perfil?.atributos_psicologicos])

  return (
    <div className="app-shell min-h-screen pb-24">
      <PageHeader
        title={perfil?.nome ?? nome.toUpperCase()}
        subtitle={perfil ? `${perfil.tour.toUpperCase()} ${modalidade.toUpperCase()} • PERFIL COMPLETO` : 'DOSSIÊ DO JOGADOR'}
        color={tour === 'wta' ? 'pink' : 'cyan'}
        onBack={() => navigate(-1)}
      >
        <ArcadeTab tabs={TABS} activeTab={activeTab} onChange={setActiveTab} color={tour === 'wta' ? 'pink' : 'cyan'} />
      </PageHeader>

      <div className="p-4 space-y-4">
        {loading && (
          <div className="py-16 text-center pixel-font text-sm" style={{ color: cor }}>
            CARREGANDO PERFIL...
          </div>
        )}

        {!loading && erro && (
          <div className="border border-[#ff4466]/50 bg-[#220d14] p-4 text-center">
            <div className="arcade-font text-[10px] text-[#ff8ca8]">{erro}</div>
          </div>
        )}

        {!loading && perfil && (
          <>
            <div
              className="border-2 p-4"
              style={{
                borderColor: cartaAccent,
                boxShadow: cartaGlow,
                background: carta?.cor_primaria
                  ? `linear-gradient(180deg, ${carta.cor_primaria}18 0%, rgba(11,17,24,0.96) 44%, rgba(11,17,24,1) 100%)`
                  : especialistaDuplas
                  ? `linear-gradient(180deg, ${palette.soft} 0%, rgba(11,17,24,0.96) 44%, rgba(11,17,24,1) 100%)`
                  : undefined,
              }}
            >
              <div className="grid grid-cols-1 gap-4 md:grid-cols-[0.95fr_1.05fr]">
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-20 w-20 items-center justify-center border-2 text-4xl" style={{ borderColor: cartaAccent }}>
                      🎾
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <PixelFlag countryCode={perfil.nacionalidade} size="md" />
                        <div className="pixel-font text-[20px] text-white">{perfil.nome}</div>
                      </div>
                      <div className="arcade-font mt-1 text-[9px] tracking-widest text-[#92a1b2]">
                        {perfil.ranking ? `#${perfil.ranking} MUNDIAL` : 'SEM RANKING'} • {perfil.estilo_jogo ?? 'SEM ESTILO'}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <div className="border px-2 py-1 arcade-font text-[8px]" style={{ borderColor: cartaAccent, color: cartaAccent }}>
                          {tier}
                        </div>
                        {carta && <CartaBadge carta={carta} />}
                        {identity && <IdentityChip label="ROLE" value={identity.role.label} color={cartaAccent} />}
                        {duplas > 0 && (
                          <div className="border px-2 py-1 arcade-font text-[8px]" style={{ borderColor: especialistaDuplas ? '#f6c453' : '#4a6172', color: especialistaDuplas ? '#f6c453' : '#8aa0b2' }}>
                            DUPLAS {duplas}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                    <InfoCard
                      label="OVR"
                      value={perfil.overall || '—'}
                      color={cartaAccent}
                      boostedValue={perfil.overall_boosted && perfil.overall_boosted !== perfil.overall ? perfil.overall_boosted : undefined}
                    />
                    <InfoCard label="PONTOS" value={fmtNumero(perfil.pontos)} color="var(--neon-yellow)" />
                    <InfoCard label="RACE" value={fmtNumero(perfil.pontos_ytd)} color="var(--neon-green)" />
                    <InfoCard label="IDADE" value={perfil.idade || '—'} color="#ffffff" />
                    <InfoCard label="ALTURA" value={perfil.altura ? `${perfil.altura} cm` : '—'} color="#ffffff" />
                    <InfoCard label="PESO" value={perfil.peso ? `${perfil.peso} kg` : '—'} color="#ffffff" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="border bg-[#0b1118] p-3" style={{ borderColor: `${palette.accent}44` }}>
                    <div className="arcade-font text-[8px] tracking-widest text-[#8aa0b2]">DADOS PESSOAIS</div>
                    <div className="mt-3 space-y-2 arcade-font text-[10px] text-white">
                      <div>MÃO: <span style={{ color: palette.accent }}>{perfil.mao_dominante ?? '—'}</span></div>
                      <div>REVÉS: <span style={{ color: palette.accent }}>{perfil.reves ?? '—'}</span></div>
                      <div>PICO: <span style={{ color: palette.accent }}>{perfil.pico_carreira ? `#${perfil.pico_carreira}` : '—'}</span></div>
                      <div>MODALIDADE: <span style={{ color: especialistaDuplas ? '#f6c453' : palette.accent }}>{modalidade.toUpperCase()}</span></div>
                      {identity && <div>BODY: <span style={{ color: palette.accent }}>{identity.body_type.label}</span></div>}
                    </div>
                  </div>
                  <div className="border bg-[#0b1118] p-3" style={{ borderColor: `${palette.accent}44` }}>
                    <div className="arcade-font text-[8px] tracking-widest text-[#8aa0b2]">VITRINE</div>
                    <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                      <InfoCard label="TÍT." value={sumario.total} color={palette.accent} />
                      <InfoCard label="GS" value={sumario.gs} color="var(--neon-yellow)" />
                      <InfoCard label="1000" value={sumario.mil} color="var(--neon-green)" />
                    </div>
                  </div>
                  <div className="col-span-2 border bg-[#0b1118] p-3" style={{ borderColor: `${palette.accent}44` }}>
                    <div className="arcade-font text-[8px] tracking-widest text-[#8aa0b2]">RESUMO DE ATRIBUTOS</div>
                    <div className="mt-3 grid grid-cols-3 gap-2 md:grid-cols-6">
                      {Object.entries(perfil.resumo_fifa).map(([chave, valor]) => (
                        <div key={chave} className="border border-white/10 bg-black/40 px-2 py-2 text-center">
                          <div className="arcade-font text-[8px] text-[#7f95a7]">{chave}</div>
                          <div
                            className="pixel-font mt-1 text-[16px]"
                            style={{ color: chave.toLowerCase() === 'duplas' ? '#f6c453' : palette.accent }}
                          >
                            {valor}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {activeTab === 0 && (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="border p-4" style={{ borderColor: `${cor}55` }}>
                  <div className="arcade-font text-[10px] tracking-widest" style={{ color: cor }}>ÚLTIMOS TÍTULOS</div>
                  <div className="mt-3 space-y-2">
                    {trofeus.length > 0 ? trofeus.slice(-8).reverse().map((item, idx) => (
                      <div key={`${String(item.nome)}-${idx}`} className="border border-white/10 bg-[#0a0f15] px-3 py-2">
                        <div className="arcade-font text-[10px] text-white">{String(item.nome ?? 'Torneio')}</div>
                        <div className="arcade-font mt-1 text-[8px] text-[#8ea0b1]">
                          {String(item.categoria ?? 'Título').toUpperCase()} • {String(item.ano ?? '—')}
                        </div>
                      </div>
                    )) : (
                      <div className="arcade-font text-[10px] text-[#8594a5]">Nenhum título registrado.</div>
                    )}
                  </div>
                </div>

                <div className="border p-4" style={{ borderColor: `${cor}55` }}>
                  <div className="arcade-font text-[10px] tracking-widest" style={{ color: cor }}>HISTÓRICO RECENTE</div>
                  <div className="mt-3 space-y-2">
                    {historicoTorneios.length > 0 ? historicoTorneios.slice(-8).reverse().map((item, idx) => (
                      <div key={`${String(item.nome ?? item.torneio)}-${idx}`} className="border border-white/10 bg-[#0a0f15] px-3 py-2">
                        <div className="arcade-font text-[10px] text-white">{String(item.nome ?? item.torneio ?? 'Torneio')}</div>
                        <div className="arcade-font mt-1 text-[8px] text-[#8ea0b1]">
                          {faseLabel(item.fase ?? item.resultado)} • {String(item.ano ?? '—')}
                        </div>
                      </div>
                    )) : (
                      <div className="arcade-font text-[10px] text-[#8594a5]">Sem histórico recente salvo.</div>
                    )}
                  </div>
                </div>

                {identity && (
                  <div className="border p-4" style={{ borderColor: `${cartaAccent}55` }}>
                    <div className="arcade-font text-[10px] tracking-widest" style={{ color: cartaAccent }}>DNA EA</div>
                    <div className="mt-3 space-y-3">
                      <div className="grid grid-cols-2 gap-2">
                        <InfoCard label="ROLE" value={identity.role.label} color={cartaAccent} />
                        <InfoCard label="FIT" value={identity.role.fit} color="var(--neon-yellow)" />
                        <InfoCard label="BODY" value={identity.body_type.label} color="#ffffff" />
                        <InfoCard label="CHEM" value={identity.doubles_profile.rating} color={identity.doubles_profile.specialist ? '#f6c453' : 'var(--neon-cyan)'} />
                      </div>
                      <div className="arcade-font text-[9px] text-[#8ea0b1]">{identity.role.description}</div>
                      <div className="flex flex-wrap gap-2">
                        <IdentityChip label="DUB ARCH" value={identity.doubles_profile.archetype} color={identity.doubles_profile.specialist ? '#f6c453' : '#8aa0b2'} />
                        <IdentityChip label="PARCERIAS" value={identity.doubles_profile.partnerships} color="#8aa0b2" />
                        {identity.doubles_profile.best_partner && (
                          <IdentityChip label="BEST LINK" value={identity.doubles_profile.best_partner} color="var(--neon-green)" />
                        )}
                        {identity.doubles_profile.record && (
                          <IdentityChip label="REC" value={identity.doubles_profile.record} color="var(--neon-yellow)" />
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {identity && (
                  <div className="border p-4" style={{ borderColor: `${cartaAccent}55` }}>
                    <div className="arcade-font text-[10px] tracking-widest" style={{ color: cartaAccent }}>PLAYSTYLES</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {identity.playstyles.length > 0 ? identity.playstyles.map((playstyle) => (
                        <PlaystyleBadge key={playstyle.id} label={playstyle.label} tier={playstyle.tier} />
                      )) : (
                        <div className="arcade-font text-[10px] text-[#8594a5]">Sem playstyles especiais.</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 1 && (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="border p-4" style={{ borderColor: `${cor}55` }}>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="arcade-font text-[10px] tracking-widest" style={{ color: cor }}>ATRIBUTOS TÉCNICOS</div>
                    {carta && Object.keys(carta.bonus).length > 0 && (
                      <div className="arcade-font text-[8px] px-1.5 py-0.5 border" style={{ color: carta.cor_primaria, borderColor: carta.cor_primaria }}>
                        {carta.label} BOOST
                      </div>
                    )}
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 md:grid-cols-3">
                    {ATRIB_TECNICOS.map(([key, label]) => (
                      <InfoCard
                        key={key}
                        label={label}
                        value={perfil.atributos[key] ?? '—'}
                        color={cor}
                        boostedValue={
                          atributosBoosted && atributosBoosted[key] !== undefined && atributosBoosted[key] !== perfil.atributos[key]
                            ? atributosBoosted[key]
                            : undefined
                        }
                      />
                    ))}
                  </div>
                </div>

                <div className="border p-4" style={{ borderColor: `${cor}55` }}>
                  <div className="arcade-font text-[10px] tracking-widest mb-3" style={{ color: cor }}>MENTAL</div>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {ATRIB_MENTAIS.map(([key, label]) => (
                      <InfoCard
                        key={key}
                        label={label}
                        value={perfil.atributos_psicologicos[key] ?? '—'}
                        color="var(--neon-yellow)"
                        boostedValue={
                          atributosPsiBoosted && atributosPsiBoosted[key] !== undefined && atributosPsiBoosted[key] !== perfil.atributos_psicologicos[key]
                            ? atributosPsiBoosted[key]
                            : undefined
                        }
                      />
                    ))}
                  </div>
                </div>

                {identity && (
                  <div className="border p-4 md:col-span-2" style={{ borderColor: `${cartaAccent}55` }}>
                    <div className="arcade-font text-[10px] tracking-widest" style={{ color: cartaAccent }}>HIDDEN STATS</div>
                    <div className="mt-3 grid grid-cols-2 gap-2 md:grid-cols-6">
                      {Object.entries(identity.hidden_stats).map(([key, value]) => (
                        <HiddenStatCard key={key} label={HIDDEN_LABELS[key] ?? key.toUpperCase()} value={value} color={key === 'doubles_iq' ? '#f6c453' : cartaAccent} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 2 && (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div className="border p-4" style={{ borderColor: `${cor}55` }}>
                  <div className="arcade-font text-[10px] tracking-widest" style={{ color: cor }}>GALERIA DE TÍTULOS</div>
                  <div className="mt-3 space-y-2">
                    {trofeus.length > 0 ? trofeus.slice().reverse().map((item, idx) => (
                      <div key={`${String(item.nome)}-${String(item.ano)}-${idx}`} className="flex items-center justify-between gap-3 border border-white/10 bg-[#0a0f15] px-3 py-2">
                        <div>
                          <div className="arcade-font text-[10px] text-white">{String(item.nome ?? 'Torneio')}</div>
                          <div className="arcade-font mt-1 text-[8px] text-[#8ea0b1]">{String(item.categoria ?? 'Título').toUpperCase()}</div>
                        </div>
                        <div className="pixel-font text-[14px]" style={{ color: cor }}>{String(item.ano ?? '—')}</div>
                      </div>
                    )) : (
                      <div className="arcade-font text-[10px] text-[#8594a5]">Nenhum título para exibir.</div>
                    )}
                  </div>
                </div>

                <div className="border p-4" style={{ borderColor: `${cor}55` }}>
                  <div className="arcade-font text-[10px] tracking-widest" style={{ color: cor }}>ÚLTIMAS PARTIDAS</div>
                  <div className="mt-3 space-y-2">
                    {historicoPartidas.length > 0 ? historicoPartidas.slice().reverse().slice(0, 20).map((item, idx) => (
                      <div key={`${String(item.torneio)}-${idx}`} className="border border-white/10 bg-[#0a0f15] px-3 py-2">
                        <div className="arcade-font text-[10px] text-white">
                          {String(item.torneio ?? 'Partida')} • {faseLabel(item.fase)}
                        </div>
                        <div className="arcade-font mt-1 text-[8px] text-[#8ea0b1]">
                          {String(item.resultado ?? '').toUpperCase()} • {String(item.adversario ?? 'Adversário')} • {String(item.placar ?? '—')}
                        </div>
                      </div>
                    )) : (
                      <div className="arcade-font text-[10px] text-[#8594a5]">Sem partidas recentes registradas.</div>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <NeonButton variant={tour === 'wta' ? 'pink' : 'cyan'} onClick={() => navigate('/rankings')}>
                VOLTAR AO RANKING
              </NeonButton>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

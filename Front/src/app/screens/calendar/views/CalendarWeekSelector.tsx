import { ScreenSection } from '../../../components'
import { TOTAL_WEEKS } from '../model'

interface CalendarWeekSelectorProps {
  semanaAtual: number
  semanaSelecionada: number
  semanasTorneio: Set<number>
  scrollRef: React.RefObject<HTMLDivElement | null>
  onSelectWeek: (week: number) => void
}

export function CalendarWeekSelector({
  semanaAtual,
  semanaSelecionada,
  semanasTorneio,
  scrollRef,
  onSelectWeek,
}: CalendarWeekSelectorProps) {
  return (
    <ScreenSection title="SELETOR DE SEMANA" subtitle="Navegue pelas 52 semanas da temporada" variant="yellow">
      <div ref={scrollRef} className="flex gap-2 overflow-x-auto pb-2 [scrollbar-width:thin]">
        {Array.from({ length: TOTAL_WEEKS }, (_, index) => index + 1).map((week) => {
          const hasTournament = semanasTorneio.has(week)
          const isAtual = week === semanaAtual

          return (
            <button
              key={week}
              data-week={week}
              onClick={() => onSelectWeek(week)}
              className={`flex h-14 w-14 shrink-0 flex-col items-center justify-center border-2 transition-all ${
                week === semanaSelecionada
                  ? 'border-neon-green bg-neon-green text-black'
                  : hasTournament
                    ? 'border-neon-green/50 bg-[#1a1a2e] text-neon-green'
                    : 'border-[#333] bg-transparent text-[#888]'
              } ${isAtual && week !== semanaSelecionada ? 'ring-1 ring-neon-yellow' : ''}`}
            >
              <div className="pixel-font text-[10px]">{week}</div>
              {hasTournament && <div className="mt-1 text-sm">●</div>}
            </button>
          )
        })}
      </div>
    </ScreenSection>
  )
}

import { ActionDock, NeonButton, PageHeader } from '../components'
import { TournamentEntryModal } from '../components/TournamentEntryModal'
import { useCalendarScreen } from './calendar/useCalendarScreen'
import { CalendarWeekSelector } from './calendar/views/CalendarWeekSelector'
import { CalendarTournamentGrid } from './calendar/views/CalendarTournamentGrid'

export function CalendarScreen() {
  const {
    ano,
    semanaAtual,
    selectedWeek,
    setSelectedWeek,
    torneiosSemana,
    semanasTorneio,
    loading,
    torneioParaInscrever,
    setTorneioParaInscrever,
    inscrevendo,
    erroInscricao,
    convocacao,
    scrollRef,
    torneioAtivo,
    handleSelectTorneio,
    handleConfirmarInscricao,
    handleRecusarConvocacao,
    handleDescansar,
  } = useCalendarScreen()

  return (
    <div className="app-shell min-h-screen font-mono pb-24">
      {torneioParaInscrever && (
        <TournamentEntryModal
          torneio={torneioParaInscrever}
          onClose={() => setTorneioParaInscrever(null)}
          onConfirm={handleConfirmarInscricao}
        />
      )}
      <PageHeader
        title="CIRCUITO MUNDIAL"
        subtitle={`TEMPORADA ${ano} • SEMANA ${selectedWeek}`}
        color="yellow"
        backTo="/hub"
      />

      <div className="p-4 space-y-6">
        <CalendarWeekSelector
          semanaAtual={semanaAtual}
          semanaSelecionada={selectedWeek}
          semanasTorneio={semanasTorneio}
          scrollRef={scrollRef}
          onSelectWeek={setSelectedWeek}
        />

        <CalendarTournamentGrid
          loading={loading}
          semanaAtual={semanaAtual}
          semanaSelecionada={selectedWeek}
          torneiosSemana={torneiosSemana}
          convocacao={convocacao}
          inscrevendo={inscrevendo}
          erroInscricao={erroInscricao}
          torneioAtivo={torneioAtivo}
          onSelectTournament={handleSelectTorneio}
          onConfirmCallup={() => handleConfirmarInscricao('simples')}
          onDeclineCallup={handleRecusarConvocacao}
        />
      </div>

      <ActionDock>
        <div className="mx-auto w-full max-w-6xl">
          <NeonButton variant="pink" className="w-full" disabled={torneioAtivo} onClick={handleDescansar}>
            [ PULAR SEMANA (RECUPERAR ENERGIA) ]
          </NeonButton>
        </div>
      </ActionDock>
    </div>
  )
}

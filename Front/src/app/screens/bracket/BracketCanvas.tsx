import { buildBracketLayout } from './utils'
import { HEADER_HEIGHT, CARD_HEIGHT, CARD_WIDTH } from './types'
import type { BracketSection } from './types'
import { BracketMatchCard } from './BracketMatchCard'

export function BracketCanvas({ section }: { section: BracketSection }) {
  const layout = buildBracketLayout(section.rounds)
  const totalWidth =
    layout.length > 0 ? layout[layout.length - 1].x + CARD_WIDTH + 20 : CARD_WIDTH
  const totalHeight =
    HEADER_HEIGHT +
    Math.max(
      220,
      ...layout.flatMap((column) => column.positions.map((top) => top + CARD_HEIGHT + 20))
    )

  return (
    <section className="overflow-hidden rounded border border-neon-pink/40 bg-[#090909] shadow-[0_0_20px_#ff005533]">
      <div className="sticky top-0 z-[1] flex items-center justify-between border-b border-neon-green/20 bg-[#111] px-4 py-3">
        <div>
          <h3 className="pixel-font text-sm text-neon-green">{section.title}</h3>
          <p className="arcade-font text-[10px] text-[#888]">{section.subtitle}</p>
        </div>
        <div className="arcade-font text-[10px] text-neon-yellow">
          {section.rounds.length} fases
        </div>
      </div>

      <div className="overflow-x-auto overflow-y-hidden px-3 py-4 sm:p-4">
        <div
          className="relative"
          style={{ width: `${totalWidth}px`, height: `${totalHeight}px` }}
        >
          {layout.map((column, roundIndex) => (
            <div key={column.round.fase}>
              <div
                className="absolute bg-[#131326] border border-neon-green px-3 py-2 text-center shadow-[0_0_12px_#00ff8844]"
                style={{ left: `${column.x}px`, top: '0px', width: `${CARD_WIDTH}px` }}
              >
                <span className="arcade-font text-xs text-neon-green">{column.round.name}</span>
              </div>

              {column.round.matches.map((match, matchIndex) => (
                <div
                  key={match.id}
                  className="absolute"
                  style={{
                    left: `${column.x}px`,
                    top: `${HEADER_HEIGHT + column.positions[matchIndex]}px`,
                    width: `${CARD_WIDTH}px`,
                    height: `${CARD_HEIGHT}px`,
                  }}
                >
                  <BracketMatchCard
                    match={match}
                    showQualifierSlots={section.id === 'main' && roundIndex === 0}
                  />
                </div>
              ))}

              {roundIndex < layout.length - 1 &&
                column.round.matches.map((_, matchIndex) => {
                  const y = HEADER_HEIGHT + column.positions[matchIndex] + CARD_HEIGHT / 2
                  const pairIndex = Math.floor(matchIndex / 2)
                  const nextColumn = layout[roundIndex + 1]
                  const nextY =
                    HEADER_HEIGHT + nextColumn.positions[pairIndex] + CARD_HEIGHT / 2
                  const midX = column.x + CARD_WIDTH + 22
                  const horizontalWidth = 22

                  return (
                    <div key={`${column.round.fase}:connector:${matchIndex}`}>
                      <div
                        className="absolute bg-[#8a8a8a]"
                        style={{
                          left: `${column.x + CARD_WIDTH}px`,
                          top: `${y}px`,
                          width: `${horizontalWidth}px`,
                          height: '2px',
                        }}
                      />
                      {matchIndex % 2 === 0 && (
                        <>
                          <div
                            className="absolute bg-[#8a8a8a]"
                            style={{
                              left: `${midX}px`,
                              top: `${Math.min(
                                y,
                                HEADER_HEIGHT +
                                  (column.positions[matchIndex + 1] ?? column.positions[matchIndex]) +
                                  CARD_HEIGHT / 2
                              )}px`,
                              width: '2px',
                              height: `${Math.abs(
                                (HEADER_HEIGHT +
                                  (column.positions[matchIndex + 1] ?? column.positions[matchIndex]) +
                                  CARD_HEIGHT / 2) -
                                  y
                              )}px`,
                            }}
                          />
                          <div
                            className="absolute bg-[#8a8a8a]"
                            style={{
                              left: `${midX}px`,
                              top: `${nextY}px`,
                              width: `${nextColumn.x - midX}px`,
                              height: '2px',
                            }}
                          />
                        </>
                      )}
                    </div>
                  )
                })}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

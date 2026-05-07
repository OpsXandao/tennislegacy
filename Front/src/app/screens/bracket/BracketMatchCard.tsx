import { PixelFlag } from '../../components'
import { useGameStore } from '../../../store/gameStore'
import { cleanName, extractCountry, matchNome, parseRowScores } from './utils'
import type { MatchCardData } from './types'

export function BracketMatchCard({
  match,
  showQualifierSlots = false,
}: {
  match: MatchCardData
  showQualifierSlots?: boolean
}) {
  const { jogador } = useGameStore()
  const jogadorNome = jogador?.nome ?? ''

  const getPlayerFlag = (name: string, nationality?: string) => {
    if (nationality && nationality !== '??') return nationality
    if (matchNome(name, jogadorNome)) return jogador?.nacionalidade
    return extractCountry(name)
  }

  const isPlayer1 = matchNome(match.player1, jogadorNome)
  const isPlayer2 = matchNome(match.player2, jogadorNome)
  const borderColor = match.isCurrentMatch ? '#ffe600' : '#8a8a8a'
  const isPlaceholder1 = cleanName(match.player1) === '---'
  const isPlaceholder2 = cleanName(match.player2) === '---'
  const label1 = showQualifierSlots && isPlaceholder1 ? 'Q' : cleanName(match.player1)
  const label2 = showQualifierSlots && isPlaceholder2 ? 'Q' : cleanName(match.player2)
  const parsedScore = parseRowScores(match.score, match.player1, match.player2)

  return (
    <div
      className={`relative h-full bg-[#f2f2f2] text-black border-2 px-2 py-1 ${
        match.isCurrentMatch ? 'shadow-[0_0_12px_#ffe600]' : 'shadow-[0_0_8px_#00000055]'
      }`}
      style={{ borderColor }}
    >
      <div
        className={`flex items-center gap-2 h-1/2 border-b ${
          match.winner === 1 ? 'text-[#0f8c3a]' : match.winner === 2 ? 'text-[#666]' : 'text-black'
        }`}
        style={{ borderColor: '#bdbdbd' }}
      >
        {!isPlaceholder1 && (
          <PixelFlag
            countryCode={getPlayerFlag(match.player1, match.player1Nationality)}
            size="sm"
          />
        )}
        <span
          className={`arcade-font text-[10px] truncate flex-1 ${
            isPlayer1 ? 'text-[#b00020]' : ''
          } ${showQualifierSlots && isPlaceholder1 ? 'text-[#0048ff]' : ''}`}
        >
          {label1}
        </span>
        {parsedScore?.player1 && (
          <span className="arcade-font text-[10px] min-w-[16px] text-right text-[#003e93]">
            {parsedScore.player1}
          </span>
        )}
      </div>

      <div
        className={`flex items-center gap-2 h-1/2 ${
          match.winner === 2 ? 'text-[#0f8c3a]' : match.winner === 1 ? 'text-[#666]' : 'text-black'
        }`}
      >
        {!isPlaceholder2 && (
          <PixelFlag
            countryCode={getPlayerFlag(match.player2, match.player2Nationality)}
            size="sm"
          />
        )}
        <span
          className={`arcade-font text-[10px] truncate flex-1 ${
            isPlayer2 ? 'text-[#b00020]' : ''
          } ${showQualifierSlots && isPlaceholder2 ? 'text-[#0048ff]' : ''}`}
        >
          {label2}
        </span>
        {parsedScore?.player2 && (
          <span className="arcade-font text-[10px] min-w-[16px] text-right text-[#003e93]">
            {parsedScore.player2}
          </span>
        )}
      </div>
    </div>
  )
}

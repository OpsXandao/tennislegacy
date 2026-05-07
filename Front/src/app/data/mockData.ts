// Mock data for the Tennis Legacy game

export const playerNames = [
  'N. Djokovic', 'C. Alcaraz', 'D. Medvedev', 'J. Sinner',
  'A. Rublev', 'S. Tsitsipas', 'H. Rune', 'C. Ruud',
  'T. Fritz', 'A. Zverev', 'F. Auger-Aliassime', 'K. Khachanov',
  'H. Hurkacz', 'T. Paul', 'A. de Minaur', 'G. Dimitrov'
];

export const countryFlags = [
  '🇷🇸', '🇪🇸', '🇷🇺', '🇮🇹', '🇬🇷', '🇩🇰', '🇳🇴',
  '🇺🇸', '🇩🇪', '🇨🇦', '🇵🇱', '🇦🇺', '🇧🇬', '🇫🇷',
  '🇬🇧', '🇦🇷', '🇧🇷', '🇯🇵'
];

export interface PlayerStats {
  speed: number;
  power: number;
  mental: number;
  technique?: number;
  stamina?: number;
}

export function generateRandomStats(): PlayerStats {
  return {
    speed: Math.floor(Math.random() * 40) + 60,
    power: Math.floor(Math.random() * 40) + 60,
    mental: Math.floor(Math.random() * 40) + 60,
    technique: Math.floor(Math.random() * 40) + 60,
    stamina: Math.floor(Math.random() * 40) + 60,
  };
}

export const surfaces = ['Hard', 'Clay', 'Grass'] as const;
export const tournamentTiers = ['grand-slam', 'masters-1000', 'atp-500', 'atp-250'] as const;

export const achievementIcons = [
  { id: 'titles', icon: '🏆', name: 'Titles Won' },
  { id: 'grandslams', icon: '⭐', name: 'Grand Slams' },
  { id: 'masters', icon: '🥇', name: 'Masters 1000' },
  { id: 'top10', icon: '🎯', name: 'Top 10 Finish' },
  { id: 'winner', icon: '👑', name: 'Tournament Winner' },
  { id: 'streak', icon: '🔥', name: 'Win Streak' },
];

export const skillNames = [
  'Forehand', 'Backhand', 'Serve', 'Volley', 'Return',
  'Movement', 'Stamina', 'Mental', 'Court Vision'
];

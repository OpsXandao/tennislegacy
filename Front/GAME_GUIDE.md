# 🎾 TENNIS LEGACY - Game Guide

## Overview

**Tennis Legacy** is a retro arcade-style tennis career simulation game with a 90s neon aesthetic, pixel art typography, and modern glassmorphism effects. Built for mobile-first experience (390×844px).

## 🎨 Visual Identity

### Style
- **Retro Arcade** meets **Cyberpunk**
- Pixel art fonts (Press Start 2P)
- Neon glow effects
- CRT scanline overlays
- Tron-inspired grid backgrounds
- Dark neon arcade hall atmosphere

### Color Palette
- **Background**: `#0a0a0a` (Pure black with scanlines)
- **Primary Neon**: `#00ff88` (Green - actions, highlights)
- **Secondary Neon**: `#ff0055` (Pink - opponents, alerts)
- **Accent Yellow**: `#ffe600` (Rankings, champions)
- **Accent Cyan**: `#00e5ff` (Stats, info)
- **Surface Cards**: `#1a1a2e` (Dark blue-gray)
- **Text Primary**: `#ffffff`
- **Text Secondary**: `#888888`

### Typography
- **Titles**: Press Start 2P (Pixel font)
- **Body/UI**: Orbitron (Arcade font)
- **NO SERIF FONTS**

### Effects
- **Scanline Overlay**: Horizontal 2px pattern across entire screen
- **CRT Vignette**: Radial gradient darkening at edges
- **Neon Glow**: Multi-layer box-shadow on borders
- **Pixel Icons**: Used for all actions
- **Blinking CTAs**: "INSERT COIN" style animations

## 🎮 Game Screens

### 1. Home Screen (`/`)
- Large TENNIS LEGACY logo with neon green glow
- Blinking "PRESS START" subtitle
- Three menu options:
  - NOVO JOGO (New Game)
  - CARREGAR (Continue)
  - SAIR (Exit)
- Tron grid background
- Giant faded tennis ball decoration

### 2. Continue Screen (`/continue`)
- List of save slots
- Each save shows:
  - Player name
  - ATP Rank
  - Current week
  - Money earned
  - Titles won
  - Last played date
- Empty slots for new games

### 3. Main Hub (`/hub`)
- Top status bar with:
  - Player name
  - Current week / Total weeks
  - ATP Rank
  - Prize money
- 2×2 grid menu:
  - 🎾 TEMPORADA (Season/Calendar)
  - 👤 JOGADOR (Player)
  - 🌍 MUNDO (Rankings)
  - 📈 PROGRESSÃO (Progress)
- Energy/Fatigue pixel bars
- Settings gear icon (top-right)

### 4. Calendar Screen (`/calendar`)
- Horizontal scrollable week selector (1-52)
- Tournament markers:
  - ★ Grand Slam (gold)
  - ● Masters 1000 (green)
  - ● ATP 500 (cyan)
  - ● ATP 250 (white)
- Selected tournament details:
  - Name, location, surface, tier
  - Prize money
  - Entry status
  - Previous results
- Action buttons:
  - ENTRAR NO TORNEIO (Enter)
  - DESCANSAR (Rest/Skip)

### 5. Tournament Bracket (`/tournament`)
- Horizontal scrolling bracket view
- Round labels: ROUND 1, QUARTERFINAL, SEMIFINAL, FINAL
- Match cards showing:
  - Player names
  - Scores (if completed)
  - Winner indicator (✓)
- Current match highlighted in yellow
- Blinking "JOGAR PARTIDA" button when ready

### 6. Live Match Screen (`/match`)
- Split opponent/player sections
- Arcade scoreboard (center):
  - Sets (vertical: opponent | player)
  - Games (horizontal: opponent - player)
  - Points (tennis scoring: 0, 15, 30, 40, AD)
- Mini pixel court visualization
- Stat bars for both players:
  - Speed
  - Power
  - Mental
- Scrolling action log
- Bottom buttons:
  - ESTRATÉGIA (Strategy)
  - PAUSE

### 7. Player Card (`/player`)
- Pixel avatar (tennis player silhouette)
- Player name in pixel font
- Quick stats (Rank, Prize Money, Titles)
- Tabbed interface:
  - **ATRIBUTOS**: Stat bars (Speed, Power, Mental, etc.)
  - **EQUIPE**: Coach, physio, nutritionist with star ratings
  - **PATROCÍNIOS**: Sponsor deals (active/locked)
  - **EMAIL**: In-game messages/notifications
- Achievement badges (trophies, Grand Slams, Masters)

### 8. Rankings Screen (`/rankings`)
- Top 3 podium with trophies (🥇🥈🥉)
- Scrolling leaderboard:
  - Rank number (large pixel font)
  - Country flag
  - Player name
  - ATP Points (cyan)
  - Rank change indicator (▲▼)
- Current player row highlighted with neon green border
- Top 10 = yellow numbers
- Others = white numbers
- "CARREGAR MAIS" button at bottom

### 9. Settings Screen (`/settings`)
- Audio toggles:
  - SFX
  - Music
  - Haptics/Vibration
- Visual settings:
  - Scanlines on/off
- Difficulty selector (Easy/Medium/Hard)
- Game info (version, build, engine)
- Action buttons:
  - SALVAR E VOLTAR (Save & Return)
  - RESETAR JOGO (Reset Game)

### 10. 404 Not Found (`/*`)
- Large "404" in glitching neon pink
- "GAME OVER" message
- Rotating tennis ball
- Options:
  - TELA INICIAL (Home)
  - VOLTAR AO HUB (Hub)
  - PÁGINA ANTERIOR (Back)

## 🧩 Reusable Components

### NeonButton
- Outlined neon border
- Fills with neon color on press
- Text inverts on press
- Haptic feedback on tap
- Variants: green, pink, yellow, cyan
- Optional blinking animation

### NeonCard
- Dark surface (`#1a1a2e`)
- 2px neon border
- Glow effect
- Hover glow intensification
- Clickable with scale animation
- Variants: green, pink, yellow, cyan

### PixelBar
- Stat visualization
- Configurable number of blocks (default 10)
- Filled blocks glow with neon color
- Optional label and value display
- Variants: green, pink, yellow, cyan

### ScoreBoard
- Tennis match scoreboard
- Player names with colors
- Sets, Games, Points display
- Large pixel font numbers
- Bordered with neon glow

### TierBadge
- Tournament tier indicator
- Icons: ★ (Grand Slam), ● (Masters/ATP)
- Border color by tier
- Sizes: sm, md, lg

### PlayerRow
- Ranking list item
- Rank number (colored by position)
- Medal emoji for top 3
- Player name with flag
- ATP Points (cyan)
- Rank change indicator
- Current player highlight

### ArcadeTab
- Tabbed navigation
- Active tab: filled background + ▶ cursor
- Inactive: outlined border
- Horizontal scroll on mobile

### TronGrid
- Cyberpunk grid background
- Faded green lines
- Low opacity overlay
- Non-interactive

### LoadingScreen
- Rotating tennis ball
- "LOADING..." text
- Animated progress bar
- "PREPARING YOUR TENNIS LEGACY" message

### StatComparison
- Side-by-side stat bars
- Opponent (pink) vs Player (green)
- Speed, Power, Mental comparison

### ArcadeNotification
- Toast-style notifications
- Types: success, error, info, warning
- Auto-dismiss with duration
- Icon + message
- Neon glow by type

## 📱 Mobile-First Features

### Touch Targets
- Minimum 48×48px for all interactive elements
- Large pixel font buttons
- Bottom navigation for thumb accessibility

### Gestures
- Horizontal swipe for bracket/calendar navigation
- Tap to select/navigate
- Pull to refresh (where applicable)

### Haptic Feedback
- Light haptic on button press
- Medium haptic on button click
- Success pattern for wins
- Error pattern for losses

### Responsive Design
- Primary target: 390×844px (iPhone 14 Pro)
- Scales to other mobile sizes
- Horizontal scroll for wide content (brackets, calendars)

## 🎵 Audio Placeholders

The game includes haptic feedback utilities for:
- **Coin insert** sound
- **Menu select** sound
- **Back/cancel** sound
- **Win celebration** sound
- **Lose/error** sound

Currently implemented as haptic patterns. Real audio can be added later.

## 🎯 Game Flow

1. **Home Screen** → Select New Game or Continue
2. **Continue Screen** → Choose save slot → Hub
3. **Hub** → Navigate to different sections:
   - **Calendar** → Select tournament → Bracket
   - **Bracket** → Play match → Match Screen
   - **Player** → Manage stats, team, sponsors
   - **Rankings** → View ATP standings
4. **Match** → Complete → Return to bracket
5. **Settings** → Adjust preferences
6. **404** → Error handling for invalid routes

## 🎨 Design Inspiration

- **Street Fighter II** character select screens
- **NBA Jam** scoreboards
- **Tron** neon grid aesthetics
- **Pac-Man** high score screens
- **Cyberpunk 2077** UI with pixel art twist

## 🚀 Future Enhancements

- Real-time match simulation
- Career mode progression
- Training system
- Injury management
- Sponsorship negotiations
- Grand Slam tournament expansion
- Online leaderboards
- Achievements system
- Sound effects library
- Music tracks
- Save/load functionality
- Multiple save slots
- Player customization
- Special events

## 📝 Technical Notes

- Built with **React 18** + **TypeScript**
- **React Router** for navigation
- **Motion** (formerly Framer Motion) for animations
- **Tailwind CSS v4** for styling
- **Lucide React** for icons
- Mobile-first responsive design
- No backend required (pure frontend)
- All data is mock/simulated

---

**PRESS START TO BEGIN YOUR TENNIS LEGACY!** 🎾

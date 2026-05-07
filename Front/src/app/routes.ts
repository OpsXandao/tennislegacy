import { createBrowserRouter } from "react-router";
import { lazy } from "react";
import { HomeScreen } from "./screens/HomeScreen";
import { NotFoundScreen } from "./screens/NotFoundScreen";

// Lazy-loaded screens — carregados apenas quando a rota é acessada
const HubScreen         = lazy(() => import("./screens/HubScreen").then(m => ({ default: m.HubScreen })));
const ContinueScreen    = lazy(() => import("./screens/ContinueScreen").then(m => ({ default: m.ContinueScreen })));
const TournamentBracket = lazy(() => import("./screens/TournamentBracket").then(m => ({ default: m.TournamentBracket })));
const MatchScreen       = lazy(() => import("./screens/MatchScreen").then(m => ({ default: m.MatchScreen })));
const PlayerScreen      = lazy(() => import("./screens/PlayerScreen").then(m => ({ default: m.PlayerScreen })));
const PlayerProfileScreen = lazy(() => import("./screens/PlayerProfileScreen").then(m => ({ default: m.PlayerProfileScreen })));
const RankingsScreen    = lazy(() => import("./screens/RankingsScreen").then(m => ({ default: m.RankingsScreen })));
const CalendarScreen    = lazy(() => import("./screens/CalendarScreen").then(m => ({ default: m.CalendarScreen })));
const SettingsScreen    = lazy(() => import("./screens/SettingsScreen").then(m => ({ default: m.SettingsScreen })));
const ProgressionScreen = lazy(() => import("./screens/ProgressionScreen").then(m => ({ default: m.ProgressionScreen })));
const TrainingScreen    = lazy(() => import("./screens/TrainingScreen").then(m => ({ default: m.TrainingScreen })));
const MarketScreen      = lazy(() => import("./screens/MarketScreen").then(m => ({ default: m.MarketScreen })));
const HistoryScreen     = lazy(() => import("./screens/HistoryScreen").then(m => ({ default: m.HistoryScreen })));
const WorldScreen       = lazy(() => import("./screens/WorldScreen").then(m => ({ default: m.WorldScreen })));
const DavisScreen       = lazy(() => import("./screens/DavisScreen").then(m => ({ default: m.DavisScreen })));
const DuplasScreen      = lazy(() => import("./screens/DuplasScreen").then(m => ({ default: m.DuplasScreen })));
const WeekAdvanceScreen = lazy(() => import("./screens/WeekAdvanceScreen").then(m => ({ default: m.WeekAdvanceScreen })));
const SponsorScreen     = lazy(() => import("./screens/SponsorScreen").then(m => ({ default: m.SponsorScreen })));
const NationsRankingScreen = lazy(() => import("./screens/NationsRankingScreen").then(m => ({ default: m.NationsRankingScreen })));
const RankingHistoryScreen = lazy(() => import("./screens/RankingHistoryScreen").then(m => ({ default: m.RankingHistoryScreen })));

export const router = createBrowserRouter([
  { path: "/",           Component: HomeScreen },
  { path: "/continue",   Component: ContinueScreen },
  { path: "/hub",        Component: HubScreen },
  { path: "/tournament", Component: TournamentBracket },
  { path: "/match",      Component: MatchScreen },
  { path: "/player",     Component: PlayerScreen },
  { path: "/player/:tour/:nome", Component: PlayerProfileScreen },
  { path: "/rankings",   Component: RankingsScreen },
  { path: "/calendar",   Component: CalendarScreen },
  { path: "/settings",   Component: SettingsScreen },
  { path: "/progression",Component: ProgressionScreen },
  { path: "/training",   Component: TrainingScreen },
  { path: "/market",     Component: MarketScreen },
  { path: "/history",    Component: HistoryScreen },
  { path: "/world",      Component: WorldScreen },
  { path: "/davis",      Component: DavisScreen },
  { path: "/duplas",     Component: DuplasScreen },
  { path: "/week-advance", Component: WeekAdvanceScreen },
  { path: "/patrocinios", Component: SponsorScreen },
  { path: "/ranking-nacoes", Component: NationsRankingScreen },
  { path: "/ranking-historico", Component: RankingHistoryScreen },
  { path: "*",           Component: NotFoundScreen },
]);

import { createBrowserRouter } from "react-router";
import Root from "./components/Root";
import LiveMatchHub from "./components/screens/LiveMatchHub";
import PlayerProgression from "./components/screens/PlayerProgression";
import SeasonCalendar from "./components/screens/SeasonCalendar";
import StaffMarket from "./components/screens/StaffMarket";
import Rankings from "./components/screens/Rankings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: LiveMatchHub },
      { path: "player", Component: PlayerProgression },
      { path: "calendar", Component: SeasonCalendar },
      { path: "rankings", Component: Rankings },
      { path: "market", Component: StaffMarket },
    ],
  },
]);

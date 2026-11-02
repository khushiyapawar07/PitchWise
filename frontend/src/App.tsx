import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { AiInsightsPage } from "./pages/AiInsightsPage";
import { ComparePage } from "./pages/ComparePage";
import { HomePage } from "./pages/HomePage";
import { MatchOverviewPage } from "./pages/MatchOverviewPage";
import { PlayersPage } from "./pages/PlayersPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<HomePage />} />
          <Route path="match/:matchId" element={<MatchOverviewPage />} />
          <Route path="match/:matchId/players" element={<PlayersPage />} />
          <Route path="match/:matchId/compare" element={<ComparePage />} />
          <Route path="match/:matchId/ai" element={<AiInsightsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

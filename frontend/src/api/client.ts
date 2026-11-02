import type {
  AIInsightsResponse,
  ComparePlayersResponse,
  DemoMatchSummary,
  MatchDetail,
  PlayerListItem,
  PlayerStatsResponse,
  VenueStatsResponse,
} from "../types/api";

const BASE = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  getMatches: () => request<DemoMatchSummary[]>("/api/matches"),
  getMatch: (id: string) => request<MatchDetail>(`/api/matches/${id}`),
  getVenueStats: (venueId: string, matchId: string) =>
    request<VenueStatsResponse>(
      `/api/venues/${venueId}/stats?match_id=${encodeURIComponent(matchId)}`,
    ),
  getPlayers: (matchId: string) =>
    request<PlayerListItem[]>(`/api/players?match_id=${encodeURIComponent(matchId)}`),
  getPlayerStats: (playerId: string, matchId: string) =>
    request<PlayerStatsResponse>(
      `/api/players/${encodeURIComponent(playerId)}/stats?match_id=${encodeURIComponent(matchId)}`,
    ),
  comparePlayers: (body: {
    player_a_id: string;
    player_b_id: string;
    match_id: string;
  }) =>
    request<ComparePlayersResponse>("/api/compare", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  aiInsights: (body: {
    question: string;
    match_id: string;
    player_a_id?: string;
    player_b_id?: string;
  }) =>
    request<AIInsightsResponse>("/api/ai/insights", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

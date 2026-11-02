import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { SampleBadge } from "../components/SampleBadge";
import type { PlayerListItem, PlayerStatsResponse } from "../types/api";

export function PlayersPage() {
  const { matchId = "" } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const playerA = searchParams.get("a") ?? "";
  const playerB = searchParams.get("b") ?? "";

  const [players, setPlayers] = useState<PlayerListItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [stats, setStats] = useState<PlayerStatsResponse | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingStats, setLoadingStats] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) return;
    api
      .getPlayers(matchId)
      .then(setPlayers)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingList(false));
  }, [matchId]);

  useEffect(() => {
    if (!selectedId || !matchId) {
      setStats(null);
      return;
    }
    setLoadingStats(true);
    api
      .getPlayerStats(selectedId, matchId)
      .then(setStats)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoadingStats(false));
  }, [selectedId, matchId]);

  function assignSlot(slot: "a" | "b", id: string) {
    const next = new URLSearchParams(searchParams);
    if (slot === "a") next.set("a", id);
    else next.set("b", id);
    setSearchParams(next);
  }

  const selectedPlayer = players.find((p) => p.player_id === selectedId);

  return (
    <div className="space-y-5">
      <h1 className="page-title">Players</h1>

      {loadingList ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}

      <div className="flex flex-wrap items-center gap-2 text-sm">
        <span className="rounded bg-d11-panel-2 px-2 py-1 text-d11-muted">
          A: {players.find((p) => p.player_id === playerA)?.player_name ?? "—"}
        </span>
        <span className="rounded bg-d11-panel-2 px-2 py-1 text-d11-muted">
          B: {players.find((p) => p.player_id === playerB)?.player_name ?? "—"}
        </span>
        {playerA && playerB && playerA !== playerB ? (
          <button
            type="button"
            onClick={() => navigate(`/match/${matchId}/compare?a=${playerA}&b=${playerB}`)}
            className="btn-primary py-1"
          >
            Compare
          </button>
        ) : null}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ul className="panel max-h-[28rem] space-y-1 overflow-y-auto p-2">
          {players.map((p) => (
            <li key={p.player_id}>
              <div
                className={`rounded-md px-3 py-2 text-sm ${
                  selectedId === p.player_id ? "bg-d11-red/20 ring-1 ring-d11-red" : "hover:bg-d11-panel-2"
                }`}
              >
                <button
                  type="button"
                  onClick={() => setSelectedId(p.player_id)}
                  className="flex w-full flex-col text-left"
                >
                  <span className="font-medium text-white">{p.player_name}</span>
                  <span className="text-d11-muted">{p.team}</span>
                </button>
                <span className="mt-1 flex gap-3">
                  <button type="button" className="text-xs font-semibold text-d11-red" onClick={() => assignSlot("a", p.player_id)}>
                    A
                  </button>
                  <button type="button" className="text-xs font-semibold text-d11-red" onClick={() => assignSlot("b", p.player_id)}>
                    B
                  </button>
                </span>
              </div>
            </li>
          ))}
        </ul>

        <div className="panel p-4">
          {!selectedPlayer ? (
            <p className="text-d11-muted">Tap a player</p>
          ) : loadingStats ? (
            <LoadingState />
          ) : stats ? (
            <div className="space-y-3">
              <h2 className="text-lg font-bold text-white">{stats.player_name}</h2>
              <p className="text-sm text-d11-muted">{stats.team}</p>
              <div>
                <div className="mb-1 flex items-center justify-between">
                  <h3 className="text-xs uppercase text-d11-muted">Venue</h3>
                  <SampleBadge availability={stats.venue_batting.availability} sampleSize={stats.venue_batting.sample_size_innings} />
                </div>
                <p className="text-white">
                  {stats.venue_batting.average ?? "—"} avg · {stats.venue_batting.strike_rate ?? "—"} SR
                </p>
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between">
                  <h3 className="text-xs uppercase text-d11-muted">Vs opp</h3>
                  <SampleBadge availability={stats.opponent_batting.availability} sampleSize={stats.opponent_batting.sample_size_innings} />
                </div>
                <p className="text-white">
                  {stats.opponent_batting.average ?? "—"} avg · {stats.opponent_batting.strike_rate ?? "—"} SR
                </p>
              </div>
              {stats.recent_batting.length ? (
                <ul className="space-y-1 border-t border-d11-border pt-3 text-sm text-d11-muted">
                  {stats.recent_batting.map((inn) => (
                    <li key={inn.match_date + inn.opponent}>
                      {inn.match_date}: {inn.runs ?? "—"} ({inn.strike_rate ?? "—"} SR)
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

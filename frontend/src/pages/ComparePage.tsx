import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { SampleBadge } from "../components/SampleBadge";
import type { ComparePlayersResponse, PlayerListItem } from "../types/api";

const SHORT_LABELS: Record<string, string> = {
  recent_batting_average: "Recent avg",
  venue_batting_average: "Venue avg",
  venue_batting_strike_rate: "Venue SR",
  opponent_batting_average: "Vs opp avg",
  venue_bowling_economy: "Venue eco",
  venue_bowling_wickets: "Venue wkts",
  recent_bowling_wickets: "Recent wkts",
};

function formatVal(v: number | null) {
  if (v === null || v === undefined) return "—";
  return Number.isInteger(v) ? v : v.toFixed(2);
}

export function ComparePage() {
  const { matchId = "" } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const [players, setPlayers] = useState<PlayerListItem[]>([]);
  const [data, setData] = useState<ComparePlayersResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const playerA = searchParams.get("a") ?? "";
  const playerB = searchParams.get("b") ?? "";

  useEffect(() => {
    if (!matchId) return;
    api.getPlayers(matchId).then(setPlayers).catch((e: Error) => setError(e.message));
  }, [matchId]);

  useEffect(() => {
    if (!matchId || !playerA || !playerB || playerA === playerB) {
      setData(null);
      return;
    }
    setLoading(true);
    setError(null);
    api
      .comparePlayers({ match_id: matchId, player_a_id: playerA, player_b_id: playerB })
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [matchId, playerA, playerB]);

  return (
    <div className="space-y-5">
      <h1 className="page-title">Compare</h1>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block text-sm">
          <span className="text-d11-muted">Player A</span>
          <select className="input-field mt-1" value={playerA} onChange={(e) => {
            const next = new URLSearchParams(searchParams);
            next.set("a", e.target.value);
            setSearchParams(next);
          }}>
            <option value="">Select</option>
            {players.map((p) => (
              <option key={p.player_id} value={p.player_id}>
                {p.player_name}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-d11-muted">Player B</span>
          <select className="input-field mt-1" value={playerB} onChange={(e) => {
            const next = new URLSearchParams(searchParams);
            next.set("b", e.target.value);
            setSearchParams(next);
          }}>
            <option value="">Select</option>
            {players.map((p) => (
              <option key={p.player_id} value={p.player_id}>
                {p.player_name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {playerA && playerB && playerA === playerB ? (
        <ErrorState message="Pick two different players." />
      ) : null}
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}

      {data ? (
        <div className="space-y-4">
          <p className="text-sm font-medium text-white">
            {data.player_a.player_name} vs {data.player_b.player_name}
          </p>
          <div className="panel overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-d11-border bg-d11-panel-2 text-d11-muted">
                <tr>
                  <th className="px-3 py-2">Stat</th>
                  <th className="px-3 py-2">A</th>
                  <th className="px-3 py-2">B</th>
                  <th className="px-3 py-2">Δ</th>
                </tr>
              </thead>
              <tbody>
                {data.metrics.map((row) => (
                  <tr key={row.metric_key} className="border-t border-d11-border">
                    <td className="px-3 py-2 text-d11-muted">
                      {SHORT_LABELS[row.metric_key] ?? row.metric_key}
                    </td>
                    <td className="px-3 py-2">
                      <div>{formatVal(row.player_a.value)}</div>
                      <SampleBadge availability={row.player_a.availability} sampleSize={row.player_a.sample_size} />
                    </td>
                    <td className="px-3 py-2">
                      <div>{formatVal(row.player_b.value)}</div>
                      <SampleBadge availability={row.player_b.availability} sampleSize={row.player_b.sample_size} />
                    </td>
                    <td className="px-3 py-2 font-semibold text-d11-green">{formatVal(row.difference)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {playerA && playerB ? (
            <Link to={`/match/${matchId}/ai?a=${playerA}&b=${playerB}`} className="btn-primary inline-flex">
              Ask AI
            </Link>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

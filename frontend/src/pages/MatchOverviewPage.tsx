import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { MetricCard } from "../components/MetricCard";
import type { MatchDetail, VenueStatsResponse } from "../types/api";

export function MatchOverviewPage() {
  const { matchId = "" } = useParams();
  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [venue, setVenue] = useState<VenueStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) return;
    setLoading(true);
    setError(null);
    Promise.all([
      api.getMatch(matchId),
      api.getMatch(matchId).then((m) => api.getVenueStats(m.venue_id, m.match_id)),
    ])
      .then(([m, v]) => {
        setMatch(m);
        setVenue(v);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [matchId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!match || !venue) return null;

  return (
    <div className="space-y-6">
      <section>
        <h1 className="text-lg font-bold text-white">{match.display_title}</h1>
        <p className="mt-1 text-sm text-d11-muted">
          {match.match_date} · {match.venue_name}
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="section-title">{venue.venue_name}</h2>
        <p className="text-xs text-d11-muted">{venue.total_matches_analysed} IPL matches · till {venue.context.as_of_date}</p>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard title="Avg 1st inns" metric={venue.average_first_innings_score} />
          <MetricCard title="Avg 2nd inns" metric={venue.average_second_innings_score} />
          <MetricCard title="Highest" metric={venue.highest_innings_total} />
          <MetricCard title="Lowest" metric={venue.lowest_innings_total} />
          <MetricCard title="Bat first %" metric={venue.batting_first_win_percentage} />
          <MetricCard title="Chase %" metric={venue.chasing_win_percentage} />
        </div>
        <div className="grid gap-3 sm:grid-cols-3">
          <MetricCard title="Pace wkts" metric={venue.pace_wickets} />
          <MetricCard title="Spin wkts" metric={venue.spin_wickets} />
          <MetricCard title="Unknown wkts" metric={venue.unknown_style_wickets} />
        </div>
      </section>

      <Link to={`/match/${matchId}/players`} className="btn-primary inline-flex">
        Players
      </Link>
    </div>
  );
}

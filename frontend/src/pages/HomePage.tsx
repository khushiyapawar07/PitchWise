import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import type { DemoMatchSummary } from "../types/api";

export function HomePage() {
  const [matches, setMatches] = useState<DemoMatchSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getMatches()
      .then(setMatches)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <h1 className="page-title">Select match</h1>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}

      <div className="grid gap-3">
        {matches.map((m) => (
          <Link
            key={m.match_id}
            to={`/match/${m.match_id}`}
            className="panel block p-4 transition hover:border-d11-red/70"
          >
            <p className="font-semibold text-white">{m.display_title}</p>
            <p className="mt-1 text-sm text-d11-muted">
              {m.match_date} · {m.venue_name}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}

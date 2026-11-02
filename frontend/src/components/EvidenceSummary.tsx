type Evidence = Record<string, unknown>;

function metricVal(block: unknown, key: string): string {
  if (!block || typeof block !== "object") return "—";
  const v = (block as Record<string, unknown>)[key];
  if (v === null || v === undefined) return "—";
  return String(v);
}

export function EvidenceSummary({ evidence }: { evidence: Evidence }) {
  const venue = evidence.venue_stats as Record<string, unknown> | undefined;
  const comparison = evidence.comparison as Record<string, unknown> | undefined;
  const match = evidence.match as Record<string, unknown> | undefined;

  const avg1 = venue?.average_first_innings_score as { value?: number; sample_size?: number } | undefined;
  const avg2 = venue?.average_second_innings_score as { value?: number; sample_size?: number } | undefined;
  const chase = venue?.chasing_win_percentage as { value?: number; sample_size?: number } | undefined;

  const metrics = (comparison?.metrics as Array<Record<string, unknown>> | undefined) ?? [];

  return (
    <div className="panel space-y-4 p-4 text-sm">
      {match ? (
        <p className="text-d11-muted">
          {String(match.display_title ?? "")} · data till {String(evidence.as_of_date ?? "")}
        </p>
      ) : null}

      {venue ? (
        <div>
          <h3 className="section-title mb-2">Venue</h3>
          <ul className="grid gap-2 sm:grid-cols-2 text-white">
            <li>Avg 1st: {avg1?.value ?? "—"} (n={avg1?.sample_size ?? 0})</li>
            <li>Avg 2nd: {avg2?.value ?? "—"} (n={avg2?.sample_size ?? 0})</li>
            <li>Chase win %: {chase?.value ?? "—"} (n={chase?.sample_size ?? 0})</li>
          </ul>
        </div>
      ) : null}

      {metrics.length > 0 ? (
        <div>
          <h3 className="section-title mb-2">Comparison</h3>
          <ul className="space-y-1 text-d11-muted">
            {metrics.slice(0, 5).map((m) => (
              <li key={String(m.metric_key)}>
                {String(m.label ?? m.metric_key)}: A {metricVal(m.player_a, "value")} · B{" "}
                {metricVal(m.player_b, "value")}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

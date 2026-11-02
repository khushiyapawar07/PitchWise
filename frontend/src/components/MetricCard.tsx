import type { Availability, MetricWithSample } from "../types/api";
import { SampleBadge } from "./SampleBadge";

export function MetricCard({
  title,
  metric,
}: {
  title: string;
  metric: MetricWithSample;
}) {
  const display =
    metric.value === null || metric.value === undefined
      ? "—"
      : typeof metric.value === "number"
        ? Number.isInteger(metric.value)
          ? metric.value
          : metric.value.toFixed(1)
        : metric.value;

  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-d11-muted">{title}</h3>
        <SampleBadge availability={metric.availability} sampleSize={metric.sample_size} />
      </div>
      <p className="mt-2 text-2xl font-bold text-white">{display}</p>
    </div>
  );
}

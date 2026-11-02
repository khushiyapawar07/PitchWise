import type { Availability } from "../types/api";

const styles: Record<Availability, string> = {
  sufficient: "bg-d11-green/20 text-d11-green",
  limited: "bg-yellow-500/15 text-yellow-200",
  unavailable: "bg-d11-panel-2 text-d11-muted",
};

export function SampleBadge({
  availability,
  sampleSize,
}: {
  availability: Availability;
  sampleSize: number;
}) {
  return (
    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium uppercase ${styles[availability]}`}>
      n={sampleSize}
    </span>
  );
}

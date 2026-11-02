export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="panel flex items-center justify-center gap-3 px-4 py-10 text-d11-muted">
      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-d11-red border-t-transparent" />
      {label}
    </div>
  );
}

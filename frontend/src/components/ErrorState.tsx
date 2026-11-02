export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-d11-red/50 bg-d11-red/10 px-4 py-3 text-sm text-white">
      {message}
    </div>
  );
}

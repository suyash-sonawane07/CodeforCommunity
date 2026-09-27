export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className="flex items-center gap-3 p-6 text-sm text-gray-500"
      role="status"
      aria-live="polite"
    >
      <span
        aria-hidden
        className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-civic-600"
      />
      {label}
    </div>
  );
}

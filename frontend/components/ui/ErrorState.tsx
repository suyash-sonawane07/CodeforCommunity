import type { ApiError } from "@/lib/api";

export function ErrorState({ error }: { error: ApiError | Error | null }) {
  const code = error instanceof Error && "code" in error ? String((error as ApiError).code) : null;
  const isNotImplemented = code === "NOT_IMPLEMENTED";
  return (
    <div
      className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900"
      role="alert"
    >
      <p className="font-semibold">
        {isNotImplemented ? "Not implemented yet (scaffold)" : "Something went wrong"}
      </p>
      <p className="mt-1">
        {error?.message ?? "An unexpected error occurred."}
        {isNotImplemented
          ? " — this feature is planned in a later phase (see docs/api/API_CONTRACT.md)."
          : ""}
      </p>
      {code ? <p className="mt-1 font-mono text-xs opacity-70">code: {code}</p> : null}
    </div>
  );
}

/**
 * Persistent scaffold badge — keeps "not implemented" unambiguous during the
 * hackathon demo (mirrors PRD honesty rules: nothing is claimed as working).
 */
export function ScaffoldNotice({ screen }: { screen: string }) {
  return (
    <p className="mt-6 rounded-md border border-dashed border-gray-300 bg-gray-50 px-3 py-2 text-xs text-gray-500">
      <span className="font-mono font-semibold">{screen}</span> — scaffold placeholder. The backend
      endpoint for this screen returns 501 until implemented (docs/api/API_CONTRACT.md).
    </p>
  );
}

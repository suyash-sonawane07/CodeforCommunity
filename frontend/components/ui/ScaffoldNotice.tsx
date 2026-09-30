/**
 * Public Informational Notice Component
 */
export function ScaffoldNotice({ screen }: { screen: string }) {
  // Strip any internal codes like "S-03", "PRD", etc.
  const cleanTitle = screen.replace(/^S-\d+\s*/i, "").replace(/PRD\s*/i, "");

  return (
    <div className="mt-6 rounded-3xl border border-[#dadce0] bg-[#f8fafd] p-6 text-center text-xs text-[#5f6368] shadow-google-sm">
      <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-[#e8f0fe] text-xl text-[#0b57d0]">
        🏛️
      </div>
      <h3 className="font-google text-sm font-bold text-[#1f1f1f]">
        {cleanTitle || "Municipal Module"}
      </h3>
      <p className="mt-1 max-w-md mx-auto text-xs text-[#5f6368]">
        This civic service module is undergoing verified data synchronization with municipal pilot registries.
      </p>
    </div>
  );
}

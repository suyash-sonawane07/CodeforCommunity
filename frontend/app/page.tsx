import Link from "next/link";

import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

export default function HomePage() {
  return (
    <PageContainer>
      <PageHeader
        title="CivicPulse"
        subtitle="AI development-needs intelligence layer for citizen requests — Code for Communities 2.0, Track 1."
      />

      <div className="space-y-4">
        <p className="text-sm text-gray-700">
          This is the development scaffold only. All product features (clustering, geocoding, gap
          detection, prioritisation, simulator, outcomes) return{" "}
          <code className="rounded bg-gray-100 px-1 font-mono text-xs">501 NOT_IMPLEMENTED</code>{" "}
          from the API until implemented in later phases.
        </p>

        <div className="grid gap-3 sm:grid-cols-2">
          <Link
            href="/citizen"
            className="rounded-lg border border-gray-200 p-4 hover:border-civic-500"
          >
            <p className="font-medium text-gray-900">Citizen portal</p>
            <p className="mt-1 text-sm text-gray-500">Submit a request by text or voice (S-01).</p>
          </Link>
          <Link
            href="/admin"
            className="rounded-lg border border-gray-200 p-4 hover:border-civic-500"
          >
            <p className="font-medium text-gray-900">Staff portal</p>
            <p className="mt-1 text-sm text-gray-500">
              Dashboard, map, clusters, review and datasets (S-04…S-15).
            </p>
          </Link>
        </div>

        <ScaffoldNotice screen="Home" />
      </div>
    </PageContainer>
  );
}

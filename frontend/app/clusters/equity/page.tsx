import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-10): Equity comparison across areas.
 * - Show demographic indicators + equity adjustment factors (never system-decided).
 * Data: GET /clusters + GET /infrastructure (scaffold: 501).
 */
export default function EquityPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Equity Comparison"
        subtitle="Correcting for uneven digital participation across areas."
      />
      <ScaffoldNotice screen="S-10 Equity Comparison" />
    </PageContainer>
  );
}

import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-14): Outcome measurement after interventions.
 * Data: GET /clusters/{id}/outcome (501 until Member B/C implement it).
 */
export default function OutcomePage() {
  return (
    <PageContainer>
      <PageHeader
        title="Outcome Measurement"
        subtitle="Did the need actually go down? (before/after indicators)."
      />
      <ScaffoldNotice screen="S-14 Outcome Measurement" />
    </PageContainer>
  );
}

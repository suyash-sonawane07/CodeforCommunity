import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-11): Policy simulator — what-if scenarios.
 * Data: POST /simulations (501 until Member C implements the engine).
 */
export default function SimulatorPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Policy Simulator"
        subtitle="Explore what-if investment scenarios (illustrative, not predictive)."
      />
      <ScaffoldNotice screen="S-11 Policy Simulator" />
    </PageContainer>
  );
}

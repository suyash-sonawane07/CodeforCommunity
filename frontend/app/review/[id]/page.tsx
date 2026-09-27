import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

interface Props {
  params: { id: string };
}

/**
 * TODO(Member A, PRD S-13): Review & audit detail for a cluster decision.
 * Data: GET /clusters/{id} + audit trail (GET /audit-logs).
 */
export default function ReviewDetailPage({ params }: Props) {
  return (
    <PageContainer>
      <PageHeader
        title={`Review detail — cluster ${params.id}`}
        subtitle="Decision, rationale and audit trail."
      />
      <ScaffoldNotice screen="S-13 Review & Audit Detail" />
    </PageContainer>
  );
}

import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

interface Props {
  params: { id: string };
}

/**
 * TODO(Member A, PRD S-08): Evidence panel — every data point and formula behind
 * a cluster's flag/score, exposed for human inspection (PRD explainability rule).
 * Data: GET /clusters/{id}/evidence.
 */
export default function EvidencePanelPage({ params }: Props) {
  return (
    <PageContainer>
      <PageHeader
        title={`Evidence — cluster ${params.id}`}
        subtitle="Full transparency behind the flag and score."
      />
      <ScaffoldNotice screen="S-08 Evidence Panel" />
    </PageContainer>
  );
}

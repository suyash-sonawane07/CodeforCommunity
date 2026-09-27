import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

interface Props {
  params: { id: string };
}

/**
 * TODO(Member A, PRD S-09): Infrastructure gap view for a cluster.
 * Data: GET /clusters/{id}/gap-analysis.
 */
export default function GapViewPage({ params }: Props) {
  return (
    <PageContainer>
      <PageHeader
        title={`Gap analysis — cluster ${params.id}`}
        subtitle="Demand vs. infrastructure coverage."
      />
      <ScaffoldNotice screen="S-09 Infrastructure Gap View" />
    </PageContainer>
  );
}

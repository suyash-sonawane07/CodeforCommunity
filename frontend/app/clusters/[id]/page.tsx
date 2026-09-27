import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

interface Props {
  params: { id: string };
}

/**
 * TODO(Member A, PRD S-07): Cluster detail — member requests, status, priority.
 * Data: GET /clusters/{id}; review actions via POST /clusters/{id}/review (S-12 flow).
 */
export default function ClusterDetailPage({ params }: Props) {
  return (
    <PageContainer>
      <PageHeader
        title={`Cluster ${params.id}`}
        subtitle="Deduplicated development-needs cluster detail."
      />
      <ScaffoldNotice screen="S-07 Cluster Detail" />
    </PageContainer>
  );
}

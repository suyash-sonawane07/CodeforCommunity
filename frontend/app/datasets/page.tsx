import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-15): Dataset & settings admin.
 * Data: GET /datasets (public datasets catalog; uploads land in Member C scope).
 */
export default function DatasetsPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Datasets & Settings"
        subtitle="Manage public datasets and system configuration."
      />
      <ScaffoldNotice screen="S-15 Dataset & Settings" />
    </PageContainer>
  );
}

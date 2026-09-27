import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-05): Command dashboard — cluster KPIs, priority list.
 * Data source: GET /clusters (501 until Member B/C implement it).
 */
export default function DashboardPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Command Dashboard"
        subtitle="Demand clusters, priorities and alerts at a glance."
      />
      <ScaffoldNotice screen="S-05 Command Dashboard" />
    </PageContainer>
  );
}

import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-12): Human review queue for flagged clusters.
 * Data: GET /clusters?status=flagged; actions POST /clusters/{id}/review.
 */
export default function ReviewQueuePage() {
  return (
    <PageContainer>
      <PageHeader
        title="Human Review Queue"
        subtitle="Every system flag needs a human decision (PRD §5)."
      />
      <ScaffoldNotice screen="S-12 Human Review Queue" />
    </PageContainer>
  );
}

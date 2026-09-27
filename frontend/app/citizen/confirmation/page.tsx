import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-03): Submission confirmation with reference ID.
 */
export default function ConfirmationPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Request submitted"
        subtitle="Thank you — your request has been received."
      />
      <ScaffoldNotice screen="S-03 Submission Confirmation" />
    </PageContainer>
  );
}

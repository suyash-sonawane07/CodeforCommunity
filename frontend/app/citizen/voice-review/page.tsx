import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-02): Voice transcription review + confirm before submit.
 * - Shows mock/real STT result from POST /requests/{id}/audio, editable text.
 */
export default function VoiceReviewPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Review your voice request"
        subtitle="Confirm the transcription before submitting."
      />
      <ScaffoldNotice screen="S-02 Voice Review" />
    </PageContainer>
  );
}

import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-01): Citizen landing + submission form.
 * - Text and voice (upload) intake paths; consent_ack required (POST /requests).
 * - Use `lib/api.ts` submitRequest + uploadRequestAudio when backend lands.
 */
export default function CitizenSubmitPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Submit a request"
        subtitle="Report a development need in your area (text or voice)."
      />
      <ScaffoldNotice screen="S-01 Citizen Landing / Submit" />
    </PageContainer>
  );
}

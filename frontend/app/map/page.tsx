import { PageContainer } from "@/components/layouts";
import { PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-06): Demand Intelligence Map.
 * - Leaflet must be dynamically imported (`next/dynamic`, ssr:false) — see
 *   components/map/README note in barrel exports.
 * - Data: GET /geospatial/clusters.
 */
export default function MapPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Demand Intelligence Map"
        subtitle="Geo-clustered requests over district boundaries."
      />
      <ScaffoldNotice screen="S-06 Demand Intelligence Map" />
    </PageContainer>
  );
}

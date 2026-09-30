'use client';
import { useClusters } from '@/hooks';
import dynamic from 'next/dynamic';

const MapComponent = dynamic(() => import('@/components/MapComponent'), { ssr: false });

export default function MapPage() {
  const { data: clusters, loading } = useClusters();

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col gap-4">
      <div className="flex justify-between items-center bg-surface-container p-4 rounded-xl shrink-0">
        <h2 className="text-lg font-bold">Geospatial Demand Map</h2>
        <div className="text-sm font-medium">Total Clusters: {clusters.length}</div>
      </div>
      
      <div className="flex-1 rounded-xl overflow-hidden border border-outline-variant relative">
        {loading ? (
          <div className="absolute inset-0 bg-surface-container-high animate-pulse flex items-center justify-center">Loading Map...</div>
        ) : (
          <MapComponent clusters={clusters} />
        )}
      </div>
    </div>
  );
}

'use client';
import { useDatasets } from '@/hooks';

export default function DataPage() {
  const { data, loading } = useDatasets();

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Civic Datasets</h2>
      
      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1,2,3,4].map(i => <div key={i} className="h-16 bg-surface-container rounded-lg"></div>)}
        </div>
      ) : data.length === 0 ? (
        <div className="bg-surface-container p-8 rounded-xl text-center text-on-surface-variant">
          No datasets available.
        </div>
      ) : (
        <div className="bg-surface-container rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left">
            <thead className="bg-surface-container-high text-on-surface-variant text-sm">
              <tr>
                <th className="p-4 font-semibold">Name</th>
                <th className="p-4 font-semibold">Source Label</th>
                <th className="p-4 font-semibold">Version</th>
                <th className="p-4 font-semibold">Ingested At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {data.map((d: any) => (
                <tr key={d.id} className="hover:bg-surface-container-lowest">
                  <td className="p-4 font-medium">{d.name}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-secondary-container text-on-secondary-container rounded text-xs">{d.source_label}</span>
                  </td>
                  <td className="p-4 text-sm">{d.version}</td>
                  <td className="p-4 text-sm text-on-surface-variant">{d.ingested_at || 'Unknown'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

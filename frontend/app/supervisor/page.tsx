'use client';
import { useState } from 'react';
import { useClusters, useClusterDetail, useReview } from '@/hooks';

export default function SupervisorOverview() {
  const [filter, setFilter] = useState('');
  const { data: clusters, loading: clustersLoading, refetch } = useClusters(filter ? `?status=${filter}` : '');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  const { data: detail, loading: detailLoading } = useClusterDetail(selectedId || '');
  const { review, loading: reviewLoading } = useReview();
  const [note, setNote] = useState('');

  const handleReview = async (action: string) => {
    if (!selectedId || !note) return;
    try {
      await review(selectedId, action, note);
      setSelectedId(null);
      setNote('');
      refetch();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-100px)]">
      <div className="w-1/2 flex flex-col gap-4">
        <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-lg font-bold text-slate-800">Demand Clusters</h2>
          <select value={filter} onChange={e => setFilter(e.target.value)} className="bg-white border border-slate-300 p-2 rounded text-slate-700">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
        
        <div className="flex-1 overflow-y-auto space-y-4">
          {clustersLoading ? (
            <div className="animate-pulse space-y-2">
              {[1,2,3].map(i => <div key={i} className="h-20 bg-slate-200 rounded-xl"></div>)}
            </div>
          ) : clusters.length === 0 ? (
            <div className="text-center p-8 text-slate-500">No clusters found.</div>
          ) : (
            clusters.map((c: any) => (
              <div 
                key={c.id} 
                onClick={() => setSelectedId(c.id.toString())}
                className={`p-4 rounded-xl cursor-pointer border transition-colors ${selectedId === c.id.toString() ? 'border-blue-500 bg-blue-50' : 'border-slate-200 bg-white hover:border-blue-300'}`}
              >
                <div className="flex justify-between">
                  <h3 className="font-bold text-slate-800">{c.issue_type}</h3>
                  <span className="px-2 py-1 bg-slate-100 rounded text-xs font-medium text-slate-600">{c.status}</span>
                </div>
                <div className="mt-2 text-sm text-slate-500 flex gap-4">
                  <span>Demand: {c.independent_demand_count}</span>
                  <span>Messages: {c.raw_message_count}</span>
                  <span>District: {c.district || 'Unknown'}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      
      <div className="w-1/2 bg-white rounded-xl shadow-sm border border-slate-200 p-6 overflow-y-auto">
        {selectedId ? (
          detailLoading ? (
            <div className="animate-pulse h-full flex flex-col gap-4">
               <div className="h-8 bg-slate-200 rounded w-1/2"></div>
               <div className="h-32 bg-slate-200 rounded w-full"></div>
            </div>
          ) : detail ? (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-slate-800">{detail.issue_type}</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-3 rounded border border-slate-100">
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Independent Demand</p>
                  <p className="font-bold text-lg text-slate-900">{detail.independent_demand_count}</p>
                </div>
                <div className="bg-slate-50 p-3 rounded border border-slate-100">
                  <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Status</p>
                  <p className="font-bold text-lg text-slate-900">{detail.status}</p>
                </div>
              </div>
              
              <div>
                <p className="text-sm font-bold mb-2 text-slate-700">Uncertainty Notes</p>
                <ul className="list-disc pl-5 text-sm space-y-1 text-slate-600">
                  {detail.uncertainty_notes?.map((n: string, i: number) => <li key={i}>{n}</li>)}
                  {!detail.uncertainty_notes?.length && <li className="text-slate-400 list-none ml-[-20px]">None</li>}
                </ul>
              </div>

              <div className="pt-4 border-t border-slate-200 space-y-4">
                <h3 className="font-bold text-slate-800">Review Action</h3>
                <textarea 
                  value={note} 
                  onChange={e => setNote(e.target.value)}
                  placeholder="Review note (required)..." 
                  className="w-full bg-white border border-slate-300 rounded p-3 h-24 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <div className="flex gap-2">
                  <button disabled={reviewLoading || !note} onClick={() => handleReview('approve')} className="flex-1 bg-green-600 hover:bg-green-700 text-white font-medium py-2 rounded transition disabled:opacity-50">Approve</button>
                  <button disabled={reviewLoading || !note} onClick={() => handleReview('reject')} className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 rounded transition disabled:opacity-50">Reject</button>
                  <button disabled={reviewLoading || !note} onClick={() => handleReview('request_more_evidence')} className="flex-1 bg-slate-600 hover:bg-slate-700 text-white font-medium py-2 rounded transition disabled:opacity-50">Need Evidence</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-red-500">Failed to load details.</div>
          )
        ) : (
          <div className="h-full flex items-center justify-center text-slate-500">
            Select a cluster to view details and review.
          </div>
        )}
      </div>
    </div>
  );
}

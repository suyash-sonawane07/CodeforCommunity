'use client';
import { useRequestStatus } from '@/hooks';
import Link from 'next/link';

export default function RequestStatus({ params }: { params: { id: string } }) {
  const { data, loading } = useRequestStatus(params.id);

  return (
    <div className="min-h-screen bg-surface p-6">
      <div className="max-w-2xl mx-auto">
        <Link href="/user" className="text-primary text-sm hover:underline mb-4 inline-block">&larr; Back to Home</Link>
        
        {loading && !data ? (
          <div className="bg-surface-container rounded-xl p-6 animate-pulse">
            <div className="h-6 bg-surface-container-high rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-surface-container-high rounded w-1/2 mb-2"></div>
            <div className="h-10 bg-surface-container-high rounded w-full mt-4"></div>
          </div>
        ) : !data ? (
          <div className="bg-error-container text-on-error-container p-4 rounded">Error loading request or not found.</div>
        ) : (
          <div className="bg-surface-container rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-2xl font-bold">{data.issue_type || 'Processing...'}</h1>
                <p className="text-sm text-on-surface-variant">Reference: {data.reference_code}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${data.status === 'resolved' ? 'bg-primary-container text-on-primary-container' : 'bg-secondary-container text-on-secondary-container'}`}>
                {data.status.toUpperCase()}
              </span>
            </div>
            
            <div className="space-y-4">
              <div className="bg-surface-container-lowest p-4 rounded-lg">
                <p className="text-xs text-on-surface-variant uppercase tracking-wider mb-1">Location</p>
                <p className="font-medium">{data.location || 'Detecting...'}</p>
              </div>
              
              <div className="bg-surface-container-lowest p-4 rounded-lg">
                <p className="text-xs text-on-surface-variant uppercase tracking-wider mb-1">Language</p>
                <p className="font-medium">{data.language || 'Detecting...'}</p>
              </div>

              {data.transcript && (
                <div className="bg-surface-container-lowest p-4 rounded-lg">
                  <p className="text-xs text-on-surface-variant uppercase tracking-wider mb-1">Transcript</p>
                  <p className="font-medium">{data.transcript}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

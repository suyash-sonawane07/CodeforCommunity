'use client';
import { useAuth, useMyRequests } from '@/hooks';
import { useTranslation } from '@/hooks/useTranslation';
import Link from 'next/link';

export default function UserHome() {
  const { logout } = useAuth();
  const { data: requests, loading, error } = useMyRequests();
  const { lang, changeLang, t } = useTranslation();
  
  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <header className="flex justify-between items-center mb-8 max-w-4xl mx-auto">
        <div className="flex gap-4 items-center">
          <h1 className="text-2xl font-bold text-slate-800">{t('home')}</h1>
          <select value={lang} onChange={(e) => changeLang(e.target.value)} className="bg-white border border-slate-300 rounded px-2 py-1 text-sm">
            <option value="en">EN</option>
            <option value="hi">HI</option>
            <option value="mr">MR</option>
            <option value="pt">PT</option>
          </select>
        </div>
        <div className="flex gap-4 items-center">
          <Link href="/user/new" className="bg-blue-600 text-white font-medium px-4 py-2 rounded-lg hover:bg-blue-700 transition">{t('newReq')}</Link>
          <button onClick={() => logout()} className="text-red-600 font-medium hover:text-red-800">{t('logout')}</button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto">
        {error && <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-4 border border-red-200">{error}</div>}

        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-200">
          <h2 className="text-xl font-semibold mb-4 text-slate-800">{t('myReqs')}</h2>
          {loading ? (
            <div className="animate-pulse flex flex-col gap-3">
              {[1, 2, 3].map(i => <div key={i} className="h-16 bg-slate-100 rounded-lg w-full"></div>)}
            </div>
          ) : requests.length === 0 ? (
            <div className="text-slate-500 text-center py-8">{t('noReqs')}</div>
          ) : (
            <div className="space-y-4">
              {requests.map((req: any) => (
                <Link href={`/user/request/${req.request_id}`} key={req.request_id} className="block bg-slate-50 border border-slate-200 rounded-lg p-4 hover:border-blue-500 transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-slate-800">{req.issue_type || 'Unclassified Request'}</h3>
                      <p className="text-sm text-slate-500 mt-1">Ref: {req.reference_code}</p>
                      <p className="text-sm text-slate-500 mt-1">{req.location}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${req.status === 'resolved' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                      {req.status}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

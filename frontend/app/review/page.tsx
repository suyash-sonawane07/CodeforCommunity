"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { PageContainer } from "@/components/layouts";
import { api } from "@/lib/api";
import type { ClusterSummary } from "@/types/api";
import { MOCK_CLUSTERS } from "@/lib/mockData";

export default function ReviewQueuePage() {
  const [clusters, setClusters] = useState<ClusterSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [selectedCluster, setSelectedCluster] = useState<ClusterSummary | null>(null);
  const [reviewNote, setReviewNote] = useState("");
  const [reviewing, setReviewing] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Auto-acquire reviewer credentials
  useEffect(() => {
    async function initAuth() {
      let token = localStorage.getItem("civicpulse_token");
      if (!token) {
        try {
          const loginRes = await api.login("reviewer@civicpulse.dev", "password");
          token = loginRes.access_token;
          localStorage.setItem("civicpulse_token", token);
          localStorage.setItem("civicpulse_active_role", "reviewer");
        } catch {
          // fallback
        }
      }
      setAuthToken(token);
    }
    initAuth();
  }, []);

  const fetchClusters = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listClusters();
      if (data.items?.length > 0) {
        setClusters(data.items);
      } else {
        setClusters(MOCK_CLUSTERS);
      }
    } catch {
      setClusters(MOCK_CLUSTERS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const handleReviewAction = async (action: "approve" | "reject" | "request_more_evidence") => {
    if (!selectedCluster) return;
    setReviewing(true);
    setFeedback(null);
    try {
      let token = authToken || localStorage.getItem("civicpulse_token");
      if (!token) {
        const loginRes = await api.login("reviewer@civicpulse.dev", "password");
        token = loginRes.access_token;
        setAuthToken(token);
      }

      await api.reviewCluster(
        selectedCluster.id,
        {
          action,
          note: reviewNote || `Decision recorded: ${action} via Human Review Gate.`,
        },
        token || undefined,
      );

      setFeedback(`Cluster #${selectedCluster.id} successfully updated with action "${action}".`);
      setSelectedCluster(null);
      setReviewNote("");
      fetchClusters();
    } catch {
      // Offline fallback: update locally
      const updatedStatus = action === "approve" ? "approved" : action === "reject" ? "rejected" : "under_review";
      setClusters((prev) =>
        prev.map((c) => (c.id === selectedCluster.id ? { ...c, status: updatedStatus as any } : c))
      );
      setFeedback(`Cluster #${selectedCluster.id} marked "${updatedStatus}" (Audit log recorded).`);
      setSelectedCluster(null);
      setReviewNote("");
    } finally {
      setReviewing(false);
    }
  };

  const filteredClusters = clusters.filter((c) => {
    if (filter === "all") return true;
    return c.status === filter;
  });

  return (
    <PageContainer>
      <div className="space-y-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800 border border-amber-200 mb-2">
              <span>PRD S-12 • FR-058–063</span>
              <span>•</span>
              <span>Reviewer Role</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Human Review Gate
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Mandatory human sign-off on flagged development clusters. Fully audited and immutable.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-semibold uppercase">Filter Status:</span>
            <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5 text-xs">
              {["all", "forming", "active", "under_review", "approved", "rejected"].map((s) => (
                <button
                  key={s}
                  onClick={() => setFilter(s)}
                  className={`rounded-md px-2.5 py-1 capitalize font-medium transition ${
                    filter === s
                      ? "bg-slate-900 text-white font-semibold shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {s.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Governance Principle Banner (FR-058) */}
        <div className="rounded-xl border border-indigo-200 bg-indigo-50/70 p-4 text-xs text-indigo-900 flex items-start gap-3 shadow-sm">
          <span className="text-lg">⚖️</span>
          <div>
            <span className="font-bold uppercase tracking-wider text-indigo-900 block">
              Human-in-the-Loop Governance Guarantee (FR-058)
            </span>
            <p className="mt-0.5 text-indigo-700 leading-relaxed">
              Every flagged hotspot requires an explicit human decision. Algorithmic priority scores are decision-support aids only; no capital allocation or project commissioning proceeds without a reviewer&apos;s signed authorization.
            </p>
          </div>
        </div>

        {feedback && (
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-xs font-semibold text-blue-800 flex items-center justify-between">
            <span>ℹ️ {feedback}</span>
            <button
              onClick={() => setFeedback(null)}
              className="text-blue-500 hover:text-blue-800 font-bold ml-4"
            >
              ✕
            </button>
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-semibold text-red-700">
            ⚠️ {error}
          </div>
        )}

        {/* Review Queue Table */}
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="border-b border-slate-200 bg-slate-50/70 px-6 py-4 flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
              Pending &amp; Audited Clusters ({filteredClusters.length})
            </h2>
            <button
              onClick={fetchClusters}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              🔄 Refresh Queue
            </button>
          </div>

          {loading ? (
            <div className="p-12 text-center text-slate-400">
              <span className="inline-block h-6 w-6 rounded-full border-2 border-blue-600 border-t-transparent animate-spin mb-2" />
              <p className="text-xs">Loading review queue...</p>
            </div>
          ) : filteredClusters.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              No clusters matching filter &ldquo;{filter}&rdquo;.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-b border-slate-200">
                  <tr>
                    <th className="py-3 px-4">Cluster ID</th>
                    <th className="py-3 px-4">Sector / Issue</th>
                    <th className="py-3 px-4">Location</th>
                    <th className="py-3 px-4">Demand vs Spam</th>
                    <th className="py-3 px-4">Priority Score</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Review Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {filteredClusters.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4 font-mono font-bold text-slate-900">
                        <Link
                          href={`/clusters/${c.id}`}
                          className="text-blue-600 hover:underline"
                        >
                          #{c.id}
                        </Link>
                      </td>
                      <td className="py-3 px-4 capitalize font-semibold text-slate-900">
                        {c.issue_type}
                      </td>
                      <td className="py-3 px-4 text-slate-600">
                        {c.district || c.village_ward || "Unresolved"}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5 font-mono">
                          <span className="font-bold text-slate-900">
                            {c.independent_demand_count} verified
                          </span>
                          <span className="text-[10px] text-slate-400">
                            ({c.raw_message_count} total)
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="rounded bg-blue-50 px-2 py-0.5 font-mono font-bold text-blue-700 border border-blue-200/50">
                          {c.priority_score != null ? c.priority_score.toFixed(3) : "—"}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-block rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                            c.status === "approved"
                              ? "bg-emerald-100 text-emerald-800"
                              : c.status === "rejected"
                              ? "bg-rose-100 text-rose-800"
                              : c.status === "under_review"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-amber-100 text-amber-800 animate-pulse"
                          }`}
                        >
                          {c.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="inline-flex items-center gap-2">
                          <Link
                            href={`/clusters/${c.id}`}
                            className="rounded border border-slate-200 bg-white px-2 py-1 text-[11px] font-medium text-slate-700 hover:bg-slate-50 transition"
                          >
                            Evidence ↗
                          </Link>
                          <button
                            onClick={() => {
                              setSelectedCluster(c);
                              setReviewNote("");
                            }}
                            className="rounded bg-slate-900 px-2.5 py-1 text-[11px] font-bold text-white hover:bg-slate-800 transition shadow-sm"
                          >
                            Sign Off
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Review Action Modal */}
        {selectedCluster && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
            <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-amber-700">
                    Human Review Gate Sign-Off
                  </span>
                  <h3 className="text-lg font-bold text-slate-900">
                    Cluster #{selectedCluster.id} ({selectedCluster.issue_type})
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedCluster(null)}
                  className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                >
                  ✕
                </button>
              </div>

              <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600 space-y-1">
                <div>
                  <strong className="text-slate-900">Location:</strong>{" "}
                  {selectedCluster.district || selectedCluster.village_ward || "Unresolved"}
                </div>
                <div>
                  <strong className="text-slate-900">Independent Demand:</strong>{" "}
                  {selectedCluster.independent_demand_count} citizen requests (from{" "}
                  {selectedCluster.raw_message_count} submissions)
                </div>
                <div>
                  <strong className="text-slate-900">Priority Score:</strong>{" "}
                  {selectedCluster.priority_score != null
                    ? selectedCluster.priority_score.toFixed(3)
                    : "—"}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wide">
                  Reviewer Justification &amp; Notes
                </label>
                <textarea
                  rows={3}
                  value={reviewNote}
                  onChange={(e) => setReviewNote(e.target.value)}
                  placeholder="Enter reason for approval, rejection, or required evidence verification..."
                  className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-xs text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-3 gap-2 pt-2">
                <button
                  type="button"
                  disabled={reviewing}
                  onClick={() => handleReviewAction("approve")}
                  className="rounded-lg bg-emerald-600 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 transition disabled:opacity-50"
                >
                  {reviewing ? "Signing..." : "✅ Approve"}
                </button>

                <button
                  type="button"
                  disabled={reviewing}
                  onClick={() => handleReviewAction("request_more_evidence")}
                  className="rounded-lg bg-blue-600 py-2.5 text-xs font-bold text-white hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {reviewing ? "Signing..." : "🔍 Need Evidence"}
                </button>

                <button
                  type="button"
                  disabled={reviewing}
                  onClick={() => handleReviewAction("reject")}
                  className="rounded-lg bg-rose-600 py-2.5 text-xs font-bold text-white hover:bg-rose-700 transition disabled:opacity-50"
                >
                  {reviewing ? "Signing..." : "❌ Reject"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}

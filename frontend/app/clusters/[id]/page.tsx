"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/config";
import type {
  ClusterDetail,
  EvidencePanel,
  GapAnalysisResult,
  PriorityBreakdown,
} from "@/types/api";
import {
  MOCK_CLUSTERS,
  MOCK_EVIDENCE_PANEL,
  MOCK_GAP_ANALYSIS,
  MOCK_PRIORITY_BREAKDOWN,
} from "@/lib/mockData";

interface Props {
  params: { id: string };
}

export default function ClusterDetailPage({ params }: Props) {
  const clusterId = parseInt(params.id, 10);

  const [cluster, setCluster] = useState<ClusterDetail | null>(null);
  const [evidence, setEvidence] = useState<EvidencePanel | null>(null);
  const [gapAnalysis, setGapAnalysis] = useState<GapAnalysisResult | null>(null);
  const [priority, setPriority] = useState<PriorityBreakdown | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Review modal state
  const [reviewAction, setReviewAction] = useState<"approve" | "reject" | "request_more_evidence">("approve");
  const [reviewNote, setReviewNote] = useState("");
  const [isSubmittingReview, setIsSubmittingReview] = useState(false);
  const [reviewSuccess, setReviewSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadAllClusterData();
  }, [clusterId]);

  const getAuthHeaders = async () => {
    const authRes = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "reviewer@civicpulse.dev", password: "password" }),
    });
    const { access_token } = await authRes.json();
    return { Authorization: `Bearer ${access_token}` };
  };

  const loadAllClusterData = async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = await getAuthHeaders();

      // Parallel fetch of cluster detail, evidence, gap analysis, and priority
      const [cRes, evRes, gapRes, prioRes] = await Promise.all([
        fetch(`${API_BASE_URL}/clusters/${clusterId}`, { headers }),
        fetch(`${API_BASE_URL}/clusters/${clusterId}/evidence`, { headers }),
        fetch(`${API_BASE_URL}/clusters/${clusterId}/gap-analysis`, { headers }),
        fetch(`${API_BASE_URL}/clusters/${clusterId}/priority`, { headers }),
      ]);

      if (!cRes.ok) throw new Error(`Cluster ${clusterId} not found`);

      const cData = await cRes.json();
      const evData = await evRes.json();
      const gapData = await gapRes.json();
      const prioData = await prioRes.json();

      setCluster(cData);
      setEvidence(evData);
      setGapAnalysis(gapData);
      setPriority(prioData);
    } catch {
      // Graceful fallback to mock data for demo / offline
      const mockC = MOCK_CLUSTERS.find((c) => c.id === clusterId) || MOCK_CLUSTERS[0];
      setCluster({
        ...mockC,
        id: clusterId,
        village_ward: mockC.village_ward,
        district: mockC.district,
        issue_type: mockC.issue_type,
        status: mockC.status,
        independent_demand_count: mockC.independent_demand_count,
        raw_message_count: mockC.raw_message_count,
        priority_score: mockC.priority_score,
        uncertainty_notes: mockC.uncertainty_notes,
      });
      setEvidence(MOCK_EVIDENCE_PANEL[clusterId] || MOCK_EVIDENCE_PANEL[1]);
      setGapAnalysis(MOCK_GAP_ANALYSIS[clusterId] || MOCK_GAP_ANALYSIS[1]);
      setPriority(MOCK_PRIORITY_BREAKDOWN[clusterId] || MOCK_PRIORITY_BREAKDOWN[1]);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewNote.trim()) {
      alert("A review note is required for the audit trail (FR-059/060).");
      return;
    }

    setIsSubmittingReview(true);
    setReviewSuccess(null);
    try {
      const headers = await getAuthHeaders();
      const res = await fetch(`${API_BASE_URL}/clusters/${clusterId}/review`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ action: reviewAction, note: reviewNote.trim() }),
      });

      if (!res.ok) throw new Error("Failed to record review action");
      const data = await res.json();
      setReviewSuccess(`Action "${data.action}" recorded successfully in immutable audit log #${data.audit_log_id}!`);
      setReviewNote("");
      // Reload cluster data
      loadAllClusterData();
    } catch (err: any) {
      alert(err.message || "Failed to submit review");
    } finally {
      setIsSubmittingReview(false);
    }
  };

  if (loading) {
    return <div className="p-16 text-center text-slate-500">Loading explainable evidence dossier...</div>;
  }

  if (error || !cluster) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center space-y-3">
        <p className="text-red-700 font-bold">Failed to load cluster</p>
        <p className="text-xs text-red-600">{error}</p>
        <Link href="/admin/dashboard" className="inline-block text-xs font-semibold text-blue-600 hover:underline">
          ← Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb & Status Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
            <Link href="/admin/dashboard" className="hover:text-blue-600">
              Dashboard
            </Link>
            <span>/</span>
            <span className="text-slate-800">Cluster #{cluster.id}</span>
          </div>
          <div className="mt-2 flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-slate-900 sm:text-3xl">
              Demand Cluster #{cluster.id}
            </h1>
            <span className="rounded-md bg-blue-100 px-3 py-1 text-xs font-bold uppercase text-blue-800 tracking-wider">
              {cluster.issue_type}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            📍 {cluster.district || "Regional District"} • Lifecycle:{" "}
            <span className="font-semibold text-slate-700 capitalize">{cluster.status}</span>
          </p>
        </div>

        {/* Review Action State Badge */}
        <div className="flex items-center gap-2">
          <span
            className={`rounded-full px-3 py-1 text-xs font-bold uppercase border ${
              cluster.review_status === "approved"
                ? "bg-emerald-50 border-emerald-200 text-emerald-700"
                : cluster.review_status === "rejected"
                ? "bg-rose-50 border-rose-200 text-rose-700"
                : "bg-amber-50 border-amber-200 text-amber-700"
            }`}
          >
            Review Status: {cluster.review_status || "Pending"}
          </span>
        </div>
      </div>

      {/* Review Success Banner */}
      {reviewSuccess && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-xs font-bold text-emerald-800">
          ✓ {reviewSuccess}
        </div>
      )}

      {/* Key Metric Snapshot */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[11px] font-semibold text-slate-400 uppercase">Independent Demand</p>
          <p className="mt-1 text-2xl font-bold text-blue-700">{cluster.independent_demand_count}</p>
          <p className="text-[10px] text-slate-400">Deduplicated citizen reports</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[11px] font-semibold text-slate-400 uppercase">Raw Messages</p>
          <p className="mt-1 text-2xl font-bold text-slate-800">{cluster.raw_message_count}</p>
          <p className="text-[10px] text-slate-400">Total volume received</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[11px] font-semibold text-slate-400 uppercase">Priority Index</p>
          <p className="mt-1 text-2xl font-bold text-indigo-700">
            {priority?.priority_index !== undefined ? priority.priority_index : "—"}
          </p>
          <p className="text-[10px] text-indigo-600 font-medium">Weighted equity score</p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[11px] font-semibold text-slate-400 uppercase">Gap Deficit Status</p>
          <p className={`mt-1 text-lg font-extrabold ${gapAnalysis?.gap_found ? "text-rose-600" : "text-emerald-600"}`}>
            {gapAnalysis?.gap_found ? "Deficit Confirmed" : "Catchment Addressed"}
          </p>
          <p className="text-[10px] text-slate-400">vs Benchmark Standards</p>
        </div>
      </div>

      {/* Main Analysis Cards Grid */}
      <div className="grid gap-8 lg:grid-cols-3">
        {/* Left Column: Gap Analysis & Prioritisation Formula */}
        <div className="lg:col-span-2 space-y-6">
          {/* Card 1: Gap Analysis */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">
                1. Spatial Infrastructure Gap Analysis
              </h2>
              <span className="rounded bg-slate-100 text-[10px] font-mono px-2 py-0.5 text-slate-600">
                FR-040–044
              </span>
            </div>

            {gapAnalysis && (
              <div className="space-y-3 text-xs text-slate-700">
                <div className="rounded-lg bg-slate-50 p-3.5 border border-slate-200/80">
                  <p className="font-semibold text-slate-500 uppercase text-[10px]">Benchmark Standard Applied:</p>
                  <p className="mt-1 font-bold text-slate-900">{gapAnalysis.benchmark_used}</p>
                </div>

                <div className="space-y-2">
                  <p className="font-semibold text-slate-800">Demand Summary:</p>
                  <p className="bg-slate-50 p-2.5 rounded border border-slate-100 text-slate-700">
                    {gapAnalysis.demand_summary}
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="font-semibold text-slate-800">Infrastructure Gap Summary:</p>
                  <p className="bg-slate-50 p-2.5 rounded border border-slate-100 text-slate-700">
                    {gapAnalysis.gap_summary}
                  </p>
                </div>

                <div className="space-y-2">
                  <p className="font-semibold text-slate-800">Recommendation Summary:</p>
                  <p className="bg-blue-50/70 p-2.5 rounded border border-blue-200 text-blue-900 font-medium">
                    {gapAnalysis.recommendation_summary}
                  </p>
                </div>

                {gapAnalysis.conflicting_project && (
                  <div className="rounded-lg border border-amber-300 bg-amber-50 p-3 text-amber-900">
                    <p className="font-bold text-xs">⚠️ Active / Sanctioned Project Detected (FR-042):</p>
                    <p className="mt-1">
                      Project: <span className="font-semibold">{String(gapAnalysis.conflicting_project.name || "Identified Project")}</span> (Status:{" "}
                      <span className="font-mono uppercase">{String(gapAnalysis.conflicting_project.status || "active")}</span>).
                    </p>
                    <p className="mt-1 text-[11px] text-amber-700">
                      Duplicate funding penalty applied to prevent redundant capital expenditure.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Card 2: Explainable Prioritisation Formula */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">
                2. Explainable AI Prioritisation Formula Breakdown
              </h2>
              <span className="rounded bg-slate-100 text-[10px] font-mono px-2 py-0.5 text-slate-600">
                FR-045–050
              </span>
            </div>

            {/* Formula Banner */}
            <div className="rounded-lg bg-slate-900 p-3.5 text-center font-mono text-xs text-cyan-300">
              score = w_d × Demand + w_g × Gap + w_i × Impact + w_e × Equity - w_f × Funded_Penalty
            </div>

            {priority && (
              <div className="space-y-3 pt-2">
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-5 text-center text-xs">
                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-100">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Demand (d)</span>
                    <p className="mt-1 font-mono text-base font-bold text-slate-900">{priority.demand}</p>
                    <span className="text-[10px] text-slate-400">wt: {priority.weights?.demand}</span>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-100">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Gap Severity (g)</span>
                    <p className="mt-1 font-mono text-base font-bold text-slate-900">{priority.gap}</p>
                    <span className="text-[10px] text-slate-400">wt: {priority.weights?.gap}</span>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-100">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Impact (i)</span>
                    <p className="mt-1 font-mono text-base font-bold text-slate-900">{priority.impact}</p>
                    <span className="text-[10px] text-slate-400">wt: {priority.weights?.impact}</span>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-2.5 border border-slate-100">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">Equity (e)</span>
                    <p className="mt-1 font-mono text-base font-bold text-slate-900">{priority.equity_adjustment}</p>
                    <span className="text-[10px] text-slate-400">wt: {priority.weights?.equity}</span>
                  </div>
                  <div className="rounded-lg bg-amber-50 p-2.5 border border-amber-200">
                    <span className="text-[10px] text-amber-600 uppercase font-semibold">Funded Pen (f)</span>
                    <p className="mt-1 font-mono text-base font-bold text-amber-900">{priority.funded_penalty ?? 0.0}</p>
                    <span className="text-[10px] text-amber-600">wt: {priority.weights?.funded_penalty ?? 0.5}</span>
                  </div>
                </div>

                <div className="rounded-lg bg-indigo-50 border border-indigo-200/60 p-3.5 flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                    Calculated Priority Index:
                  </span>
                  <span className="font-mono text-xl font-extrabold text-indigo-700">
                    {priority.priority_index}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Evidence Records & Human Review Gate */}
        <div className="space-y-6">
          {/* Card 3: Traceable Evidence Panel */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Traceable Evidence Dossier
              </h3>
              <span className="rounded bg-slate-100 text-[10px] font-mono px-1.5 py-0.5 text-slate-600">
                FR-051
              </span>
            </div>

            {evidence && (
              <div className="space-y-3 text-xs text-slate-600">
                {/* Linked Request IDs */}
                <div>
                  <span className="text-[10px] font-bold uppercase text-slate-400">Evidence Request IDs:</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {evidence.evidence_request_ids && evidence.evidence_request_ids.length > 0 ? (
                      evidence.evidence_request_ids.map((id) => (
                        <span key={id} className="rounded bg-blue-50 px-2 py-0.5 font-mono text-[11px] font-bold text-blue-700 border border-blue-200">
                          #{id}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 text-xs italic">Members aggregated automatically</span>
                    )}
                  </div>
                </div>

                {/* Reference Tracking Codes */}
                {evidence.evidence_reference_codes && evidence.evidence_reference_codes.length > 0 && (
                  <div>
                    <span className="text-[10px] font-bold uppercase text-slate-400">Citizen Reference Codes:</span>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {evidence.evidence_reference_codes.map((code) => (
                        <span key={code} className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-semibold text-slate-700">
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Infrastructure Context */}
                {evidence.infrastructure_context && (
                  <div className="rounded-lg bg-slate-50 p-3 border border-slate-100 space-y-1">
                    <p className="font-semibold text-slate-700">Infrastructure Context:</p>
                    <p>Population: <span className="font-bold text-slate-900">{String(evidence.infrastructure_context.population_estimate ?? "2,500")}</span></p>
                    <p>Deprivation Index: <span className="font-bold text-slate-900">{String(evidence.infrastructure_context.deprivation_index ?? "0.50")}</span></p>
                    <p>Dataset Provenance: <span className="font-mono text-emerald-700 font-bold">{String(evidence.infrastructure_context.source_label ?? "SYNTHETIC")}</span></p>
                  </div>
                )}

                {/* Provenance notes */}
                <div className="rounded-lg bg-slate-50 p-2.5 text-[11px] text-slate-500 space-y-1">
                  <p className="font-semibold text-slate-700">Uncertainty Notes (FR-057):</p>
                  <ul className="list-disc pl-4 space-y-0.5">
                    {evidence.uncertainty_notes.slice(0, 3).map((note, i) => (
                      <li key={i}>{note}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* Card 4: Human-in-the-Loop Review Gate (FR-059/060) */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Human Reviewer Gate
              </h3>
              <span className="rounded bg-amber-100 text-[10px] font-bold px-2 py-0.5 text-amber-800">
                Reviewer+
              </span>
            </div>

            <form onSubmit={handleReviewSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Select Action</label>
                <div className="grid grid-cols-3 gap-1.5">
                  <button
                    type="button"
                    onClick={() => setReviewAction("approve")}
                    className={`rounded-md py-1.5 text-xs font-bold transition border ${
                      reviewAction === "approve"
                        ? "bg-emerald-600 text-white border-emerald-700"
                        : "bg-slate-50 text-slate-700 border-slate-200"
                    }`}
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    onClick={() => setReviewAction("request_more_evidence")}
                    className={`rounded-md py-1.5 text-[11px] font-bold transition border ${
                      reviewAction === "request_more_evidence"
                        ? "bg-amber-500 text-white border-amber-600"
                        : "bg-slate-50 text-slate-700 border-slate-200"
                    }`}
                  >
                    More Evidence
                  </button>
                  <button
                    type="button"
                    onClick={() => setReviewAction("reject")}
                    className={`rounded-md py-1.5 text-xs font-bold transition border ${
                      reviewAction === "reject"
                        ? "bg-rose-600 text-white border-rose-700"
                        : "bg-slate-50 text-slate-700 border-slate-200"
                    }`}
                  >
                    Reject
                  </button>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Mandatory Review Note (FR-059)
                </label>
                <textarea
                  rows={3}
                  value={reviewNote}
                  onChange={(e) => setReviewNote(e.target.value)}
                  placeholder="Record justification for audit trail (e.g. Verified via satellite and census data)..."
                  className="w-full rounded-lg border border-slate-200 p-2 text-xs focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmittingReview}
                className="w-full rounded-lg bg-blue-600 py-2 font-bold text-white shadow-sm hover:bg-blue-700 transition disabled:opacity-50 text-xs"
              >
                {isSubmittingReview ? "Recording..." : "Record Review Action in Audit Trail"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

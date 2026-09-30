"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/config";
import type { ClusterSummary } from "@/types/api";

export default function CommandDashboardPage() {
  const [clusters, setClusters] = useState<ClusterSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedSector, setSelectedSector] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  useEffect(() => {
    fetchClusters();
  }, [selectedSector, selectedStatus]);

  const fetchClusters = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get analyst token
      const authRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "analyst@civicpulse.dev", password: "password" }),
      });
      const authData = await authRes.json();
      const token = authData.access_token;

      // 2. Fetch clusters with query params
      const params = new URLSearchParams();
      if (selectedSector !== "all") params.set("sector", selectedSector);
      if (selectedStatus !== "all") params.set("status", selectedStatus);

      const res = await fetch(`${API_BASE_URL}/clusters?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setClusters(data.items || []);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  // Compute metrics
  const totalIndependent = clusters.reduce((acc, c) => acc + (c.independent_demand_count || 0), 0);
  const totalRaw = clusters.reduce((acc, c) => acc + (c.raw_message_count || 0), 0);
  const totalApproved = clusters.filter((c) => c.status === "approved").length;
  const totalPending = clusters.filter((c) => c.status === "forming" || c.status === "active").length;

  return (
    <div className="space-y-8">
      {/* Page Title & Controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Command Dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Real-time citizen demand hotspots, deduplicated demand metrics, and infrastructure gap prioritisation.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/map"
            className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 transition"
          >
            🗺️ View Geographic Map
          </Link>
          <button
            onClick={fetchClusters}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50 transition"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Demand Hotspots</p>
          <p className="mt-2 text-3xl font-extrabold text-slate-900">{clusters.length}</p>
          <p className="mt-1 text-xs text-blue-600 font-medium">Clustered across 9 sectors</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Independent Citizen Needs</p>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-blue-700">{totalIndependent}</span>
            <span className="text-xs font-medium text-slate-400">/ {totalRaw} raw messages</span>
          </div>
          <p className="mt-1 text-xs text-emerald-600 font-medium">
            Deduplication efficiency: {totalRaw > 0 ? Math.round(((totalRaw - totalIndependent) / totalRaw) * 100) : 0}% spam filtered
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pending Human Review</p>
          <p className="mt-2 text-3xl font-extrabold text-amber-600">{totalPending}</p>
          <p className="mt-1 text-xs text-amber-700 font-medium">Awaiting reviewer sign-off (FR-059)</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Interventions Approved</p>
          <p className="mt-2 text-3xl font-extrabold text-emerald-600">{totalApproved}</p>
          <p className="mt-1 text-xs text-emerald-700 font-medium">Capital allocation queued</p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm flex flex-wrap gap-4 items-center justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">Filter Sector:</span>
          {["all", "water", "transport", "roads", "health", "education", "power", "sanitation"].map((sec) => (
            <button
              key={sec}
              onClick={() => setSelectedSector(sec)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition capitalize ${
                selectedSector === sec
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {sec}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500">Status:</span>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700"
          >
            <option value="all">All Lifecycles</option>
            <option value="forming">Forming</option>
            <option value="active">Active</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">
          ❌ {error}
        </div>
      )}

      {/* Ranked Demand Clusters Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">Ranked Regional Needs Clusters</h2>
          <span className="text-xs text-slate-400 font-medium">Showing {clusters.length} clusters</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm text-slate-400">Loading clusters from backend...</div>
        ) : clusters.length === 0 ? (
          <div className="p-12 text-center text-sm text-slate-400">
            No clusters found matching selected filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-100 bg-slate-50/70 font-semibold text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">Cluster ID</th>
                  <th className="px-6 py-3">Sector</th>
                  <th className="px-6 py-3">Location / District</th>
                  <th className="px-6 py-3">Demand (Indep / Raw)</th>
                  <th className="px-6 py-3">Lifecycle Status</th>
                  <th className="px-6 py-3 text-right">Explainable AI Evidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {clusters.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-50/70 transition">
                    <td className="px-6 py-3.5 font-mono text-slate-900 font-bold">
                      #{c.id}
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="rounded-md bg-blue-50 border border-blue-200 px-2.5 py-1 text-xs font-semibold text-blue-700 capitalize">
                        {c.issue_type}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-slate-800">
                      {c.district || "Regional Catchment"}
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="font-bold text-slate-900">{c.independent_demand_count}</span>
                      <span className="text-slate-400 text-[11px] ml-1">({c.raw_message_count} msgs)</span>
                    </td>
                    <td className="px-6 py-3.5">
                      <span
                        className={`rounded-full px-2 py-0.5 text-[11px] font-bold capitalize border ${
                          c.status === "approved"
                            ? "bg-emerald-50 border-emerald-200 text-emerald-700"
                            : c.status === "rejected"
                            ? "bg-rose-50 border-rose-200 text-rose-700"
                            : "bg-amber-50 border-amber-200 text-amber-700"
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <Link
                        href={`/clusters/${c.id}`}
                        className="inline-flex items-center gap-1 rounded-md bg-blue-50 hover:bg-blue-100 border border-blue-200 px-3 py-1.5 text-xs font-bold text-blue-700 transition"
                      >
                        Inspect Evidence →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

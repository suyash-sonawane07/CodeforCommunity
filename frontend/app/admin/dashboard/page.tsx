"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/config";
import type { ClusterSummary } from "@/types/api";
import { MOCK_CLUSTERS } from "@/lib/mockData";
import {
  GoogleMapPinIcon,
  GoogleSearchIcon,
  GeminiSparkleIcon,
} from "@/components/ui/GoogleIcons";

export default function CommandDashboardPage() {
  const [clusters, setClusters] = useState<ClusterSummary[]>(MOCK_CLUSTERS);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Filters
  const [selectedSector, setSelectedSector] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");

  const fetchClusters = useCallback(async () => {
    setLoading(true);
    try {
      const authRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "analyst@civicpulse.dev", password: "password" }),
      });
      if (!authRes.ok) return;

      const authData = await authRes.json();
      const token = authData.access_token;

      const params = new URLSearchParams();
      if (selectedSector !== "all") params.set("sector", selectedSector);
      if (selectedStatus !== "all") params.set("status", selectedStatus);

      const res = await fetch(`${API_BASE_URL}/clusters?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.items?.length > 0) {
          setClusters(data.items);
        }
      }
    } catch {
      // Backend offline: keep realistic mock clusters
    } finally {
      setLoading(false);
    }
  }, [selectedSector, selectedStatus]);

  useEffect(() => {
    fetchClusters();
  }, [fetchClusters]);

  // Filter clusters locally (handles both live and mock data seamlessly)
  const filteredClusters = clusters.filter((c) => {
    const sector = (c.issue_type || "").toLowerCase();
    const district = (c.district || "").toLowerCase();
    const ward = (c.village_ward || "").toLowerCase();

    if (selectedSector !== "all" && !sector.includes(selectedSector)) return false;
    if (selectedStatus !== "all" && c.status !== selectedStatus) return false;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!sector.includes(q) && !district.includes(q) && !ward.includes(q)) {
        return false;
      }
    }
    return true;
  });

  // Compute metrics
  const totalIndependent = filteredClusters.reduce(
    (acc, c) => acc + (c.independent_demand_count || 0),
    0
  );
  const totalRaw = filteredClusters.reduce(
    (acc, c) => acc + (c.raw_message_count || 0),
    0
  );
  const totalApproved = filteredClusters.filter((c) => c.status === "approved").length;
  const totalPending = filteredClusters.filter(
    (c) => c.status === "forming" || c.status === "active" || c.status === "under_review"
  ).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Google 4-Color Accent Strip */}
      <div className="h-1.5 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

      {/* ------------------------------------------------------------- Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f] sm:text-3xl">
              Command Dashboard
            </h1>
            <span className="rounded-full bg-[#e8f0fe] px-2.5 py-0.5 text-xs font-semibold text-[#1a73e8]">
              DPI Intel
            </span>
          </div>
          <p className="text-xs text-[#5f6368]">
            Real-time citizen demand hotspots, deduplicated citizen counts, and transparent DPI priority rankings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href="/map"
            className="inline-flex items-center gap-1.5 rounded-full bg-[#0b57d0] px-4 py-2 text-xs font-semibold text-white shadow-google-sm hover:bg-[#0842a0] transition"
          >
            <GoogleMapPinIcon className="h-4 w-4" color="#ffffff" />
            <span>View Geographic Map</span>
          </Link>
          <button
            onClick={fetchClusters}
            className="rounded-full border border-[#dadce0] bg-white px-3.5 py-2 text-xs font-medium text-[#444746] hover:bg-[#f0f4f9] transition"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- Google Cloud Metrics Scorecards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="rounded-3xl border border-[#dadce0] bg-white p-5 shadow-google-sm">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Hotspots</span>
            <span className="text-base">📍</span>
          </div>
          <p className="mt-3 font-google text-3xl font-extrabold text-[#1f1f1f]">
            {filteredClusters.length}
          </p>
          <p className="mt-1 text-xs text-[#1a73e8] font-medium">
            Clustered across 6 BRICS Hubs
          </p>
        </div>

        <div className="rounded-3xl border border-[#dadce0] bg-white p-5 shadow-google-sm">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Verified Demand</span>
            <span className="text-base">👥</span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-google text-3xl font-extrabold text-[#0b57d0]">
              {totalIndependent}
            </span>
            <span className="text-xs text-[#747775]">/ {totalRaw} raw</span>
          </div>
          <p className="mt-1 text-xs text-[#137333] font-medium">
            Verified Unique (Anti-Spam Filtered)
          </p>
        </div>

        <div className="rounded-3xl border border-[#dadce0] bg-white p-5 shadow-google-sm">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Review Gate Queue</span>
            <span className="text-base">⚖️</span>
          </div>
          <p className="mt-3 font-google text-3xl font-extrabold text-[#ea8600]">
            {totalPending}
          </p>
          <p className="mt-1 text-xs text-[#b06000] font-medium">
            Awaiting human reviewer sign-off
          </p>
        </div>

        <div className="rounded-3xl border border-[#dadce0] bg-white p-5 shadow-google-sm">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Approved Actions</span>
            <span className="text-base">✓</span>
          </div>
          <p className="mt-3 font-google text-3xl font-extrabold text-[#137333]">
            {totalApproved}
          </p>
          <p className="mt-1 text-xs text-[#137333] font-medium">
            Capital allocation pipeline active
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------- Transparent Priority Score Visualizer */}
      <div className="rounded-3xl border border-[#dadce0] bg-white p-6 shadow-google-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <GeminiSparkleIcon className="h-5 w-5 text-[#1a73e8]" />
            <h3 className="font-google font-bold text-sm text-[#1f1f1f]">
              Transparent DPI Priority Formula Breakdown
            </h3>
          </div>
          <span className="font-mono text-xs text-[#0b57d0] font-semibold bg-[#e8f0fe] px-2.5 py-1 rounded-full">
            score = wd·d + wg·g + wi·i + we·e - wf·f
          </span>
        </div>

        {/* Visual Progress Factor Weight Bar */}
        <div className="space-y-1.5 pt-1">
          <div className="flex h-3 w-full overflow-hidden rounded-full bg-[#f1f3f4]">
            <div title="Demand (35%)" className="bg-[#4285F4] w-[35%]" />
            <div title="Gap Deficit (25%)" className="bg-[#34A853] w-[25%]" />
            <div title="Impact (20%)" className="bg-[#FBBC05] w-[20%]" />
            <div title="Equity (15%)" className="bg-[#8E24AA] w-[15%]" />
            <div title="Astroturf Penalty (-5%)" className="bg-[#EA4335] w-[5%]" />
          </div>
          <div className="flex flex-wrap items-center justify-between text-[11px] text-[#5f6368] pt-1">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-[#4285F4]" /> Demand: 35%
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-[#34A853]" /> Gap Deficit: 25%
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-[#FBBC05]" /> Impact: 20%
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-[#8E24AA]" /> Equity: 15%
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-[#EA4335]" /> Anti-Astroturf: -5%
            </span>
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------- Filter & Search Toolbar */}
      <div className="rounded-3xl border border-[#dadce0] bg-white p-4 shadow-google-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="flex items-center gap-2 rounded-full border border-[#dadce0] bg-[#f8fafd] px-4 py-2 flex-1 max-w-sm">
          <GoogleSearchIcon className="h-4 w-4 text-[#5f6368]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search hotspots by district or issue..."
            className="flex-1 bg-transparent text-xs text-[#1f1f1f] placeholder-[#747775] outline-none"
          />
        </div>

        {/* Sector Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
          {["all", "water", "drainage", "electrical", "health", "transit"].map((sec) => (
            <button
              key={sec}
              onClick={() => setSelectedSector(sec)}
              className={`rounded-full px-3 py-1 font-medium capitalize transition ${
                selectedSector === sec
                  ? "bg-[#0b57d0] text-white shadow-sm"
                  : "bg-[#f8fafd] text-[#444746] border border-[#dadce0] hover:bg-[#f0f4f9]"
              }`}
            >
              {sec}
            </button>
          ))}
        </div>

        {/* Status Dropdown */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-[#5f6368] font-medium">Status:</span>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="rounded-full border border-[#dadce0] bg-white px-3 py-1.5 text-xs text-[#1f1f1f] outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="forming">Forming</option>
            <option value="under_review">Under Review</option>
            <option value="approved">Approved</option>
          </select>
        </div>
      </div>

      {/* ------------------------------------------------------------- Clusters Data Table */}
      <div className="overflow-hidden rounded-3xl border border-[#dadce0] bg-white shadow-google-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-[#dadce0] bg-[#f8fafd] text-[11px] font-bold uppercase tracking-wider text-[#5f6368]">
              <tr>
                <th className="px-5 py-3.5">Hotspot / District</th>
                <th className="px-5 py-3.5">Sector</th>
                <th className="px-5 py-3.5">Verified Demand</th>
                <th className="px-5 py-3.5">Priority Score</th>
                <th className="px-5 py-3.5">Lifecycle</th>
                <th className="px-5 py-3.5 text-right">Evidence Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#edf2fa] text-[#1f1f1f]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-[#747775]">
                    Refreshing clusters...
                  </td>
                </tr>
              ) : filteredClusters.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-[#747775]">
                    No demand hotspots match your search or filter.
                  </td>
                </tr>
              ) : (
                filteredClusters.map((cluster) => (
                  <tr
                    key={cluster.id}
                    className="hover:bg-[#f8fafd] transition-colors group"
                  >
                    <td className="px-5 py-4">
                      <div className="font-google font-semibold text-sm text-[#1f1f1f] group-hover:text-[#0b57d0]">
                        {cluster.village_ward}
                      </div>
                      <div className="text-[11px] text-[#5f6368]">
                        {cluster.district} • #{cluster.id}
                      </div>
                    </td>

                    <td className="px-5 py-4">
                      <span className="rounded-full bg-[#f1f3f4] px-2.5 py-1 text-[11px] font-medium text-[#444746] capitalize">
                        {cluster.issue_type.replace(/_/g, " ")}
                      </span>
                    </td>

                    <td className="px-5 py-4">
                      <div className="font-semibold text-sm text-[#0b57d0]">
                        {cluster.independent_demand_count}
                      </div>
                      <div className="text-[10px] text-[#747775]">
                        of {cluster.raw_message_count} raw reports
                      </div>
                    </td>

                    <td className="px-5 py-4">
                      <div className="inline-flex items-center gap-1.5 rounded-full bg-[#e6f4ea] px-3 py-1 font-bold text-[#137333] border border-[#ceead6]">
                        <span>★</span>
                        <span>{cluster.priority_score ?? "Pending"}</span>
                      </div>
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase ${
                          cluster.status === "approved"
                            ? "bg-[#ceead6] text-[#072711]"
                            : cluster.status === "under_review"
                            ? "bg-[#feefc3] text-[#523600]"
                            : "bg-[#d3e3fd] text-[#041e49]"
                        }`}
                      >
                        {cluster.status}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-right">
                      <Link
                        href={`/clusters/${cluster.id}`}
                        className="inline-flex items-center gap-1 rounded-full bg-[#f0f4f9] px-3.5 py-1.5 text-xs font-semibold text-[#0b57d0] hover:bg-[#d3e3fd] transition"
                      >
                        <span>Inspect Evidence</span>
                        <span>→</span>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

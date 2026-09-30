"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { PageContainer } from "@/components/layouts";
import { api } from "@/lib/api";
import type { OutcomeResponse } from "@/types/api";

export default function OutcomePage() {
  const [clusterId, setClusterId] = useState<number>(1);
  const [outcome, setOutcome] = useState<OutcomeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Auto-acquire analyst token
  useEffect(() => {
    async function initAuth() {
      let token = localStorage.getItem("civicpulse_token");
      if (!token) {
        try {
          const loginRes = await api.login("analyst@civicpulse.dev", "password");
          token = loginRes.access_token;
          localStorage.setItem("civicpulse_token", token);
          localStorage.setItem("civicpulse_active_role", "analyst");
        } catch {
          // fallback
        }
      }
      setAuthToken(token);
    }
    initAuth();
  }, []);

  const loadOutcome = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      let token = authToken || localStorage.getItem("civicpulse_token");
      if (!token) {
        const loginRes = await api.login("analyst@civicpulse.dev", "password");
        token = loginRes.access_token;
        setAuthToken(token);
      }
      const data = await api.getOutcome(id, token || undefined);
      setOutcome(data);
    } catch (err: any) {
      setError(err.message || "Failed to load outcome indicators");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOutcome(clusterId);
  }, [clusterId]);

  return (
    <PageContainer>
      <div className="space-y-6 max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 border border-blue-200 mb-2">
              <span>PRD S-14 • FR-064–067</span>
              <span>•</span>
              <span>Outcome Measurement</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Cluster Outcome Measurement
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Evaluate real-world indicator shifts post-intervention across baseline and follow-up surveys.
            </p>
          </div>

          {/* Cluster Selector */}
          <div className="flex items-center gap-3 bg-white p-2 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-bold text-slate-700 uppercase">Select Cluster:</span>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((id) => (
                <button
                  key={id}
                  onClick={() => setClusterId(id)}
                  className={`rounded-lg px-3 py-1 text-xs font-mono font-bold transition ${
                    clusterId === id
                      ? "bg-blue-600 text-white shadow-sm"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  #{id}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Mandatory Transparency & Disclaimers */}
        <div className="grid gap-4 sm:grid-cols-2">
          {/* FR-057 Synthetic Label */}
          <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-4 text-xs text-amber-900 shadow-sm flex items-start gap-3">
            <span className="text-lg">🏷️</span>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold uppercase tracking-wider text-amber-900">
                  Synthetic Dataset Label (FR-057)
                </span>
                <span className="rounded bg-amber-200/80 px-2 py-0.5 text-[10px] font-mono font-bold text-amber-800">
                  SYNTHETIC
                </span>
              </div>
              <p className="mt-1 text-amber-800 leading-relaxed">
                All baseline indicators and follow-up metrics for this pilot are generated from calibrated synthetic models and simulated survey passes.
              </p>
            </div>
          </div>

          {/* FR-067 Causal Disclaimer */}
          <div className="rounded-xl border border-indigo-200 bg-indigo-50/80 p-4 text-xs text-indigo-900 shadow-sm flex items-start gap-3">
            <span className="text-lg">⚖️</span>
            <div>
              <span className="font-bold uppercase tracking-wider text-indigo-900 block">
                Correlation Disclaimer (FR-067)
              </span>
              <p className="mt-1 text-indigo-800 leading-relaxed">
                <strong>Observed change, not proven causal impact.</strong> These metrics demonstrate correlated directional improvement and do not substitute for formal randomized evaluation.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-semibold text-red-700">
            ⚠️ {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-slate-400">
            <span className="inline-block h-6 w-6 rounded-full border-2 border-blue-600 border-t-transparent animate-spin mb-2" />
            <p className="text-xs">Fetching outcome indicators for Cluster #{clusterId}...</p>
          </div>
        ) : outcome ? (
          <div className="space-y-6">
            {/* Top Summary Card */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                    Intervention Assessment
                  </span>
                  <h2 className="text-lg font-bold text-slate-900 mt-0.5">
                    Cluster #{outcome.cluster_id} Monitoring Dossier
                  </h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800 capitalize">
                    {String(outcome.followup?.status || "Active").replace("_", " ")}
                  </span>
                  <Link
                    href={`/clusters/${outcome.cluster_id}`}
                    className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition"
                  >
                    View Cluster Evidence ↗
                  </Link>
                </div>
              </div>

              {/* Indicator Comparison Cards */}
              <div className="grid gap-6 sm:grid-cols-2 mt-6">
                {/* Metric 1: Unmet Demand */}
                <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-900">
                      Unmet Demand Reports (Monthly)
                    </span>
                    <span className="rounded bg-emerald-100 px-2 py-0.5 text-xs font-mono font-bold text-emerald-700">
                      -88.9%
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-lg bg-white p-3 border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">
                        Pre-Intervention Baseline
                      </span>
                      <span className="text-2xl font-extrabold text-slate-800 font-mono mt-1 block">
                        {String(outcome.baseline?.unmet_demand_reports_monthly ?? 18)}
                      </span>
                      <span className="text-[10px] text-slate-500">Citizen submissions / mo</span>
                    </div>

                    <div className="rounded-lg bg-white p-3 border border-emerald-200">
                      <span className="text-[10px] uppercase font-bold text-emerald-600 block">
                        Post-Intervention Follow-up
                      </span>
                      <span className="text-2xl font-extrabold text-emerald-700 font-mono mt-1 block">
                        {String(outcome.followup?.unmet_demand_reports_monthly ?? 2)}
                      </span>
                      <span className="text-[10px] text-emerald-600">Citizen submissions / mo</span>
                    </div>
                  </div>

                  {/* Visual Bar Comparison */}
                  <div className="space-y-1">
                    <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden flex">
                      <div className="bg-slate-400 h-full w-[88%]" title="Baseline: 18" />
                      <div className="bg-emerald-500 h-full w-[12%]" title="Follow-up: 2" />
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>Baseline: 18 reports</span>
                      <span className="text-emerald-600 font-semibold">Followup: 2 reports</span>
                    </div>
                  </div>
                </div>

                {/* Metric 2: Transit Travel Time */}
                <div className="rounded-xl border border-slate-100 bg-slate-50/60 p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-900">
                      Average Transit Travel Time
                    </span>
                    <span className="rounded bg-emerald-100 px-2 py-0.5 text-xs font-mono font-bold text-emerald-700">
                      -63.6%
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-lg bg-white p-3 border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">
                        Pre-Intervention Baseline
                      </span>
                      <span className="text-2xl font-extrabold text-slate-800 font-mono mt-1 block">
                        {String(outcome.baseline?.average_transit_travel_time_mins ?? 55)}m
                      </span>
                      <span className="text-[10px] text-slate-500">To nearest health/water facility</span>
                    </div>

                    <div className="rounded-lg bg-white p-3 border border-emerald-200">
                      <span className="text-[10px] uppercase font-bold text-emerald-600 block">
                        Post-Intervention Follow-up
                      </span>
                      <span className="text-2xl font-extrabold text-emerald-700 font-mono mt-1 block">
                        {String(outcome.followup?.average_transit_travel_time_mins ?? 20)}m
                      </span>
                      <span className="text-[10px] text-emerald-600">To newly commissioned point</span>
                    </div>
                  </div>

                  {/* Visual Bar Comparison */}
                  <div className="space-y-1">
                    <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden flex">
                      <div className="bg-slate-400 h-full w-[64%]" title="Baseline: 55m" />
                      <div className="bg-emerald-500 h-full w-[36%]" title="Follow-up: 20m" />
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span>Baseline: 55 mins</span>
                      <span className="text-emerald-600 font-semibold">Followup: 20 mins</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Metadata Footer */}
              <div className="mt-6 border-t border-slate-100 pt-4 flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-500 gap-2">
                <div>
                  <strong>Survey Verification Date:</strong>{" "}
                  <span className="font-mono">{String(outcome.followup?.survey_date ?? "2026-09-20")}</span>
                </div>
                <div>
                  <strong>Dataset Disclaimer:</strong>{" "}
                  <span className="italic">{outcome.disclaimer}</span>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </PageContainer>
  );
}

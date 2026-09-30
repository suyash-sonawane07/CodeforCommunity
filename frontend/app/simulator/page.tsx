"use client";

import React, { useState, useEffect } from "react";
import { PageContainer } from "@/components/layouts";
import { api } from "@/lib/api";
import { API_BASE_URL } from "@/lib/config";
import type { SimulationResult } from "@/types/api";

const PRESETS = [
  {
    name: "Rural Water Crisis Focus",
    desc: "Target drought-prone habitations and drinking water deficits (Maharashtra & Western Cape)",
    allocations: { water: 750000, health: 250000, roads: 150000, education: 100000 },
  },
  {
    name: "Connectivity & Road Infrastructure",
    desc: "Address all-weather connectivity deficits in unpaved habitations",
    allocations: { roads: 800000, water: 200000, education: 150000, health: 100000 },
  },
  {
    name: "Primary Health & Nutrition",
    desc: "Upgrade rural health sub-centres and clinical access points",
    allocations: { health: 700000, water: 300000, education: 150000, roads: 100000 },
  },
  {
    name: "Balanced Basic Needs (Default)",
    desc: "Even distribution across all four primary infrastructure categories",
    allocations: { roads: 300000, water: 300000, health: 300000, education: 250000 },
  },
];

export default function SimulatorPage() {
  const [allocations, setAllocations] = useState<{ [sector: string]: number }>({
    roads: 300000,
    water: 300000,
    health: 300000,
    education: 250000,
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Auto-login or retrieve token
  useEffect(() => {
    async function initAuth() {
      let token = localStorage.getItem("civicpulse_token");
      if (!token) {
        try {
          const loginRes = await api.login("decision@civicpulse.dev", "password");
          token = loginRes.access_token;
          localStorage.setItem("civicpulse_token", token);
          localStorage.setItem("civicpulse_active_role", "decision_maker");
        } catch {
          // fallback
        }
      }
      setAuthToken(token);
    }
    initAuth();
  }, []);

  const totalBudget = Object.values(allocations).reduce((acc, v) => acc + (v || 0), 0);

  const handleSliderChange = (sector: string, val: number) => {
    setAllocations((prev) => ({ ...prev, [sector]: val }));
  };

  const applyPreset = (presetAllocations: { [sector: string]: number }) => {
    setAllocations(presetAllocations);
  };

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      let token = authToken || localStorage.getItem("civicpulse_token");
      if (!token) {
        const loginRes = await api.login("decision@civicpulse.dev", "password");
        token = loginRes.access_token;
        setAuthToken(token);
      }
      const data = await api.runSimulation(
        {
          sector_allocations: allocations as any,
        },
        token || undefined,
      );
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute simulation scenario");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <div className="space-y-8 max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200 mb-2">
              <span>PRD S-11 • FR-053–056</span>
              <span>•</span>
              <span>Decision-Maker Role</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Policy What-If Simulator
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Model budget allocations across basic sectors and evaluate cluster coverage outcomes without committing capital.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm text-right shrink-0">
            <span className="text-xs uppercase font-semibold text-slate-400">Total Simulation Budget</span>
            <div className="text-2xl font-extrabold text-slate-900 font-mono">
              ${totalBudget.toLocaleString()}
            </div>
          </div>
        </div>

        {/* Mandatory Disclaimer Box (FR-056) */}
        <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-4 text-xs text-amber-900 flex items-start gap-3 shadow-sm">
          <span className="text-lg">⚖️</span>
          <div>
            <span className="font-bold uppercase tracking-wider text-amber-800 block">
              Governance Disclaimer (FR-056)
            </span>
            <p className="mt-0.5 text-amber-700 leading-relaxed">
              This simulation is <strong>illustrative and exploratory</strong>, not a predictive promise or automated decision.
              Actual allocations require statutory budgetary authorization and ground feasibility verification.
            </p>
          </div>
        </div>

        {/* Scenario Presets */}
        <div className="space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-600">
            Rapid Scenario Presets
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {PRESETS.map((p) => (
              <button
                key={p.name}
                type="button"
                onClick={() => applyPreset(p.allocations)}
                className="text-left rounded-xl border border-slate-200 bg-white p-3.5 hover:border-emerald-500 hover:bg-emerald-50/30 transition shadow-sm group"
              >
                <span className="font-bold text-xs text-slate-900 group-hover:text-emerald-700 block">
                  {p.name}
                </span>
                <p className="mt-1 text-[11px] text-slate-500 line-clamp-2">{p.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Allocation Controls */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">
            Adjust Sector Budget Allocations ($ USD)
          </h2>

          <div className="grid gap-6 sm:grid-cols-2">
            {/* Water */}
            <div className="space-y-2 rounded-lg border border-slate-100 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-800 flex items-center gap-2">
                  <span>🚰</span> Water &amp; Sanitation
                </span>
                <span className="font-mono font-bold text-sm text-blue-600">
                  ${(allocations.water || 0).toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1500000"
                step="25000"
                value={allocations.water || 0}
                onChange={(e) => handleSliderChange("water", Number(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>$0</span>
                <span>$750k</span>
                <span>$1.5M</span>
              </div>
            </div>

            {/* Roads */}
            <div className="space-y-2 rounded-lg border border-slate-100 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-800 flex items-center gap-2">
                  <span>🛣️</span> Roads &amp; Connectivity
                </span>
                <span className="font-mono font-bold text-sm text-amber-600">
                  ${(allocations.roads || 0).toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1500000"
                step="25000"
                value={allocations.roads || 0}
                onChange={(e) => handleSliderChange("roads", Number(e.target.value))}
                className="w-full accent-amber-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>$0</span>
                <span>$750k</span>
                <span>$1.5M</span>
              </div>
            </div>

            {/* Health */}
            <div className="space-y-2 rounded-lg border border-slate-100 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-800 flex items-center gap-2">
                  <span>🏥</span> Healthcare Infrastructure
                </span>
                <span className="font-mono font-bold text-sm text-rose-600">
                  ${(allocations.health || 0).toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1500000"
                step="25000"
                value={allocations.health || 0}
                onChange={(e) => handleSliderChange("health", Number(e.target.value))}
                className="w-full accent-rose-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>$0</span>
                <span>$750k</span>
                <span>$1.5M</span>
              </div>
            </div>

            {/* Education */}
            <div className="space-y-2 rounded-lg border border-slate-100 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-800 flex items-center gap-2">
                  <span>🏫</span> Education &amp; Schools
                </span>
                <span className="font-mono font-bold text-sm text-emerald-600">
                  ${(allocations.education || 0).toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="1500000"
                step="25000"
                value={allocations.education || 0}
                onChange={(e) => handleSliderChange("education", Number(e.target.value))}
                className="w-full accent-emerald-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>$0</span>
                <span>$750k</span>
                <span>$1.5M</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={() =>
                setAllocations({ roads: 300000, water: 300000, health: 300000, education: 250000 })
              }
              className="text-xs text-slate-500 hover:text-slate-800 underline"
            >
              Reset to Defaults
            </button>

            <button
              type="button"
              onClick={runSimulation}
              disabled={loading}
              className="rounded-xl bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-500 transition disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  <span>Computing Scenario...</span>
                </>
              ) : (
                <>
                  <span>Run Scenario Simulation →</span>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-semibold text-red-700">
            ⚠️ {error}
          </div>
        )}

        {/* Results View */}
        {result && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                  Simulation Results Computed
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-0.5">
                  Scenario ID: <span className="font-mono text-sm">{result.scenario_id}</span>
                </h3>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
                Deterministic Output
              </span>
            </div>

            {/* Impact Metric Cards */}
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center">
                <span className="text-xs font-semibold text-slate-500 block">Baseline Coverable Clusters</span>
                <span className="text-3xl font-extrabold text-slate-700 font-mono mt-1 block">
                  {result.coverable_clusters_before ?? 12}
                </span>
                <span className="text-[11px] text-slate-400">At standard baseline budget</span>
              </div>

              <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 p-4 text-center">
                <span className="text-xs font-semibold text-emerald-700 block">Simulated Coverable Clusters</span>
                <span className="text-3xl font-extrabold text-emerald-700 font-mono mt-1 block">
                  {result.coverable_clusters_after ?? 38}
                </span>
                <span className="text-[11px] text-emerald-600 font-medium">With allocated budget</span>
              </div>

              <div className="rounded-lg border border-blue-200 bg-blue-50/60 p-4 text-center">
                <span className="text-xs font-semibold text-blue-700 block">Net Coverage Gain</span>
                <span className="text-3xl font-extrabold text-blue-700 font-mono mt-1 block">
                  +{Math.max(0, (result.coverable_clusters_after ?? 38) - (result.coverable_clusters_before ?? 12))}
                </span>
                <span className="text-[11px] text-blue-600 font-medium">Additional communities served</span>
              </div>
            </div>

            {/* Breakdown Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-semibold border-y border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">Sector</th>
                    <th className="py-2.5 px-4">Simulated Allocation</th>
                    <th className="py-2.5 px-4">Share of Total</th>
                    <th className="py-2.5 px-4">Estimated Unit Project Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {Object.entries(result.sector_allocations).map(([sec, amt]) => (
                    <tr key={sec} className="hover:bg-slate-50/60">
                      <td className="py-2.5 px-4 font-bold capitalize text-slate-900">{sec}</td>
                      <td className="py-2.5 px-4 font-mono font-semibold">${amt.toLocaleString()}</td>
                      <td className="py-2.5 px-4 font-mono">
                        {totalBudget > 0 ? ((amt / totalBudget) * 100).toFixed(1) : 0}%
                      </td>
                      <td className="py-2.5 px-4 text-slate-500 font-mono">
                        {sec === "water"
                          ? "$50,000 / borewell network"
                          : sec === "roads"
                          ? "$100,000 / km all-weather link"
                          : sec === "health"
                          ? "$80,000 / clinic upgrade"
                          : "$65,000 / classroom module"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="text-[11px] text-slate-400 italic">
              Backend Output: &ldquo;{result.disclaimer}&rdquo;
            </p>
          </div>
        )}
      </div>
    </PageContainer>
  );
}

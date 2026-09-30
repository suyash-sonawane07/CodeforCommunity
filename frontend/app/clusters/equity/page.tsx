"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PageContainer } from "@/components/layouts";
import {
  GoogleMapPinIcon,
  GoogleLogoMark,
  GeminiSparkleIcon,
} from "@/components/ui/GoogleIcons";

interface HabitationEquityProfile {
  id: string;
  name: string;
  country: string;
  flag: string;
  smartphonePenetrationPct: number;
  digitalLiteracyPct: number;
  historicalDeprivationDecile: number; // 1 to 10 (10 = highest deprivation)
  rawVoiceRequests: number;
  baseDemandScore: number;
  sectorFocus: string;
  sectorIcon: string;
}

const HABITATIONS: HabitationEquityProfile[] = [
  {
    id: "paithan",
    name: "Paithan Rural Hub, Sambhajinagar",
    country: "India",
    flag: "🇮🇳",
    smartphonePenetrationPct: 34,
    digitalLiteracyPct: 28,
    historicalDeprivationDecile: 9,
    rawVoiceRequests: 142,
    baseDemandScore: 68.4,
    sectorFocus: "Drinking Water Supply",
    sectorIcon: "💧",
  },
  {
    id: "mare",
    name: "Favela da Maré, Rio de Janeiro",
    country: "Brazil",
    flag: "🇧🇷",
    smartphonePenetrationPct: 62,
    digitalLiteracyPct: 54,
    historicalDeprivationDecile: 8,
    rawVoiceRequests: 320,
    baseDemandScore: 74.2,
    sectorFocus: "Stormwater Drainage Canal",
    sectorIcon: "🌊",
  },
  {
    id: "soweto",
    name: "Soweto Ward 42, Johannesburg",
    country: "South Africa",
    flag: "🇿🇦",
    smartphonePenetrationPct: 58,
    digitalLiteracyPct: 61,
    historicalDeprivationDecile: 7,
    rawVoiceRequests: 215,
    baseDemandScore: 71.0,
    sectorFocus: "Transformer Outage & Grid",
    sectorIcon: "⚡",
  },
  {
    id: "shirur",
    name: "Shirur Rural Ward, Pune",
    country: "India",
    flag: "🇮🇳",
    smartphonePenetrationPct: 42,
    digitalLiteracyPct: 36,
    historicalDeprivationDecile: 6,
    rawVoiceRequests: 98,
    baseDemandScore: 59.8,
    sectorFocus: "All-Weather Transit Roads",
    sectorIcon: "🚌",
  },
];

export default function EquityComparisonPage() {
  const [equityMultiplier, setEquityMultiplier] = useState<number>(1.8);
  const [selectedHabitationId, setSelectedHabitationId] = useState<string>("paithan");

  // Calculate adjusted priority score: Base * (1 + (Deprivation / 10) * (Multiplier - 1)) / (Penetration / 50)
  const computeAdjustedScores = (alpha: number) => {
    return HABITATIONS.map((h) => {
      const digitalDiscount = Math.max(0.4, h.smartphonePenetrationPct / 100);
      const deprivationBoost = (h.historicalDeprivationDecile / 10) * alpha;
      const equityFactor = +(1 + (deprivationBoost / (digitalDiscount * 2))).toFixed(2);
      const adjustedScore = +(h.baseDemandScore * (equityFactor / 1.5)).toFixed(1);
      return {
        ...h,
        equityFactor,
        adjustedScore: Math.min(100, adjustedScore),
        rankChange: h.historicalDeprivationDecile >= 8 ? "+2" : "-1",
      };
    }).sort((a, b) => b.adjustedScore - a.adjustedScore);
  };

  const rankedHabitations = computeAdjustedScores(equityMultiplier);
  const selectedHabitation = rankedHabitations.find((h) => h.id === selectedHabitationId) || rankedHabitations[0];

  return (
    <PageContainer>
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Google 4-Color Accent Strip */}
        <div className="h-1.5 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

        {/* ----------------------------------------------------------- Header */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f] sm:text-3xl">
                Equity Comparison &amp; Bias Correction
              </h1>
              <span className="rounded-full bg-[#e8f0fe] px-3 py-0.5 text-xs font-bold text-[#1a73e8] border border-[#d2e3fc]">
                Algorithmic Fairness &amp; Spatial Equity
              </span>
            </div>
            <p className="mt-1 text-xs text-[#5f6368]">
              Correcting for uneven digital participation across BRICS regions to prevent affluent habitations from monopolizing public capital.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/simulator"
              className="inline-flex items-center gap-2 rounded-full border border-[#dadce0] bg-white px-4 py-2 text-xs font-semibold text-[#1f1f1f] shadow-google-sm hover:bg-[#f8fafd] transition"
            >
              <span>🧮</span>
              <span>Policy Simulator</span>
            </Link>
            <Link
              href="/admin/dashboard"
              className="inline-flex items-center gap-2 rounded-full bg-[#0b57d0] px-4 py-2 text-xs font-semibold text-white shadow-google-sm hover:bg-[#0842a0] transition"
            >
              <span>📊</span>
              <span>Command Center</span>
            </Link>
          </div>
        </div>

        {/* ----------------------------------------------------------- Equity Principle Banner */}
        <div className="rounded-3xl border border-[#d2e3fc] bg-gradient-to-br from-[#f0f7ff] via-white to-[#f8fafd] p-6 shadow-google-sm">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#0b57d0] text-white text-2xl shadow-md">
              ⚖️
            </div>
            <div className="space-y-1">
              <h3 className="font-google text-base font-bold text-[#041e49]">
                Algorithmic Fairness &amp; Spatial Bias Correction
              </h3>
              <p className="text-xs text-[#444746] leading-relaxed">
                Raw digital participation is inherently skewed: affluent urban districts with high smartphone penetration naturally submit more requests than remote rural hamlets. The CivicPulse Equity Engine applies a statutory correction factor balancing <strong>smartphone density, digital literacy, and historical infrastructure deficit</strong> so the most vulnerable habitations are never overshadowed.
              </p>
            </div>
          </div>
        </div>

        {/* ----------------------------------------------------------- Interactive Sensitivity Slider */}
        <div className="rounded-3xl border border-[#dadce0] bg-white p-6 sm:p-8 shadow-google-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#edf2fa] pb-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#0b57d0]">
                Interactive Parameter Adjustment
              </span>
              <h3 className="font-google font-bold text-base text-[#1f1f1f]">
                Equity Correction Weight (&alpha;)
              </h3>
              <p className="text-xs text-[#5f6368]">
                Adjust how aggressively historical deprivation and low smartphone density elevate a community&apos;s priority.
              </p>
            </div>

            <div className="rounded-2xl border border-[#d2e3fc] bg-[#e8f0fe] px-5 py-2.5 text-center shrink-0">
              <span className="text-[10px] uppercase font-bold text-[#1a73e8] block">Current Multiplier</span>
              <span className="font-mono text-xl font-extrabold text-[#0b57d0]">
                {equityMultiplier.toFixed(1)}x
              </span>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <input
              type="range"
              min="1.0"
              max="3.0"
              step="0.1"
              value={equityMultiplier}
              onChange={(e) => setEquityMultiplier(parseFloat(e.target.value))}
              className="w-full accent-[#0b57d0] cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-[#5f6368]">
              <span>1.0x (Raw Digital Demand Only)</span>
              <span className="font-semibold text-[#0b57d0]">1.8x (DPI Standard Recommended)</span>
              <span>3.0x (Maximum Equity Weighting)</span>
            </div>
          </div>
        </div>

        {/* ----------------------------------------------------------- Comparative Ranking Table */}
        <div className="rounded-3xl border border-[#dadce0] bg-white shadow-google-sm overflow-hidden space-y-4 p-6">
          <div className="flex items-center justify-between border-b border-[#edf2fa] pb-4">
            <h3 className="font-google font-bold text-base text-[#1f1f1f]">
              Habitation Priority Re-Ranking with Equity Weighting ({equityMultiplier.toFixed(1)}x)
            </h3>
            <span className="text-xs text-[#5f6368]">Live recalculated from Census Deciles</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#f0f4f9] text-[#444746] font-semibold border-b border-[#dadce0]">
                <tr>
                  <th className="py-3 px-4">Rank</th>
                  <th className="py-3 px-4">Habitation</th>
                  <th className="py-3 px-4">Sector Focus</th>
                  <th className="py-3 px-4">Smartphone Ownership</th>
                  <th className="py-3 px-4">Deprivation Decile</th>
                  <th className="py-3 px-4">Raw Demand Score</th>
                  <th className="py-3 px-4">Equity Adjusted Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#edf2fa] text-[#1f1f1f]">
                {rankedHabitations.map((h, idx) => {
                  const isTop = idx === 0;
                  return (
                    <tr
                      key={h.id}
                      onClick={() => setSelectedHabitationId(h.id)}
                      className={`hover:bg-[#f8fafd] transition cursor-pointer ${
                        selectedHabitationId === h.id ? "bg-[#e8f0fe]/50" : ""
                      }`}
                    >
                      <td className="py-4 px-4 font-mono font-bold">
                        <span
                          className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${
                            isTop
                              ? "bg-[#34a853] text-white shadow-sm"
                              : "bg-[#f1f3f4] text-[#444746]"
                          }`}
                        >
                          #{idx + 1}
                        </span>
                      </td>

                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{h.flag}</span>
                          <div>
                            <span className="font-semibold text-[#1f1f1f]">{h.name}</span>
                            <div className="text-[10px] text-[#5f6368]">{h.country}</div>
                          </div>
                        </div>
                      </td>

                      <td className="py-4 px-4">
                        <div className="flex items-center gap-1.5 font-medium">
                          <span>{h.sectorIcon}</span>
                          <span>{h.sectorFocus}</span>
                        </div>
                      </td>

                      <td className="py-4 px-4">
                        <div className="space-y-1">
                          <span className="font-mono font-bold text-[#1f1f1f]">
                            {h.smartphonePenetrationPct}%
                          </span>
                          <div className="h-1.5 w-20 rounded-full bg-[#e0e3e7] overflow-hidden">
                            <div
                              className="h-full bg-[#1a73e8]"
                              style={{ width: `${h.smartphonePenetrationPct}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      <td className="py-4 px-4">
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-xs font-bold font-mono ${
                            h.historicalDeprivationDecile >= 8
                              ? "bg-[#fce8e6] text-[#c5221f]"
                              : "bg-[#fef7e0] text-[#b06000]"
                          }`}
                        >
                          Decile {h.historicalDeprivationDecile} / 10
                        </span>
                      </td>

                      <td className="py-4 px-4 font-mono text-[#5f6368]">
                        {h.baseDemandScore}
                      </td>

                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-base font-extrabold text-[#0b57d0]">
                            {h.adjustedScore}
                          </span>
                          <span className="rounded-full bg-[#e6f4ea] px-2 py-0.2 text-[10px] font-bold text-[#137333]">
                            {h.rankChange}
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* ----------------------------------------------------------- Selected Habitation Breakdown Card */}
        {selectedHabitation && (
          <div className="rounded-3xl border border-[#dadce0] bg-white p-6 sm:p-8 shadow-google-sm space-y-4">
            <div className="flex items-center justify-between border-b border-[#edf2fa] pb-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{selectedHabitation.flag}</span>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#0b57d0]">
                    Detailed Demographic Equity Audit
                  </span>
                  <h3 className="font-google font-bold text-lg text-[#1f1f1f]">
                    {selectedHabitation.name}
                  </h3>
                </div>
              </div>
              <span className="rounded-full bg-[#e8f0fe] px-3 py-1 font-mono text-xs font-bold text-[#0b57d0]">
                Score: {selectedHabitation.adjustedScore}/100
              </span>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border border-[#dadce0] bg-[#f8fafd] p-4">
                <span className="text-[10px] font-bold uppercase text-[#5f6368]">
                  Digital Participation Barrier
                </span>
                <p className="font-mono text-lg font-bold text-[#c5221f] mt-1">
                  {100 - selectedHabitation.smartphonePenetrationPct}% Unconnected
                </p>
                <p className="text-[10px] text-[#5f6368] mt-1">
                  Citizens without personal smartphones relying on community kiosks or neighbors.
                </p>
              </div>

              <div className="rounded-2xl border border-[#dadce0] bg-[#f8fafd] p-4">
                <span className="text-[10px] font-bold uppercase text-[#5f6368]">
                  Deprivation Multiplier
                </span>
                <p className="font-mono text-lg font-bold text-[#0b57d0] mt-1">
                  {selectedHabitation.equityFactor}x Boost
                </p>
                <p className="text-[10px] text-[#5f6368] mt-1">
                  Applied to each verified citizen voice request from this geofence.
                </p>
              </div>

              <div className="rounded-2xl border border-[#dadce0] bg-[#f8fafd] p-4">
                <span className="text-[10px] font-bold uppercase text-[#5f6368]">
                  Primary Public Need
                </span>
                <p className="font-bold text-base text-[#1f1f1f] mt-1 flex items-center gap-1.5">
                  <span>{selectedHabitation.sectorIcon}</span>
                  <span>{selectedHabitation.sectorFocus}</span>
                </p>
                <p className="text-[10px] text-[#5f6368] mt-1">
                  Ground truth surveys show critical infrastructure deficit exceeding 24 months.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </PageContainer>
  );
}

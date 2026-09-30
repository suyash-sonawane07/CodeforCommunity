"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PageContainer } from "@/components/layouts";
import {
  GoogleLogoMark,
  Google4ColorPlus,
  GeminiSparkleIcon,
  GoogleMapPinIcon,
  GoogleMicIcon,
} from "@/components/ui/GoogleIcons";

interface RegionData {
  id: string;
  name: string;
  country: string;
  flag: string;
  demand: number;
  hotspots: number;
  topIssue: string;
  budget: string;
  urgency: string;
}

const REGIONS: RegionData[] = [
  {
    id: "all",
    name: "All BRICS Hubs",
    country: "Global Pilot",
    flag: "🌐",
    demand: 1433,
    hotspots: 6,
    topIssue: "Water Deficit & Grid Vulnerability",
    budget: "$2.4M",
    urgency: "High",
  },
  {
    id: "ind",
    name: "Paithan & Shirur",
    country: "India (Maharashtra)",
    flag: "🇮🇳",
    demand: 642,
    hotspots: 2,
    topIssue: "Irrigation & Potable Water Scarcity",
    budget: "$850K",
    urgency: "Critical",
  },
  {
    id: "bra",
    name: "Favela da Maré & Santos",
    country: "Brazil (Rio & SP)",
    flag: "🇧🇷",
    demand: 489,
    hotspots: 2,
    topIssue: "Drainage Overflow & Hillside Erosion",
    budget: "$920K",
    urgency: "High",
  },
  {
    id: "zaf",
    name: "Soweto & Khayelitsha",
    country: "South Africa (Gauteng & WC)",
    flag: "🇿🇦",
    demand: 302,
    hotspots: 2,
    topIssue: "Substation Failures & Road Lighting",
    budget: "$630K",
    urgency: "Moderate",
  },
];

const PRESET_VOICE_DEMOS = [
  {
    lang: "Marathi (मराठी)",
    code: "mr",
    text: "पैठण गावात गेल्या १५ दिवसांपासून नळाला पाणी नाही, टँकर सुद्धा वेळेवर येत नाही.",
    translation: "Paithan village has had no tap water for 15 days, tankers are not arriving on time.",
    category: "Water Supply",
    urgency: "9.2/10",
    color: "blue",
  },
  {
    lang: "Portuguese (Português)",
    code: "pt",
    text: "O canal da Maré transborda a cada chuva forte e a água suja invade as casas na rua principal.",
    translation: "The Maré canal overflows with heavy rain and dirty water floods main street houses.",
    category: "Drainage / Sanitation",
    urgency: "8.8/10",
    color: "red",
  },
  {
    lang: "English (South Africa)",
    code: "en",
    text: "Frequent transformer explosions in Ward 42 leave the maternity clinic without power.",
    translation: "Frequent transformer explosions in Ward 42 leave the maternity clinic without power.",
    category: "Energy Grid",
    urgency: "9.5/10",
    color: "yellow",
  },
];

export default function HomePage() {
  const [selectedRegion, setSelectedRegion] = useState<RegionData>(REGIONS[0]);
  const [activeVoiceDemo, setActiveVoiceDemo] = useState(PRESET_VOICE_DEMOS[0]);
  const [isPlayingVoice, setIsPlayingVoice] = useState(false);

  const simulateVoicePlayback = (demo: (typeof PRESET_VOICE_DEMOS)[0]) => {
    setActiveVoiceDemo(demo);
    setIsPlayingVoice(true);
    setTimeout(() => setIsPlayingVoice(false), 2200);
  };

  return (
    <PageContainer>
      {/* ------------------------------------------------------------- Google Flagship Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl border border-[#dadce0] bg-white shadow-google-sm transition-all hover:shadow-google-md">
        {/* Google 4-Color Accent Strip */}
        <div className="h-1.5 w-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

        <div className="p-6 sm:p-10 md:p-12">
          <div className="max-w-4xl space-y-5">
            {/* Top Pill Tags */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-[#e8f0fe] px-3.5 py-1 text-xs font-semibold text-[#1a73e8] border border-[#d2e3fc]">
                <GoogleLogoMark className="h-3.5 w-3.5" />
                <span>Google Developer Groups</span>
                <span>•</span>
                <span>Code for Communities 2.0 (Track 1)</span>
              </div>
              <div className="inline-flex items-center gap-1.5 rounded-full bg-gradient-to-r from-[#1ba1e3]/10 to-[#9b51e0]/10 px-3 py-1 text-xs font-semibold text-[#5457cd] border border-[#5457cd]/20">
                <GeminiSparkleIcon className="h-3.5 w-3.5 text-[#5457cd]" />
                <span>Gemini 1.5 Multilingual NLP</span>
              </div>
            </div>

            {/* Main Headline */}
            <div>
              <h1
                aria-label="CivicPulse"
                className="font-google text-4xl sm:text-6xl font-extrabold tracking-tight text-[#1f1f1f]"
              >
                Civic<span className="text-[#1a73e8]">Pulse</span>
              </h1>
              <p className="mt-2 font-google text-lg sm:text-xl font-medium text-[#444746]">
                AI Development-Needs Intelligence Layer for Digital Public Infrastructure
              </p>
            </div>

            <p className="text-sm sm:text-base text-[#5f6368] font-normal leading-relaxed max-w-3xl">
              Translating multilingual citizen voice recordings into transparently ranked public infrastructure
              investments with geospatial PostGIS evidence, deterministic mathematical formulas, and human-governed sign-off.
            </p>

            {/* Test Requirement & Production Readiness Badge */}
            <div className="inline-flex items-center gap-2 rounded-full bg-[#e6f4ea] px-3.5 py-1 text-xs font-medium text-[#137333] border border-[#ceead6]">
              <span className="h-2 w-2 rounded-full bg-[#34a853] animate-pulse" />
              <span>Production-ready UI: Hackathon scaffold placeholder upgraded to Google Material Design 3</span>
            </div>

            {/* Primary Action Buttons */}
            <div className="pt-2 flex flex-wrap items-center gap-3">
              <Link
                href="/citizen"
                className="inline-flex items-center gap-2.5 rounded-full bg-[#0b57d0] px-6 py-3 text-sm font-semibold text-white shadow-google-sm hover:bg-[#0842a0] hover:shadow-google-md transition transform hover:-translate-y-0.5"
              >
                <GoogleMicIcon className="h-4 w-4" />
                <span>Submit Citizen Voice</span>
              </Link>
              <Link
                href="/admin/dashboard"
                className="inline-flex items-center gap-2 rounded-full bg-[#d3e3fd] px-5 py-3 text-sm font-semibold text-[#041e49] hover:bg-[#c2d7fc] transition"
              >
                <span>📊 Command Dashboard</span>
              </Link>
              <Link
                href="/map"
                className="inline-flex items-center gap-2 rounded-full border border-[#747775]/30 bg-white px-5 py-3 text-sm font-semibold text-[#1f1f1f] hover:bg-[#f0f4f9] hover:border-[#1a73e8] transition"
              >
                <GoogleMapPinIcon className="h-4 w-4" color="#EA4335" />
                <span>Geospatial Map</span>
              </Link>
              <Link
                href="/simulator"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-[#1ba1e3]/15 via-[#5457cd]/15 to-[#9b51e0]/15 border border-[#5457cd]/30 px-5 py-3 text-sm font-semibold text-[#041e49] hover:bg-[#5457cd]/25 transition"
              >
                <GeminiSparkleIcon className="h-4 w-4 text-[#5457cd]" />
                <span>Policy Simulator</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------- BRICS Region Selector Bar */}
      <div className="rounded-2xl border border-[#dadce0] bg-white p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-[#5f6368]">
              Active Pilot Hub:
            </span>
            <span className="rounded-full bg-[#f1f3f4] px-2.5 py-0.5 text-xs font-semibold text-[#1f1f1f]">
              {selectedRegion.country}
            </span>
          </div>

          {/* Region Tabs */}
          <div className="flex flex-wrap items-center gap-2">
            {REGIONS.map((region) => {
              const active = selectedRegion.id === region.id;
              return (
                <button
                  key={region.id}
                  onClick={() => setSelectedRegion(region)}
                  className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-xs font-semibold transition ${
                    active
                      ? "bg-[#c2e7ff] text-[#001d35] shadow-sm border border-[#7fcfff]"
                      : "bg-[#f8f9fa] text-[#444746] hover:bg-[#e8eaed] border border-transparent"
                  }`}
                >
                  <span>{region.flag}</span>
                  <span>{region.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------- Dynamic KPI Scorecards (Google Cloud Style) */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {/* Card 1: Demand */}
        <div className="rounded-2xl border border-[#e0e3e7] bg-white p-5 shadow-sm hover:shadow-google-sm hover:border-[#1a73e8] transition">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Independent Demand</span>
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#e8f0fe] text-sm">📢</span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-google text-3xl font-extrabold text-[#1f1f1f]">
              {selectedRegion.demand.toLocaleString()}
            </span>
            <span className="text-xs font-bold text-[#137333]">+14.2%</span>
          </div>
          <p className="mt-1 text-xs text-[#747775]">
            Verified citizen requests (anti-spam clustered)
          </p>
        </div>

        {/* Card 2: Hotspots */}
        <div className="rounded-2xl border border-[#e0e3e7] bg-white p-5 shadow-sm hover:shadow-google-sm hover:border-[#ea4335] transition">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Hotspots</span>
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#fad2cf] text-sm">🗺️</span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-google text-3xl font-extrabold text-[#ea4335]">
              {selectedRegion.hotspots} Hubs
            </span>
            <span className="rounded-full bg-[#fce8e6] px-2 py-0.5 text-[10px] font-bold text-[#c5221f]">
              {selectedRegion.urgency}
            </span>
          </div>
          <p className="mt-1 text-xs text-[#747775]">
            Priority: {selectedRegion.topIssue}
          </p>
        </div>

        {/* Card 3: Explainability */}
        <div className="rounded-2xl border border-[#e0e3e7] bg-white p-5 shadow-sm hover:shadow-google-sm hover:border-[#34a853] transition">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Explainability Index</span>
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#ceead6] text-sm">📐</span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-google text-3xl font-extrabold text-[#137333]">100%</span>
            <span className="text-xs font-bold text-[#137333]">Deterministic</span>
          </div>
          <p className="mt-1 text-xs text-[#747775]">
            Zero black-box ranking; full formula breakdown
          </p>
        </div>

        {/* Card 4: Governance */}
        <div className="rounded-2xl border border-[#e0e3e7] bg-white p-5 shadow-sm hover:shadow-google-sm hover:border-[#fbbc04] transition">
          <div className="flex items-center justify-between text-[#5f6368]">
            <span className="text-xs font-semibold uppercase tracking-wider">Allocation Envelope</span>
            <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#feefc3] text-sm">⚖️</span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-google text-3xl font-extrabold text-[#1f1f1f]">
              {selectedRegion.budget}
            </span>
            <span className="text-xs font-bold text-[#b06000]">CapEx</span>
          </div>
          <p className="mt-1 text-xs text-[#747775]">
            Human review gate RBAC required before sign-off
          </p>
        </div>
      </div>

      {/* ------------------------------------------------------------- Live Interactive Citizen Voice Simulator Widget */}
      <div className="rounded-3xl border border-[#dadce0] bg-white p-6 sm:p-8 shadow-google-sm">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#4285F4] to-[#34A853] text-white shadow-sm">
              <GoogleMicIcon className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-google text-lg font-bold text-[#1f1f1f]">
                Live Multilingual Voice Intake Simulation
              </h2>
              <p className="text-xs text-[#5f6368]">
                Click sample citizen voice recordings across BRICS dialects to test Whisper STT transcription.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#f0f4f9] px-3 py-1 text-xs font-medium text-[#444746]">
              <span>Simulated Whisper STT</span>
            </span>
          </div>
        </div>

        {/* Preset Selector Chips */}
        <div className="grid gap-3 sm:grid-cols-3">
          {PRESET_VOICE_DEMOS.map((demo) => {
            const isSelected = activeVoiceDemo.code === demo.code;
            return (
              <button
                key={demo.code}
                onClick={() => simulateVoicePlayback(demo)}
                className={`flex flex-col items-start p-4 rounded-2xl border text-left transition-all ${
                  isSelected
                    ? "border-[#1a73e8] bg-[#f0f7ff] shadow-google-sm ring-1 ring-[#1a73e8]"
                    : "border-[#e0e3e7] bg-white hover:bg-[#f8f9fa] hover:border-[#bdc1c6]"
                }`}
              >
                <div className="flex w-full items-center justify-between">
                  <span className="text-xs font-bold text-[#1f1f1f]">{demo.lang}</span>
                  <span className="rounded-full bg-white px-2 py-0.5 text-[10px] font-semibold text-[#5f6368] border border-[#dadce0]">
                    {demo.category}
                  </span>
                </div>
                <p className="mt-2 text-xs text-[#444746] line-clamp-2 italic">
                  &ldquo;{demo.text}&rdquo;
                </p>
                <div className="mt-3 flex w-full items-center justify-between text-[11px]">
                  <span className="font-semibold text-[#1a73e8]">
                    {isSelected && isPlayingVoice ? "🔊 Transcribing..." : "▶ Test Audio"}
                  </span>
                  <span className="font-medium text-[#b3261e]">Urgency: {demo.urgency}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Wave Animation & Live Transcription Result */}
        <div className="mt-5 rounded-2xl bg-[#f8fafd] border border-[#e0e3e7] p-4 sm:p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#e8eaed] pb-3 mb-3">
            <div className="flex items-center gap-3">
              {/* Google 4-Color Wave Bars */}
              <div className="flex items-center gap-1 h-6">
                <span className={`w-1.5 rounded-full ${isPlayingVoice ? "google-bar-blue" : "h-3 bg-[#4285f4]"}`} />
                <span className={`w-1.5 rounded-full ${isPlayingVoice ? "google-bar-red" : "h-4 bg-[#ea4335]"}`} />
                <span className={`w-1.5 rounded-full ${isPlayingVoice ? "google-bar-yellow" : "h-2 bg-[#fbbc04]"}`} />
                <span className={`w-1.5 rounded-full ${isPlayingVoice ? "google-bar-green" : "h-5 bg-[#34a853]"}`} />
              </div>
              <span className="text-xs font-bold text-[#1f1f1f]">
                {isPlayingVoice ? "Processing Audio Stream via Whisper & Gemini..." : "Transcription Complete"}
              </span>
            </div>
            <Link
              href="/citizen"
              className="inline-flex items-center gap-1 text-xs font-semibold text-[#0b57d0] hover:underline"
            >
              <span>Open Full Intake Portal</span>
              <span>→</span>
            </Link>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 text-xs">
            <div>
              <span className="font-semibold text-[#5f6368] block mb-1">Original Audio Transcript ({activeVoiceDemo.lang}):</span>
              <p className="font-medium text-[#1f1f1f] bg-white p-2.5 rounded-xl border border-[#dadce0]">
                {activeVoiceDemo.text}
              </p>
            </div>
            <div>
              <span className="font-semibold text-[#5f6368] block mb-1">Gemini Normalized Translation (English DPI):</span>
              <p className="font-medium text-[#1f1f1f] bg-white p-2.5 rounded-xl border border-[#dadce0]">
                {activeVoiceDemo.translation}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ------------------------------------------------------------- Core Interactive Modules Grid */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h2 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f]">
              Interactive System Modules
            </h2>
            <p className="text-xs text-[#5f6368]">
              Comprehensive end-to-end pipeline from citizen voice intake to transparent resource allocation.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-[#f1f3f4] px-3 py-1 text-xs font-semibold text-[#444746]">
              6 End-to-End Screens Live
            </span>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {/* S-01: Citizen Intake */}
          <Link
            href="/citizen"
            className="group relative rounded-3xl border border-[#e0e3e7] bg-white p-6 shadow-sm hover:border-[#1a73e8] hover:shadow-google-md transition transform hover:-translate-y-1"
          >
            <div className="flex items-start justify-between">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#e8f0fe] text-2xl group-hover:scale-110 transition">
                📢
              </span>
              <span className="rounded-full bg-[#e8f0fe] px-2.5 py-0.5 text-[11px] font-semibold text-[#1a73e8]">
                S-01 Portal
              </span>
            </div>
            <h3 className="mt-4 font-google text-lg font-bold text-[#1f1f1f] group-hover:text-[#1a73e8]">
              Citizen Voice &amp; Text Intake
            </h3>
            <p className="mt-1 text-xs text-[#5f6368] leading-relaxed">
              Submit community infrastructure needs in Marathi, Hindi, Portuguese, English, Zulu, or Afrikaans with real-time Speech-to-Text and tracking codes.
            </p>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#1a73e8]">
              <span>Open Intake Portal</span>
              <span>→</span>
            </div>
          </Link>

          {/* S-04: Command Center */}
          <Link
            href="/admin/dashboard"
            className="group relative rounded-3xl border border-[#e0e3e7] bg-white p-6 shadow-sm hover:border-[#1a73e8] hover:shadow-google-md transition transform hover:-translate-y-1"
          >
            <div className="flex items-start justify-between">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#e8f0fe] text-2xl group-hover:scale-110 transition">
                📊
              </span>
              <span className="rounded-full bg-[#e8f0fe] px-2.5 py-0.5 text-[11px] font-semibold text-[#1a73e8]">
                S-04 Center
              </span>
            </div>
            <h3 className="mt-4 font-google text-lg font-bold text-[#1f1f1f] group-hover:text-[#1a73e8]">
              Command Dashboard
            </h3>
            <p className="mt-1 text-xs text-[#5f6368] leading-relaxed">
              Ranked hotspots based on transparent DPI priority formulas. Filter by sector, inspect cluster demand counts, and view factor breakdowns.
            </p>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#1a73e8]">
              <span>View Rankings</span>
              <span>→</span>
            </div>
          </Link>

          {/* S-06: Geospatial Demand Map */}
          <Link
            href="/map"
            className="group relative rounded-3xl border border-[#e0e3e7] bg-white p-6 shadow-sm hover:border-[#34a853] hover:shadow-google-md transition transform hover:-translate-y-1"
          >
            <div className="flex items-start justify-between">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#ceead6] text-2xl group-hover:scale-110 transition">
                🗺️
              </span>
              <span className="rounded-full bg-[#e6f4ea] px-2.5 py-0.5 text-[11px] font-semibold text-[#137333]">
                S-06 GIS Map
              </span>
            </div>
            <h3 className="mt-4 font-google text-lg font-bold text-[#1f1f1f] group-hover:text-[#137333]">
              Geospatial Demand Map
            </h3>
            <p className="mt-1 text-xs text-[#5f6368] leading-relaxed">
              Google Maps styled GIS visualization featuring PostGIS geodesic clusters, infrastructure overlay pins, and location drawer.
            </p>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#137333]">
              <span>Explore Maps</span>
              <span>→</span>
            </div>
          </Link>

          {/* S-11: Policy Simulator */}
          <Link
            href="/simulator"
            className="group relative rounded-3xl border border-[#e0e3e7] bg-white p-6 shadow-sm hover:border-[#fbbc04] hover:shadow-google-md transition transform hover:-translate-y-1"
          >
            <div className="flex items-start justify-between">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#feefc3] text-2xl group-hover:scale-110 transition">
                🧮
              </span>
              <span className="rounded-full bg-[#fef7e0] px-2.5 py-0.5 text-[11px] font-semibold text-[#b06000]">
                S-11 Simulation
              </span>
            </div>
            <h3 className="mt-4 font-google text-lg font-bold text-[#1f1f1f] group-hover:text-[#b06000]">
              Policy What-If Simulator
            </h3>
            <p className="mt-1 text-xs text-[#5f6368] leading-relaxed">
              Model budget allocations across Water, Roads, Health, and Energy with real-time recalculations and advisory policy guidance.
            </p>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#b06000]">
              <span>Run Simulation</span>
              <span>→</span>
            </div>
          </Link>

          {/* S-12: Human Review Gate */}
          <Link
            href="/review"
            className="group relative rounded-3xl border border-[#e0e3e7] bg-white p-6 shadow-sm hover:border-[#ea4335] hover:shadow-google-md transition transform hover:-translate-y-1"
          >
            <div className="flex items-start justify-between">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#fad2cf] text-2xl group-hover:scale-110 transition">
                ⚖️
              </span>
              <span className="rounded-full bg-[#fce8e6] px-2.5 py-0.5 text-[11px] font-semibold text-[#c5221f]">
                S-12 Gate
              </span>
            </div>
            <h3 className="mt-4 font-google text-lg font-bold text-[#1f1f1f] group-hover:text-[#c5221f]">
              Human Review Gate
            </h3>
            <p className="mt-1 text-xs text-[#5f6368] leading-relaxed">
              RBAC approval workflow for flagged high-capex investments. Reviewers can approve, reject, or request more evidence with immutable audit trails.
            </p>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#c5221f]">
              <span>Enter Review Gate</span>
              <span>→</span>
            </div>
          </Link>

          {/* S-15: BRICS Datasets */}
          <Link
            href="/datasets"
            className="group relative rounded-3xl border border-[#e0e3e7] bg-white p-6 shadow-sm hover:border-[#0b57d0] hover:shadow-google-md transition transform hover:-translate-y-1"
          >
            <div className="flex items-start justify-between">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#f0f4f9] text-2xl group-hover:scale-110 transition">
                🏛️
              </span>
              <span className="rounded-full bg-[#f1f3f4] px-2.5 py-0.5 text-[11px] font-semibold text-[#444746]">
                S-15 Catalog
              </span>
            </div>
            <h3 className="mt-4 font-google text-lg font-bold text-[#1f1f1f] group-hover:text-[#0b57d0]">
              BRICS Datasets &amp; Audit Logs
            </h3>
            <p className="mt-1 text-xs text-[#5f6368] leading-relaxed">
              Public dataset repositories for India, Brazil, and South Africa with synthetic source indicators and cryptographically auditable logs.
            </p>
            <div className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#0b57d0]">
              <span>View Datasets</span>
              <span>→</span>
            </div>
          </Link>
        </div>
      </div>

      {/* ------------------------------------------------------------- Transparent DPI Governance Principles */}
      <div className="rounded-3xl border border-[#dadce0] bg-white p-6 sm:p-8 shadow-google-sm">
        <div className="flex items-center gap-2 mb-4">
          <GoogleLogoMark className="h-5 w-5" />
          <h3 className="font-google text-sm font-bold uppercase tracking-wider text-[#444746]">
            Transparent Digital Public Infrastructure Governance
          </h3>
        </div>

        <div className="grid gap-4 sm:grid-cols-3 text-xs">
          <div className="rounded-2xl bg-[#f8fafd] p-5 border border-[#e0e3e7]">
            <span className="font-bold text-[#1f1f1f] block mb-1 text-sm">📐 Deterministic Formula</span>
            <p className="text-[#5f6368] leading-relaxed">
              <code className="text-[#0b57d0] font-mono font-semibold">score = wd·d + wg·g + wi·i + we·e - wf·f</code>.
              Weights are public, reproducible, and explainable with complete mathematical factor breakdowns.
            </p>
          </div>

          <div className="rounded-2xl bg-[#f8fafd] p-5 border border-[#e0e3e7]">
            <span className="font-bold text-[#1f1f1f] block mb-1 text-sm">🛡️ Anti-Astroturfing</span>
            <p className="text-[#5f6368] leading-relaxed">
              Separates raw spam from verified independent citizen demand (<code className="text-[#0b57d0] font-mono font-semibold">independent_demand_count</code>) via semantic clustering and coordinate jitter analysis.
            </p>
          </div>

          <div className="rounded-2xl bg-[#f8fafd] p-5 border border-[#e0e3e7]">
            <span className="font-bold text-[#1f1f1f] block mb-1 text-sm">🏷️ Pilot Simulation Transparency</span>
            <p className="text-[#5f6368] leading-relaxed">
              All demonstration indicators are clearly labeled as <span className="font-bold text-[#b06000]">PILOT SIMULATION</span> with full audit traceability and open source methodologies.
            </p>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}

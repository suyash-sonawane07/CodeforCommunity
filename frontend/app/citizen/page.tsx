"use client";

import React, { useState } from "react";
import { API_BASE_URL } from "@/lib/config";
import type { RequestStatusResponse } from "@/types/api";

const PRESET_LOCATIONS = [
  { label: "Paithan Rural Hub (IND)", text: "Paithan Rural Hub, Paithan" },
  { label: "Shirur Rural Ward (IND)", text: "Shirur Rural Ward, Pune" },
  { label: "Favela da Maré (BRA)", text: "Favela da Maré, Zona Norte, Rio de Janeiro" },
  { label: "Santos Encosta (BRA)", text: "Santos Encosta, Morros, Santos" },
  { label: "Soweto Ward 42 (ZAF)", text: "Soweto Ward 42, Region D, Johannesburg" },
  { label: "Khayelitsha Site C (ZAF)", text: "Khayelitsha Site C, Cape Town" },
];

const PRESET_MESSAGES = [
  {
    lang: "mr",
    label: "Marathi (Water Crisis)",
    text: "पैठण गावात गेल्या १५ दिवसांपासून नळाला पाणी नाही, टँकर सुद्धा वेळेवर येत नाही.",
    loc: "Paithan Rural Hub, Paithan",
  },
  {
    lang: "pt",
    label: "Portuguese (Drainage Overflow)",
    text: "O canal da Maré transborda a cada chuva forte e a água suja invade as casas na rua principal.",
    loc: "Favela da Maré, Zona Norte, Rio de Janeiro",
  },
  {
    lang: "en",
    label: "English (Transformer Breakdown)",
    text: "Frequent transformer explosions in Ward 42 leave the community and local clinic without power for days.",
    loc: "Soweto Ward 42, Region D, Johannesburg",
  },
  {
    lang: "hi",
    label: "Hindi (Rural Transit Deficit)",
    text: "गाँव में शाम 5 बजे के बाद बस नहीं मिलती, छात्रों और महिलाओं को परेशानी होती है।",
    loc: "Demo Village 1, Demo Block A",
  },
];

export default function CitizenPortalPage() {
  const [activeTab, setActiveTab] = useState<"submit" | "track">("submit");

  // Submit form state
  const [channel, setChannel] = useState<"text" | "voice">("text");
  const [languageHint, setLanguageHint] = useState<string>("auto");
  const [text, setText] = useState("");
  const [locationText, setLocationText] = useState("");
  const [consentAck, setConsentAck] = useState(true);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<{
    reference_code: string;
    request_id: string;
    status: string;
  } | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Track state
  const [searchRef, setSearchRef] = useState("");
  const [isTracking, setIsTracking] = useState(false);
  const [trackResult, setTrackResult] = useState<RequestStatusResponse | null>(null);
  const [trackError, setTrackError] = useState<string | null>(null);

  const applyPreset = (preset: (typeof PRESET_MESSAGES)[0]) => {
    setText(preset.text);
    setLocationText(preset.loc);
    setLanguageHint(preset.lang);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!consentAck) {
      setSubmitError("Consent is required to submit a public development request (FR-005).");
      return;
    }
    if (!text.trim() && !audioFile) {
      setSubmitError("Please enter a description or upload an audio voice note.");
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // 1. Create request
      const res = await fetch(`${API_BASE_URL}/requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel,
          language_hint: languageHint === "auto" ? null : languageHint,
          text: text.trim() || undefined,
          location_text: locationText.trim() || undefined,
          consent_ack: consentAck,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.detail?.error?.message || `HTTP ${res.status}`);
      }

      const data = await res.json();

      // 2. If voice audio attached, upload to audio endpoint
      if (channel === "voice" && audioFile && data.request_id) {
        const formData = new FormData();
        formData.append("file", audioFile);
        await fetch(`${API_BASE_URL}/requests/${data.request_id}/audio`, {
          method: "POST",
          body: formData,
        });
      }

      setSubmissionResult(data);
      setSearchRef(data.reference_code);
    } catch (err: any) {
      setSubmitError(err.message || "Failed to submit request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTrack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchRef.trim()) return;

    setIsTracking(true);
    setTrackError(null);
    setTrackResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/requests/${encodeURIComponent(searchRef.trim())}`);
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error(`Reference code "${searchRef}" not found. Verify your tracking code.`);
        }
        throw new Error(`Lookup failed with status ${res.status}`);
      }
      const data = await res.json();
      setTrackResult(data);
    } catch (err: any) {
      setTrackError(err.message || "Failed to retrieve status.");
    } finally {
      setIsTracking(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Citizen Needs Intake & Tracking Portal
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Multilingual Digital Public Infrastructure (DPI) for community issue submission in any BRICS language.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab("submit")}
          className={`border-b-2 px-5 py-3 text-sm font-semibold transition-all ${
            activeTab === "submit"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          📝 Submit New Request
        </button>
        <button
          onClick={() => setActiveTab("track")}
          className={`border-b-2 px-5 py-3 text-sm font-semibold transition-all ${
            activeTab === "track"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          🔍 Track Existing Request
        </button>
      </div>

      {/* Tab 1: Submit */}
      {activeTab === "submit" && (
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            {/* Success Banner */}
            {submissionResult && (
              <div className="rounded-xl border border-emerald-200 bg-emerald-50/80 p-5 shadow-sm">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600 text-white font-bold">
                      ✓
                    </span>
                    <div>
                      <h3 className="font-semibold text-emerald-900">Request Successfully Registered!</h3>
                      <p className="text-xs text-emerald-700">
                        Assigned to regional geospatial demand cluster for municipal analysis.
                      </p>
                    </div>
                  </div>
                  <span className="rounded-md bg-emerald-100 px-2 py-1 font-mono text-xs font-bold text-emerald-800">
                    {submissionResult.status}
                  </span>
                </div>
                <div className="mt-4 rounded-lg bg-white/90 p-3.5 border border-emerald-200/80">
                  <p className="text-xs text-slate-500 font-medium">Your Public Reference Tracking Code:</p>
                  <p className="mt-1 font-mono text-xl font-bold tracking-wider text-slate-900">
                    {submissionResult.reference_code}
                  </p>
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={() => {
                        setSearchRef(submissionResult.reference_code);
                        setActiveTab("track");
                      }}
                      className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 transition"
                    >
                      View Live Tracking Status →
                    </button>
                    <button
                      onClick={() => setSubmissionResult(null)}
                      className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
                    >
                      Submit Another
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Submission Form */}
            <form onSubmit={handleSubmit} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
              {submitError && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3.5 text-xs font-medium text-red-700">
                  ⚠️ {submitError}
                </div>
              )}

              {/* Channel & Language Bar */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Intake Channel
                  </label>
                  <div className="mt-1 flex rounded-lg border border-slate-200 p-1 bg-slate-50">
                    <button
                      type="button"
                      onClick={() => setChannel("text")}
                      className={`flex-1 rounded-md py-1.5 text-xs font-semibold transition ${
                        channel === "text" ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      💬 Text
                    </button>
                    <button
                      type="button"
                      onClick={() => setChannel("voice")}
                      className={`flex-1 rounded-md py-1.5 text-xs font-semibold transition ${
                        channel === "voice" ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      🎙️ Voice / Audio
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Language Hint
                  </label>
                  <select
                    value={languageHint}
                    onChange={(e) => setLanguageHint(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="auto">Auto-Detect (Any BRICS Language)</option>
                    <option value="mr">Marathi (मराठी)</option>
                    <option value="hi">Hindi (हिंदी)</option>
                    <option value="pt">Portuguese (Português)</option>
                    <option value="en">English</option>
                  </select>
                </div>
              </div>

              {/* Voice file upload if voice selected */}
              {channel === "voice" && (
                <div className="rounded-lg border-2 border-dashed border-slate-200 bg-slate-50/70 p-4 text-center">
                  <p className="text-xs font-medium text-slate-700">Attach Voice Note or Audio File (WAV, MP3, OGG)</p>
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                    className="mt-2 text-xs text-slate-500 file:mr-3 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-1 file:text-xs file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {audioFile && (
                    <p className="mt-1 text-xs text-emerald-600 font-medium">Selected: {audioFile.name}</p>
                  )}
                </div>
              )}

              {/* Request Text */}
              <div>
                <div className="flex justify-between items-center">
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                    Community Need Description
                  </label>
                  <span className="text-[11px] text-slate-400">{text.length} characters</span>
                </div>
                <textarea
                  rows={4}
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Describe the issue (e.g. broken road, missing water connection, clinic shortage)..."
                  className="mt-1 block w-full rounded-lg border border-slate-200 p-3 text-sm text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              {/* Location Input */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Location (Village, Ward, Landmark or City)
                </label>
                <input
                  type="text"
                  value={locationText}
                  onChange={(e) => setLocationText(e.target.value)}
                  placeholder="e.g. Paithan Rural Hub, Favela da Maré, or Soweto Ward 42"
                  className="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {/* Location Quick Chips */}
                <div className="mt-2 flex flex-wrap gap-1.5">
                  <span className="text-[11px] text-slate-400 self-center mr-1">Quick Select:</span>
                  {PRESET_LOCATIONS.map((loc) => (
                    <button
                      type="button"
                      key={loc.label}
                      onClick={() => setLocationText(loc.text)}
                      className="rounded-full bg-slate-100 hover:bg-blue-50 hover:text-blue-700 border border-slate-200/80 px-2.5 py-0.5 text-[11px] font-medium text-slate-600 transition"
                    >
                      {loc.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Consent Ack (Mandatory FR-005) */}
              <div className="flex items-start gap-2.5 rounded-lg bg-blue-50/60 p-3.5 border border-blue-200/60">
                <input
                  type="checkbox"
                  id="consent_ack"
                  checked={consentAck}
                  onChange={(e) => setConsentAck(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="consent_ack" className="text-xs text-slate-700">
                  <span className="font-semibold">Privacy & Open Governance Consent (FR-005):</span> I consent to
                  anonymized processing of this report for municipal public infrastructure planning. No personal identification is stored.
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-blue-500/20 hover:from-blue-700 hover:to-indigo-700 transition disabled:opacity-50"
              >
                {isSubmitting ? "Processing through AI Intake..." : "Submit Public Development Request"}
              </button>
            </form>
          </div>

          {/* Preset Demonstrations Sidebar */}
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                BRICS Demo Scenarios
              </h3>
              <p className="mt-1 text-xs text-slate-500">
                Click any benchmark case to populate multilingual test inputs:
              </p>
              <div className="mt-3 space-y-2.5">
                {PRESET_MESSAGES.map((preset) => (
                  <button
                    key={preset.label}
                    type="button"
                    onClick={() => applyPreset(preset)}
                    className="w-full text-left rounded-lg border border-slate-200 p-3 hover:border-blue-400 hover:bg-blue-50/40 transition group"
                  >
                    <p className="text-xs font-bold text-blue-700 group-hover:text-blue-800">
                      {preset.label}
                    </p>
                    <p className="mt-1 text-xs text-slate-600 line-clamp-2 italic">
                      &ldquo;{preset.text}&rdquo;
                    </p>
                    <p className="mt-1 text-[11px] text-slate-400 font-medium">📍 {preset.loc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs text-slate-600 space-y-2">
              <p className="font-semibold text-slate-800">Governance Integrity (FR-005/FR-057):</p>
              <ul className="list-disc pl-4 space-y-1 text-[11px] text-slate-500">
                <li>Immutable raw message recording.</li>
                <li>Zero token required for citizen status lookup.</li>
                <li>Real-time automated deduplication against existing clusters.</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Track */}
      {activeTab === "track" && (
        <div className="max-w-2xl mx-auto space-y-6">
          <form onSubmit={handleTrack} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900">
              Track Request by Reference Code
            </h2>
            <p className="text-xs text-slate-500">
              Enter your public tracking code (e.g. <span className="font-mono text-blue-600">CP-2026-IND001</span> or <span className="font-mono text-blue-600">CP-2026-004821</span>) to check processing stage and cluster assignment.
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchRef}
                onChange={(e) => setSearchRef(e.target.value)}
                placeholder="CP-2026-XXXXXX"
                className="flex-1 rounded-lg border border-slate-200 px-3 py-2 font-mono text-sm uppercase placeholder:normal-case focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={isTracking}
                className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition disabled:opacity-50"
              >
                {isTracking ? "Checking..." : "Track"}
              </button>
            </div>
          </form>

          {trackError && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">
              ❌ {trackError}
            </div>
          )}

          {trackResult && (
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Reference Code</p>
                  <p className="font-mono text-lg font-bold text-blue-700">{trackResult.reference_code}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</p>
                  <span className="inline-block mt-0.5 rounded-full bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 text-xs font-bold text-emerald-700 capitalize">
                    {trackResult.status}
                  </span>
                </div>
              </div>

              {/* Timeline Steps */}
              <div>
                <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-3">Processing Lifecycle</p>
                <div className="grid grid-cols-4 gap-2 text-center text-xs">
                  <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2 font-medium text-emerald-800">
                    1. Received ✓
                  </div>
                  <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2 font-medium text-emerald-800">
                    2. AI NLP ✓
                  </div>
                  <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-2 font-medium text-emerald-800">
                    3. Geocoded ✓
                  </div>
                  <div className="rounded-lg bg-blue-600 text-white p-2 font-bold shadow-sm">
                    4. Clustered 📍
                  </div>
                </div>
              </div>

              {/* Details Grid */}
              <div className="rounded-lg bg-slate-50 p-4 border border-slate-100 space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Internal ID:</span>
                  <span className="font-mono text-slate-800">{trackResult.request_id}</span>
                </div>
                {trackResult.language && (
                  <div className="flex justify-between">
                    <span className="text-slate-500">Detected Language:</span>
                    <span className="font-semibold text-slate-800 uppercase">{trackResult.language}</span>
                  </div>
                )}
                {trackResult.transcript && (
                  <div>
                    <span className="text-slate-500 block">Transcript:</span>
                    <p className="mt-1 italic text-slate-700 bg-white p-2 rounded border border-slate-200/60">
                      &ldquo;{trackResult.transcript}&rdquo;
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

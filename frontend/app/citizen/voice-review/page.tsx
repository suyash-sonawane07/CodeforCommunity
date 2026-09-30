"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { PageContainer } from "@/components/layouts";
import { GeminiSparkleIcon, GoogleLogoMark } from "@/components/ui/GoogleIcons";

export default function VoiceReviewPage() {
  const router = useRouter();
  const [transcription, setTranscription] = useState(
    "पैठण गावात गेल्या १५ दिवसांपासून नळाला पाणी नाही. मुख्य पाइपलाइन फुटली आहे आणि पिण्याच्या पाण्याचा गंभीर तुटवडा निर्माण झाला आहे."
  );
  const [normalizedSummary, setNormalizedSummary] = useState(
    "No tap water in Paithan village for the past 15 days due to a burst main pipeline, causing severe drinking water shortage."
  );
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleConfirm = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      router.push("/citizen/confirmation");
    }, 800);
  };

  return (
    <PageContainer>
      <div className="space-y-6 max-w-3xl mx-auto py-4">
        {/* Google 4-Color Accent Strip */}
        <div className="h-1.5 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

        <div className="rounded-3xl border border-[#dadce0] bg-white p-6 sm:p-10 shadow-google-sm space-y-6">
          {/* Header */}
          <div className="border-b border-[#edf2fa] pb-4">
            <span className="rounded-full bg-[#e8f0fe] px-3 py-0.5 text-xs font-bold text-[#0b57d0] border border-[#d2e3fc]">
              Audio Intelligence Review
            </span>
            <h1 className="mt-2 font-google text-2xl font-bold tracking-tight text-[#1f1f1f]">
              Review Your Voice Request
            </h1>
            <p className="mt-1 text-xs text-[#5f6368]">
              Verify or refine the automated speech transcription before municipal ingestion.
            </p>
          </div>

          {/* Audio Player Card */}
          <div className="rounded-2xl border border-[#dadce0] bg-[#f8fafd] p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex h-12 w-12 items-center justify-center rounded-full bg-[#0b57d0] text-white shadow-google-sm hover:bg-[#0842a0] transition"
              >
                {isPlaying ? "⏸️" : "▶️"}
              </button>
              <div>
                <span className="font-bold text-xs text-[#1f1f1f] block">
                  Citizen Voice Note (0:18)
                </span>
                <span className="text-[11px] text-[#5f6368]">
                  Recorded on Oct 1, 2026 • High Quality
                </span>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <span className="rounded-full bg-[#ceead6] px-2.5 py-0.5 text-[11px] font-bold text-[#0d652d]">
                Marathi (mr) • 98% Confidence
              </span>
            </div>
          </div>

          {/* Editable Original Transcription */}
          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-[#5f6368]">
              Original Voice Transcription (Editable)
            </label>
            <textarea
              rows={4}
              value={transcription}
              onChange={(e) => setTranscription(e.target.value)}
              className="w-full rounded-2xl border border-[#dadce0] bg-white p-4 text-xs text-[#1f1f1f] leading-relaxed focus:border-[#0b57d0] focus:shadow-google-sm outline-none transition"
              placeholder="Edit transcription if any word was misheard..."
            />
            <p className="text-[11px] text-[#747775]">
              You can modify or clarify any words if the automated transcription was inaccurate.
            </p>
          </div>

          {/* Gemini AI Normalized English Summary */}
          <div className="rounded-2xl border border-[#d2e3fc] bg-[#f0f7ff] p-5 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#041e49]">
              <GeminiSparkleIcon className="h-4 w-4 text-[#0b57d0]" />
              <span>Google Gemini Normalized English Summary</span>
            </div>
            <p className="text-xs text-[#174ea6] leading-relaxed">
              &ldquo;{normalizedSummary}&rdquo;
            </p>
            <div className="flex flex-wrap gap-2 pt-2 text-[10px]">
              <span className="rounded-full bg-white px-2.5 py-0.5 font-bold text-[#0b57d0] border border-[#d2e3fc]">
                Sector: Water &amp; Sanitation
              </span>
              <span className="rounded-full bg-white px-2.5 py-0.5 font-bold text-[#137333] border border-[#ceead6]">
                Detected Urgency: High (15 days deficit)
              </span>
              <span className="rounded-full bg-white px-2.5 py-0.5 font-bold text-[#b06000] border border-[#feefc3]">
                Location: Paithan Rural Hub
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-end gap-3 pt-4 border-t border-[#edf2fa]">
            <Link
              href="/citizen"
              className="w-full sm:w-auto text-center rounded-full border border-[#dadce0] bg-white px-5 py-2.5 text-xs font-semibold text-[#5f6368] hover:bg-[#f8fafd] transition"
            >
              Discard &amp; Re-record
            </Link>
            <button
              onClick={handleConfirm}
              disabled={isSubmitting}
              className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-full bg-[#0b57d0] px-6 py-2.5 text-xs font-semibold text-white shadow-google-sm hover:bg-[#0842a0] transition"
            >
              <span>{isSubmitting ? "Submitting..." : "✓ Confirm & Submit Request"}</span>
            </button>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}

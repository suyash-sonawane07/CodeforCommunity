"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PageContainer } from "@/components/layouts";
import { GoogleMapPinIcon } from "@/components/ui/GoogleIcons";

export default function ConfirmationPage() {
  const [copied, setCopied] = useState(false);
  const refCode = "CP-2026-IND-8492";

  const handleCopy = () => {
    navigator.clipboard.writeText(refCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <PageContainer>
      <div className="space-y-6 max-w-3xl mx-auto py-6">
        {/* Google 4-Color Accent Strip */}
        <div className="h-1.5 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

        {/* Main Success Card */}
        <div className="rounded-3xl border border-[#dadce0] bg-white p-8 sm:p-12 shadow-google-md text-center space-y-6">
          <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-[#e6f4ea] text-3xl text-[#137333] shadow-inner">
            ✓
          </div>

          <div className="space-y-2">
            <span className="rounded-full bg-[#e6f4ea] px-3.5 py-1 text-xs font-bold text-[#137333] border border-[#ceead6]">
              Verified &amp; Cryptographically Logged
            </span>
            <h1 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f] sm:text-3xl">
              Public Development Request Submitted
            </h1>
            <p className="max-w-md mx-auto text-xs text-[#5f6368] leading-relaxed">
              Your request has been securely anonymized, processed through our Google Gemini language engine, and queued for spatial cluster aggregation.
            </p>
          </div>

          {/* Reference Tracking Code Box */}
          <div className="rounded-2xl border border-[#dadce0] bg-[#f8fafd] p-5 max-w-md mx-auto space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-[#747775] block">
              Public Tracking Reference ID
            </span>
            <div className="flex items-center justify-center gap-3">
              <span className="font-mono text-xl font-extrabold text-[#0b57d0]">
                {refCode}
              </span>
              <button
                onClick={handleCopy}
                className="rounded-full border border-[#dadce0] bg-white px-3 py-1 text-xs font-semibold text-[#1f1f1f] shadow-google-sm hover:bg-[#f0f4f9] transition"
              >
                {copied ? "✓ Copied" : "Copy ID"}
              </button>
            </div>
            <p className="text-[10px] text-[#747775]">
              Use this reference ID to track your request on the open GIS map.
            </p>
          </div>

          {/* Verification Pipeline Steps */}
          <div className="grid gap-3 sm:grid-cols-3 text-left text-xs pt-4 border-t border-[#edf2fa]">
            <div className="rounded-2xl bg-[#f8fafd] p-4 border border-[#dadce0]">
              <span className="font-bold text-[#1f1f1f] block mb-1">1. PII Stripping</span>
              <p className="text-[#5f6368] text-[11px]">
                Names, phone numbers, and private tokens removed before storage.
              </p>
            </div>
            <div className="rounded-2xl bg-[#f8fafd] p-4 border border-[#dadce0]">
              <span className="font-bold text-[#1f1f1f] block mb-1">2. Spatial Clustered</span>
              <p className="text-[#5f6368] text-[11px]">
                Grouped with nearby community reports within 650m PostGIS buffer.
              </p>
            </div>
            <div className="rounded-2xl bg-[#f8fafd] p-4 border border-[#dadce0]">
              <span className="font-bold text-[#1f1f1f] block mb-1">3. Human Review</span>
              <p className="text-[#5f6368] text-[11px]">
                Submitted to municipal reviewers for capital allocation scoring.
              </p>
            </div>
          </div>

          {/* Navigation Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Link
              href="/map"
              className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-full bg-[#0b57d0] px-6 py-3 text-xs font-semibold text-white shadow-google-sm hover:bg-[#0842a0] transition"
            >
              <GoogleMapPinIcon className="h-4 w-4" color="#ffffff" />
              <span>Explore Public GIS Map</span>
            </Link>
            <Link
              href="/citizen"
              className="flex w-full sm:w-auto items-center justify-center gap-2 rounded-full border border-[#dadce0] bg-white px-6 py-3 text-xs font-semibold text-[#1f1f1f] shadow-google-sm hover:bg-[#f8fafd] transition"
            >
              <span>➕ Submit Another Request</span>
            </Link>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}

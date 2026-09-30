"use client";

import React, { useState } from "react";
import { useAuth } from "@/hooks";
import Link from "next/link";
import { GoogleLogoMark } from "@/components/ui/GoogleIcons";

export default function SignupPage() {
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(email, password);
  };

  return (
    <div className="min-h-screen bg-[#f8fafd] flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-3xl border border-[#dadce0] bg-white p-8 shadow-google-md space-y-6">
        {/* Google 4-Color Accent Strip */}
        <div className="h-1 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

        <div className="text-center space-y-2">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm ring-1 ring-black/5">
            <GoogleLogoMark className="h-7 w-7" />
          </div>
          <h1 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f]">
            Create CivicPulse Account
          </h1>
          <p className="text-xs text-[#5f6368]">
            Register as a community member to voice local infrastructure needs
          </p>
        </div>

        {error && (
          <div className="rounded-2xl border border-[#fad2cf] bg-[#fce8e6] p-3 text-xs font-semibold text-[#c5221f]">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[#444746] mb-1">Full Name</label>
            <input
              type="text"
              className="w-full rounded-2xl border border-[#dadce0] bg-[#f8fafd] px-4 py-2.5 text-xs text-[#1f1f1f] focus:border-[#0b57d0] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#0b57d0]"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Ramesh Patil / Maria Silva"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#444746] mb-1">Email Address</label>
            <input
              type="email"
              className="w-full rounded-2xl border border-[#dadce0] bg-[#f8fafd] px-4 py-2.5 text-xs text-[#1f1f1f] focus:border-[#0b57d0] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#0b57d0]"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="citizen@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#444746] mb-1">Password</label>
            <input
              type="password"
              className="w-full rounded-2xl border border-[#dadce0] bg-[#f8fafd] px-4 py-2.5 text-xs text-[#1f1f1f] focus:border-[#0b57d0] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#0b57d0]"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full bg-[#0b57d0] py-3 text-xs font-bold text-white shadow-google-sm hover:bg-[#0842a0] hover:shadow-google-md transition disabled:opacity-50"
          >
            {loading ? "Creating Account..." : "Create Account &amp; Sign In →"}
          </button>
        </form>

        <div className="text-center text-xs text-[#5f6368] pt-2 border-t border-[#edf2fa]">
          <Link href="/login" className="text-[#0b57d0] hover:underline font-semibold">
            Already have an account? Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

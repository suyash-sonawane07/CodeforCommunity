"use client";

import React, { useState, Suspense } from "react";
import { useAuth } from "@/hooks";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { GoogleLogoMark } from "@/components/ui/GoogleIcons";

function LoginForm() {
  const { login, loading, error } = useAuth();
  const searchParams = useSearchParams();
  const expired = searchParams.get("expired");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(email, password);
  };

  const fillDemoUser = () => {
    setEmail("user@demo.com");
    setPassword("demo123");
  };

  const fillDemoSupervisor = () => {
    setEmail("supervisor@demo.com");
    setPassword("demo123");
  };

  return (
    <div className="w-full max-w-md rounded-3xl border border-[#dadce0] bg-white p-8 shadow-google-md space-y-6">
      {/* Google 4-Color Accent Strip */}
      <div className="h-1 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

      <div className="text-center space-y-2">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white shadow-sm ring-1 ring-black/5">
          <GoogleLogoMark className="h-7 w-7" />
        </div>
        <h1 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f]">
          CivicPulse Sign-In
        </h1>
        <p className="text-xs text-[#5f6368]">
          Sign in to access your citizen requests &amp; community petitions
        </p>
      </div>

      {expired && !error && (
        <div className="rounded-2xl border border-[#feefc3] bg-[#fef7e0] p-3 text-xs font-semibold text-[#523600]">
          Your session has expired. Please sign in again.
        </div>
      )}

      {error && (
        <div className="rounded-2xl border border-[#fad2cf] bg-[#fce8e6] p-3 text-xs font-semibold text-[#c5221f]">
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-[#444746] mb-1">Email</label>
          <input
            type="email"
            className="w-full rounded-2xl border border-[#dadce0] bg-[#f8fafd] px-4 py-2.5 text-xs text-[#1f1f1f] focus:border-[#0b57d0] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#0b57d0]"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="citizen@example.com"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#444746] mb-1">Password</label>
          <input
            type="password"
            className="w-full rounded-2xl border border-[#dadce0] bg-[#f8fafd] px-4 py-2.5 text-xs text-[#1f1f1f] focus:border-[#0b57d0] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#0b57d0]"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-full bg-[#0b57d0] py-3 text-xs font-bold text-white shadow-google-sm hover:bg-[#0842a0] hover:shadow-google-md transition disabled:opacity-50"
        >
          {loading ? "Signing in..." : "Continue to CivicPulse →"}
        </button>
      </form>

      <div className="pt-2 border-t border-[#edf2fa] space-y-3">
        <p className="text-[11px] text-center text-[#5f6368] font-medium">Quick fill demo accounts:</p>
        <div className="flex gap-2 justify-center">
          <button
            onClick={fillDemoUser}
            type="button"
            className="rounded-full bg-[#f0f4f9] px-3.5 py-1 text-xs font-semibold text-[#1f1f1f] hover:bg-[#e0e3e7] transition border border-[#dadce0]"
          >
            👤 Demo Citizen
          </button>
          <button
            onClick={fillDemoSupervisor}
            type="button"
            className="rounded-full bg-[#f0f4f9] px-3.5 py-1 text-xs font-semibold text-[#1f1f1f] hover:bg-[#e0e3e7] transition border border-[#dadce0]"
          >
            🛡️ Demo Supervisor
          </button>
        </div>
      </div>

      <div className="text-center text-xs text-[#5f6368] pt-2">
        <Link href="/admin" className="text-[#0b57d0] hover:underline font-semibold block mb-1">
          Are you a municipal official or reviewer? Sign in here →
        </Link>
        <Link href="/signup" className="text-[#5f6368] hover:underline">
          Need a citizen account? Sign up
        </Link>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-[#f8fafd] flex items-center justify-center p-4">
      <Suspense
        fallback={
          <div className="w-full max-w-md rounded-3xl border border-[#dadce0] bg-white p-8 text-center text-xs text-[#5f6368]">
            Loading CivicPulse sign-in...
          </div>
        }
      >
        <LoginForm />
      </Suspense>
    </div>
  );
}

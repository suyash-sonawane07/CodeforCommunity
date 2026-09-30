"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { PageContainer } from "@/components/layouts";
import { API_BASE_URL } from "@/lib/config";

const DEMO_ACCOUNTS = [
  { role: "analyst", name: "Demo Analyst", email: "analyst@civicpulse.dev", desc: "Cluster exploration, gap detection, evidence panel view" },
  { role: "reviewer", name: "Demo Reviewer", email: "reviewer@civicpulse.dev", desc: "Human review gate (approve / reject / corrections)" },
  { role: "decision_maker", name: "Demo Decision-Maker", email: "decision@civicpulse.dev", desc: "Policy what-if simulator & capital budget allocation" },
  { role: "admin", name: "Demo Admin", email: "admin@civicpulse.dev", desc: "Public dataset registry & immutable audit trails" },
];

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("analyst@civicpulse.dev");
  const [password, setPassword] = useState("password");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (loginEmail?: string) => {
    const targetEmail = loginEmail || email;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: targetEmail, password: "password" }),
      });
      if (!res.ok) throw new Error("Invalid credentials");
      const data = await res.json();
      localStorage.setItem("civicpulse_token", data.access_token);
      localStorage.setItem("civicpulse_active_role", data.role);
      router.push("/admin/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageContainer>
      <div className="max-w-2xl mx-auto space-y-8 py-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Staff & Decision-Maker Authentication
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Sign in with your role-based credentials or select a one-click evaluative profile below.
          </p>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-xs font-semibold text-red-700">
            ⚠️ {error}
          </div>
        )}

        {/* Manual Login Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wide">Enter Credentials</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <button
              onClick={() => handleLogin()}
              disabled={loading}
              className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? "Authenticating..." : "Sign In to Command Center →"}
            </button>
          </div>
        </div>

        {/* 1-Click Role Profiles for Judges */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-6 space-y-4">
          <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Quick 1-Click Role Profiles (Evaluator Shortcut)
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.role}
                onClick={() => handleLogin(acc.email)}
                className="text-left rounded-lg border border-slate-200 bg-white p-3.5 hover:border-blue-400 hover:bg-blue-50/40 transition group shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-900 group-hover:text-blue-700">
                    {acc.name}
                  </span>
                  <span className="rounded bg-slate-100 text-[10px] font-mono px-1.5 py-0.5 text-slate-600">
                    {acc.role}
                  </span>
                </div>
                <p className="mt-1 text-[11px] text-slate-500 line-clamp-2">{acc.desc}</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}

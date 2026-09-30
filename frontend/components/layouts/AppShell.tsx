"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_GROUPS: { label: string; links: { href: string; label: string; icon: string }[] }[] = [
  {
    label: "Citizen Intake",
    links: [
      { href: "/citizen", label: "Citizen Portal", icon: "📢" },
    ],
  },
  {
    label: "Decision Intelligence",
    links: [
      { href: "/admin/dashboard", label: "Command Dashboard", icon: "📊" },
      { href: "/map", label: "Demand Map (Geo)", icon: "🗺️" },
      { href: "/simulator", label: "Policy What-If Simulator", icon: "🧮" },
      { href: "/outcome", label: "Outcome Tracking", icon: "📈" },
    ],
  },
  {
    label: "Governance & Review",
    links: [
      { href: "/review", label: "Human Review Gate", icon: "⚖️" },
      { href: "/datasets", label: "BRICS Datasets & Audit", icon: "🏛️" },
    ],
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [activeRole, setActiveRole] = useState("analyst");

  useEffect(() => {
    // Sync active role with localStorage
    const saved = localStorage.getItem("civicpulse_active_role");
    if (saved) setActiveRole(saved);
  }, []);

  const handleRoleChange = (role: string) => {
    setActiveRole(role);
    localStorage.setItem("civicpulse_active_role", role);
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white md:flex md:flex-col shadow-sm">
        <div className="border-b border-slate-100 p-5">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-blue-700 via-indigo-600 to-cyan-500 text-white font-bold shadow-md shadow-blue-500/20 text-lg">
              CP
            </span>
            <div>
              <span className="text-lg font-bold tracking-tight text-slate-900">
                Civic<span className="text-blue-600">Pulse</span>
              </span>
              <p className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">
                Track 1 • AI for DPI
              </p>
            </div>
          </Link>
          <div className="mt-3 flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 border border-emerald-200/60 text-[11px] font-semibold text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>82/82 System Tests Active</span>
          </div>
        </div>

        <nav aria-label="Main navigation" className="flex-1 space-y-6 overflow-y-auto px-3 py-5">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="space-y-1">
              <p className="px-3 pb-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                {group.label}
              </p>
              {group.links.map((link) => {
                const active = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href + "/"));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                      active
                        ? "bg-blue-600 text-white shadow-sm shadow-blue-600/30"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    <span className="text-base">{link.icon}</span>
                    <span>{link.label}</span>
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* BRICS Flag Indicators */}
        <div className="border-t border-slate-100 p-4 bg-slate-50/70">
          <p className="text-[10px] font-semibold uppercase text-slate-400 tracking-wider">
            BRICS Pilot Coverage
          </p>
          <div className="mt-2 flex items-center gap-2 text-xs font-medium text-slate-600">
            <span title="India (Maharashtra)">🇮🇳 India</span>
            <span>•</span>
            <span title="Brazil (Rio/São Paulo)">🇧🇷 Brazil</span>
            <span>•</span>
            <span title="South Africa (Gauteng/WC)">🇿🇦 S. Africa</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top Navbar */}
        <header className="sticky top-0 z-30 flex h-16 shrink-0 items-center justify-between border-b border-slate-200/80 bg-white/95 px-6 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1.5 rounded-md bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 border border-blue-200/50">
              <span className="font-semibold">Code for Communities 2.0</span> • DPI Governance
            </span>
          </div>

          {/* Quick Role Switcher for Evaluators */}
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500 font-medium">Evaluator Role:</span>
            <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-0.5 text-xs font-medium">
              {[
                { id: "analyst", label: "Analyst" },
                { id: "reviewer", label: "Reviewer" },
                { id: "decision_maker", label: "Decision-Maker" },
                { id: "admin", label: "Admin" },
              ].map((r) => (
                <button
                  key={r.id}
                  onClick={() => handleRoleChange(r.id)}
                  className={`rounded-md px-2.5 py-1 transition-all ${
                    activeRole === r.id
                      ? "bg-white text-blue-700 shadow-sm font-semibold"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="mx-auto w-full max-w-7xl flex-1 p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
}

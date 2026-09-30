"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  GoogleLogoMark,
  Google4ColorPlus,
  GoogleWaffleIcon,
  GoogleSearchIcon,
  GoogleMicIcon,
  GoogleLensIcon,
  GeminiSparkleIcon,
} from "@/components/ui/GoogleIcons";
import { GoogleSearchModal } from "@/components/ui/GoogleSearchModal";
import { GoogleWaffleMenu } from "@/components/ui/GoogleWaffleMenu";
import { GoogleRoleAccountMenu } from "@/components/ui/GoogleRoleAccountMenu";
import { GeminiCopilot } from "@/components/ui/GeminiCopilot";

const NAV_GROUPS: {
  label: string;
  links: { href: string; label: string; icon: string; badge?: string }[];
}[] = [
  {
    label: "Main",
    links: [
      { href: "/", label: "Overview Hub", icon: "🏠" },
      { href: "/citizen", label: "Citizen Intake", icon: "📢", badge: "STT" },
    ],
  },
  {
    label: "Decision Intelligence",
    links: [
      { href: "/admin/dashboard", label: "Command Center", icon: "📊" },
      { href: "/map", label: "Geospatial Map", icon: "🗺️", badge: "GIS" },
      { href: "/simulator", label: "Policy Simulator", icon: "🧮" },
      { href: "/outcome", label: "Outcome Tracking", icon: "📈" },
    ],
  },
  {
    label: "Governance & DPI",
    links: [
      { href: "/review", label: "Human Review Gate", icon: "⚖️", badge: "RBAC" },
      { href: "/datasets", label: "BRICS Datasets & Audit", icon: "🏛️" },
    ],
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const [activeRole, setActiveRole] = useState("analyst");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Modals state
  const [searchOpen, setSearchOpen] = useState(false);
  const [waffleOpen, setWaffleOpen] = useState(false);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [geminiOpen, setGeminiOpen] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("civicpulse_active_role");
    if (saved) setActiveRole(saved);

    // Keyboard shortcut for search
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleRoleChange = (role: string) => {
    setActiveRole(role);
    localStorage.setItem("civicpulse_active_role", role);
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#f8fafd] text-[#1f1f1f] font-sans">
      {/* ------------------------------------------------------------- Google Top App Bar */}
      <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-[#e0e3e7] bg-white/95 px-4 md:px-6 backdrop-blur-md">
        {/* Left Section: Menu Toggle & Google Branding */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              if (window.innerWidth < 768) {
                setMobileMenuOpen(!mobileMenuOpen);
              } else {
                setSidebarOpen(!sidebarOpen);
              }
            }}
            aria-label="Toggle Navigation Drawer"
            className="flex h-10 w-10 items-center justify-center rounded-full text-[#5f6368] hover:bg-[#f0f4f9] transition"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white shadow-sm ring-1 ring-black/5 hover:scale-105 transition">
              <GoogleLogoMark className="h-6 w-6" />
            </div>
            <div>
              <span className="font-google text-lg font-bold tracking-tight text-[#1f1f1f]">
                Civic<span className="text-[#1a73e8]">Pulse</span>
              </span>
              <p className="text-[10px] font-semibold text-[#5f6368] tracking-wider">
                Google Developer Groups • DPI Layer
              </p>
            </div>
          </Link>
        </div>

        {/* Center Section: Google Search Capsule */}
        <div className="hidden flex-1 max-w-xl mx-4 sm:flex items-center">
          <div
            onClick={() => setSearchOpen(true)}
            className="flex w-full cursor-pointer items-center justify-between rounded-full border border-transparent bg-[#f0f4f9] px-4 py-2 text-sm text-[#444746] shadow-inner hover:border-[#dadce0] hover:bg-white hover:shadow-google-sm transition-all"
          >
            <div className="flex items-center gap-3 flex-1">
              <GoogleSearchIcon className="h-4 w-4 text-[#5f6368]" />
              <span className="text-xs text-[#747775]">
                Search citizen requests, clusters, coordinates...
              </span>
            </div>
            <div className="flex items-center gap-2">
              <kbd className="hidden lg:inline-block rounded-md bg-[#e8eaed] px-2 py-0.5 text-[10px] font-semibold text-[#5f6368]">
                ⌘K
              </kbd>
              <GoogleMicIcon className="h-4 w-4" />
              <GoogleLensIcon className="h-4 w-4" />
            </div>
          </div>
        </div>

        {/* Right Section: Actions, Copilot & Account */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Gemini AI Copilot Button */}
          <button
            onClick={() => setGeminiOpen(true)}
            className="group relative inline-flex items-center gap-2 rounded-full border border-transparent bg-gradient-to-r from-[#1ba1e3]/10 via-[#5457cd]/10 to-[#9b51e0]/10 px-3.5 py-1.5 text-xs font-semibold text-[#0b57d0] hover:bg-[#e8f0fe] hover:shadow-google-sm transition"
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-tr from-[#1ba1e3] to-[#9b51e0] text-white">
              <GeminiSparkleIcon className="h-3 w-3" />
            </span>
            <span className="hidden md:inline">Gemini AI</span>
            <span className="inline-flex h-1.5 w-1.5 rounded-full bg-[#1ba1e3] animate-ping" />
          </button>

          {/* System Test/Network Status Indicator */}
          <div className="hidden xl:flex items-center gap-1.5 rounded-full bg-[#e6f4ea] px-3 py-1 text-[11px] font-semibold text-[#137333] border border-[#ceead6]">
            <span className="h-2 w-2 rounded-full bg-[#34a853] animate-pulse" />
            <span>BRICS Pilot Live • 82/82 Tests</span>
          </div>

          {/* Google 9-dot Waffle Menu */}
          <div className="relative">
            <button
              onClick={() => {
                setWaffleOpen(!waffleOpen);
                setAccountMenuOpen(false);
              }}
              aria-label="Google Apps Launcher"
              className="flex h-10 w-10 items-center justify-center rounded-full text-[#5f6368] hover:bg-[#f0f4f9] transition"
            >
              <GoogleWaffleIcon className="h-5 w-5" />
            </button>
            <GoogleWaffleMenu
              isOpen={waffleOpen}
              onClose={() => setWaffleOpen(false)}
            />
          </div>

          {/* User Account Avatar & Role Switcher */}
          <div className="relative">
            <button
              onClick={() => {
                setAccountMenuOpen(!accountMenuOpen);
                setWaffleOpen(false);
              }}
              aria-label="User Account & Role Menu"
              className="flex items-center gap-2 rounded-full p-1 hover:bg-[#f0f4f9] transition"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-[#1a73e8] via-[#8e24aa] to-[#ea4335] text-white font-bold text-sm shadow-sm ring-2 ring-white">
                {activeRole.charAt(0).toUpperCase()}
              </div>
              <span className="hidden lg:inline text-xs font-semibold text-[#444746] capitalize">
                {activeRole.replace("_", " ")}
              </span>
            </button>
            <GoogleRoleAccountMenu
              isOpen={accountMenuOpen}
              onClose={() => setAccountMenuOpen(false)}
              activeRole={activeRole}
              onSelectRole={handleRoleChange}
            />
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------- Main Workspace with Navigation Drawer */}
      <div className="flex flex-1 overflow-hidden">
        {/* Google Navigation Drawer (Desktop) */}
        {sidebarOpen && (
          <aside className="hidden md:flex w-64 shrink-0 flex-col border-r border-[#e0e3e7] bg-white transition-all duration-200">
            {/* Extended Floating Action Button (FAB) */}
            <div className="p-4">
              <Link
                href="/citizen"
                className="group flex w-full items-center gap-3 rounded-2xl bg-[#ffffff] p-3 text-sm font-semibold text-[#1f1f1f] shadow-google-fab border border-[#dadce0] hover:bg-[#f0f4f9] hover:shadow-google-md transition-all"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white shadow-sm">
                  <Google4ColorPlus className="h-5 w-5 group-hover:rotate-90 transition-transform duration-300" />
                </div>
                <span>+ New Citizen Request</span>
              </Link>
            </div>

            {/* Navigation Items */}
            <nav
              aria-label="Main Navigation"
              className="flex-1 space-y-6 overflow-y-auto px-3 py-2"
            >
              {NAV_GROUPS.map((group) => (
                <div key={group.label} className="space-y-1">
                  <p className="px-3 pb-1 text-[11px] font-bold uppercase tracking-wider text-[#747775]">
                    {group.label}
                  </p>
                  {group.links.map((link) => {
                    const active =
                      pathname === link.href ||
                      (link.href !== "/" && pathname.startsWith(link.href + "/"));
                    return (
                      <Link
                        key={link.href}
                        href={link.href}
                        className={`flex items-center justify-between rounded-full px-4 py-2.5 text-sm font-medium transition-all ${
                          active
                            ? "bg-[#c2e7ff] text-[#001d35] font-semibold shadow-sm"
                            : "text-[#444746] hover:bg-[#f0f4f9] hover:text-[#1f1f1f]"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-base">{link.icon}</span>
                          <span>{link.label}</span>
                        </div>
                        {link.badge && (
                          <span
                            className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${
                              active
                                ? "bg-[#001d35] text-white"
                                : "bg-[#f1f3f4] text-[#5f6368]"
                            }`}
                          >
                            {link.badge}
                          </span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              ))}
            </nav>

            {/* BRICS Pilot Footer Card */}
            <div className="border-t border-[#edf2fa] bg-[#f8fafd] p-4 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#747775]">
                  BRICS Pilot Coverage
                </span>
                <span className="h-2 w-2 rounded-full bg-[#34a853]" />
              </div>
              <div className="mt-2 grid grid-cols-3 gap-1 text-center font-medium text-[#444746] text-[11px]">
                <div className="rounded-lg bg-white p-1.5 border border-[#dadce0]">
                  <span>🇮🇳 IND</span>
                  <span className="block text-[9px] text-[#747775]">MH Hub</span>
                </div>
                <div className="rounded-lg bg-white p-1.5 border border-[#dadce0]">
                  <span>🇧🇷 BRA</span>
                  <span className="block text-[9px] text-[#747775]">Rio/SP</span>
                </div>
                <div className="rounded-lg bg-white p-1.5 border border-[#dadce0]">
                  <span>🇿🇦 ZAF</span>
                  <span className="block text-[9px] text-[#747775]">Gauteng</span>
                </div>
              </div>
            </div>
          </aside>
        )}

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 flex md:hidden bg-black/40 backdrop-blur-sm">
            <aside className="w-72 bg-white p-4 shadow-2xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-4 border-b border-[#e0e3e7]">
                  <div className="flex items-center gap-2">
                    <GoogleLogoMark className="h-6 w-6" />
                    <span className="font-google font-bold text-base">CivicPulse</span>
                  </div>
                  <button
                    onClick={() => setMobileMenuOpen(false)}
                    className="p-1 rounded-full text-[#5f6368]"
                  >
                    ✕
                  </button>
                </div>

                <div className="mt-4 space-y-4">
                  {NAV_GROUPS.map((group) => (
                    <div key={group.label} className="space-y-1">
                      <p className="px-2 text-[10px] font-bold uppercase text-[#747775]">
                        {group.label}
                      </p>
                      {group.links.map((link) => (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMobileMenuOpen(false)}
                          className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-[#444746] hover:bg-[#f0f4f9]"
                        >
                          <span>{link.icon}</span>
                          <span>{link.label}</span>
                        </Link>
                      ))}
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-[#edf2fa] text-xs text-[#747775]">
                Google Developer Groups • Track 1
              </div>
            </aside>
            <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
          </div>
        )}

        {/* Main Content Viewport */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-7xl">{children}</div>
        </main>
      </div>

      {/* ------------------------------------------------------------- Mounted Modals & Drawers */}
      <GoogleSearchModal
        isOpen={searchOpen}
        onClose={() => setSearchOpen(false)}
      />

      <GeminiCopilot
        isOpen={geminiOpen}
        onClose={() => setGeminiOpen(false)}
      />
    </div>
  );
}

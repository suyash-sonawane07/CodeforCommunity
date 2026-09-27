"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_GROUPS: { label: string; links: { href: string; label: string }[] }[] = [
  {
    label: "Citizen",
    links: [{ href: "/citizen", label: "Submit a request" }],
  },
  {
    label: "Planning",
    links: [
      { href: "/admin/dashboard", label: "Command Dashboard" },
      { href: "/map", label: "Demand Map" },
      { href: "/clusters/equity", label: "Equity Comparison" },
      { href: "/simulator", label: "Policy Simulator" },
      { href: "/outcome", label: "Outcome Measurement" },
    ],
  },
  {
    label: "Review",
    links: [
      { href: "/review", label: "Review Queue" },
      { href: "/datasets", label: "Datasets & Settings" },
    ],
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-60 shrink-0 border-r border-gray-200 bg-gray-50 md:block">
        <div className="p-4">
          <Link href="/" className="text-lg font-bold text-civic-700">
            CivicPulse
          </Link>
          <p className="text-xs text-gray-400">scaffold</p>
        </div>
        <nav aria-label="Main navigation" className="px-2 pb-6">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="mb-4">
              <p className="px-2 pb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">
                {group.label}
              </p>
              {group.links.map((link) => {
                const active = pathname === link.href || pathname.startsWith(link.href + "/");
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`block rounded-md px-2 py-1.5 text-sm ${
                      active
                        ? "bg-civic-50 font-medium text-civic-700"
                        : "text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}

function SiteHeader() {
  return (
    <header className="border-b border-gray-200 bg-white px-6 py-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">
          AI Development-Needs Intelligence Layer — <span className="font-mono">SCAFFOLD</span>
        </p>
        <Link href="/admin" className="text-sm text-civic-600 hover:underline">
          Admin login
        </Link>
      </div>
    </header>
  );
}

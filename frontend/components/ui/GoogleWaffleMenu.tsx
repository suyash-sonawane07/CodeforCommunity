"use client";

import React, { useRef, useEffect } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/config";

const GOOGLE_APPS = [
  {
    name: "Citizen Intake",
    desc: "Voice & text submissions",
    icon: "📢",
    href: "/citizen",
    color: "#4285F4",
  },
  {
    name: "Demand Map",
    desc: "Google Maps GIS overlay",
    icon: "🗺️",
    href: "/map",
    color: "#34A853",
  },
  {
    name: "Command Center",
    desc: "DPI priority rankings",
    icon: "📊",
    href: "/admin/dashboard",
    color: "#EA4335",
  },
  {
    name: "Policy Simulator",
    desc: "What-If budget planning",
    icon: "🧮",
    href: "/simulator",
    color: "#FBBC05",
  },
  {
    name: "Review Gate",
    desc: "Human-in-the-loop signoff",
    icon: "⚖️",
    href: "/review",
    color: "#4285F4",
  },
  {
    name: "BRICS Datasets",
    desc: "Open catalogs & audit logs",
    icon: "🏛️",
    href: "/datasets",
    color: "#34A853",
  },
  {
    name: "Outcome Tracking",
    desc: "Post-investment monitoring",
    icon: "📈",
    href: "/outcome",
    color: "#EA4335",
  },
  {
    name: "FastAPI Swagger",
    desc: "Backend API Contracts",
    icon: "⚡",
    href: `${API_BASE_URL}/docs`,
    external: true,
    color: "#FBBC05",
  },
];

export function GoogleWaffleMenu({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={menuRef}
      className="absolute right-0 top-12 z-50 w-80 rounded-3xl border border-[#dadce0] bg-white p-4 shadow-xl ring-1 ring-black/5 animate-in fade-in zoom-in-95 duration-150"
    >
      <div className="mb-3 px-2 flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-[#5f6368]">
          CivicPulse Ecosystem
        </span>
        <span className="rounded-full bg-[#e8f0fe] px-2 py-0.5 text-[10px] font-semibold text-[#1a73e8]">
          Google DPI
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {GOOGLE_APPS.map((app) => (
          <Link
            key={app.name}
            href={app.href}
            onClick={onClose}
            target={app.external ? "_blank" : undefined}
            rel={app.external ? "noreferrer" : undefined}
            className="group flex flex-col items-center justify-center rounded-2xl p-2.5 text-center hover:bg-[#f0f4f9] transition"
          >
            <div
              className="flex h-11 w-11 items-center justify-center rounded-2xl text-2xl shadow-sm transition group-hover:scale-110"
              style={{ backgroundColor: `${app.color}15` }}
            >
              <span>{app.icon}</span>
            </div>
            <span className="mt-2 block text-xs font-medium text-[#1f1f1f] group-hover:text-[#0b57d0] line-clamp-1">
              {app.name}
            </span>
          </Link>
        ))}
      </div>

      <div className="mt-3 border-t border-[#edf2fa] pt-3 text-center">
        <span className="text-[11px] text-[#747775]">
          Google Developer Groups • Track 1 BRICS Pilot
        </span>
      </div>
    </div>
  );
}

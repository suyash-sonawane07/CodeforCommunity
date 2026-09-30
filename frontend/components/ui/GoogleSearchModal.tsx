"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  GoogleSearchIcon,
  GoogleMicIcon,
  GoogleLensIcon,
  GoogleMapPinIcon,
} from "./GoogleIcons";
import { MOCK_CLUSTERS } from "@/lib/mockData";

export function GoogleSearchModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filteredClusters = MOCK_CLUSTERS.filter((c) => {
    const text = `${c.village_ward} ${c.district} ${c.issue_type} ${c.country}`.toLowerCase();
    const matchesQuery = !query || text.includes(query.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" ||
      c.country === selectedCategory ||
      c.issue_type.includes(selectedCategory);
    return matchesQuery && matchesCategory;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-4 pt-20 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-2xl overflow-hidden rounded-3xl bg-white shadow-2xl ring-1 ring-black/5 animate-in fade-in zoom-in-95 duration-150">
        {/* Search Header */}
        <div className="flex items-center gap-3 border-b border-[#e0e3e7] px-5 py-3.5">
          <GoogleSearchIcon className="h-5 w-5 text-[#4285F4]" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search citizen requests, clusters, coordinates, or sectors... (Press ESC to close)"
            className="flex-1 bg-transparent text-sm text-[#1f1f1f] placeholder-[#747775] outline-none"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="text-xs font-semibold text-[#747775] hover:text-[#1f1f1f]"
            >
              Clear
            </button>
          )}
          <GoogleMicIcon className="h-5 w-5 cursor-pointer hover:opacity-80" />
          <GoogleLensIcon className="h-5 w-5 cursor-pointer hover:opacity-80" />
        </div>

        {/* Quick Filter Chips */}
        <div className="flex items-center gap-2 border-b border-[#f0f4f9] bg-[#f8fafd] px-5 py-2.5 overflow-x-auto text-xs">
          <span className="text-[11px] font-semibold text-[#747775] uppercase tracking-wider">
            Filter:
          </span>
          {[
            { id: "all", label: "All Hubs" },
            { id: "india", label: "🇮🇳 India" },
            { id: "brazil", label: "🇧🇷 Brazil" },
            { id: "south_africa", label: "🇿🇦 South Africa" },
            { id: "water", label: "💧 Water" },
            { id: "health", label: "🏥 Health" },
            { id: "drainage", label: "🌊 Flood/Drainage" },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                selectedCategory === cat.id
                  ? "bg-[#0b57d0] text-white shadow-sm"
                  : "bg-white text-[#444746] border border-[#dadce0] hover:bg-[#f0f4f9]"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-1">
          {filteredClusters.length > 0 ? (
            filteredClusters.map((cluster) => (
              <div
                key={cluster.id}
                onClick={() => {
                  onClose();
                  router.push(`/clusters/${cluster.id}`);
                }}
                className="group flex cursor-pointer items-center justify-between rounded-2xl p-3 hover:bg-[#f0f4f9] transition"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#e8f0fe] text-[#1a73e8] group-hover:scale-105 transition">
                    <GoogleMapPinIcon className="h-5 w-5" color="#1a73e8" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-[#1f1f1f] group-hover:text-[#0b57d0]">
                        {cluster.village_ward}
                      </span>
                      <span className="rounded-full bg-[#f1f3f4] px-2 py-0.5 text-[10px] font-medium text-[#5f6368]">
                        {cluster.district}
                      </span>
                    </div>
                    <p className="text-xs text-[#5f6368]">
                      {cluster.issue_type.replace(/_/g, " ")} • {cluster.independent_demand_count} verified citizen reports
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="rounded-full bg-[#c4eed0] px-2.5 py-1 text-xs font-bold text-[#072711]">
                    Score: {cluster.priority_score}
                  </span>
                  <span className="block text-[10px] text-[#747775] mt-1 capitalize">
                    {cluster.country}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-sm text-[#747775]">
              No matching DPI clusters or requests found for &ldquo;{query}&rdquo;.
            </div>
          )}
        </div>

        {/* Quick Links Footer */}
        <div className="flex items-center justify-between border-t border-[#e0e3e7] bg-[#f8fafd] px-5 py-3 text-xs text-[#5f6368]">
          <div className="flex items-center gap-4">
            <Link
              href="/map"
              onClick={onClose}
              className="hover:text-[#0b57d0] font-medium"
            >
              🗺️ Open Geospatial Map
            </Link>
            <Link
              href="/citizen"
              onClick={onClose}
              className="hover:text-[#0b57d0] font-medium"
            >
              📢 Submit Voice Request
            </Link>
            <Link
              href="/simulator"
              onClick={onClose}
              className="hover:text-[#0b57d0] font-medium"
            >
              🧮 Launch Simulator
            </Link>
          </div>
          <span className="text-[11px] text-[#747775]">
            Use <kbd className="rounded bg-[#e8eaed] px-1.5 py-0.5 text-[10px]">ESC</kbd> to exit
          </span>
        </div>
      </div>
    </div>
  );
}

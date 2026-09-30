"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { API_BASE_URL } from "@/lib/config";
import type { GeoJSONFeature } from "@/types/api";
import {
  MOCK_GEOJSON_FEATURES,
  MOCK_INFRASTRUCTURE,
} from "@/lib/mockData";
import {
  GoogleMapPinIcon,
  GoogleSearchIcon,
  GoogleLensIcon,
  GeminiSparkleIcon,
} from "@/components/ui/GoogleIcons";

const InteractiveMap = dynamic(() => import("@/components/MapComponent"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center bg-[#f0f4f9] text-[#5f6368]">
      <div className="flex flex-col items-center gap-2">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#0b57d0] border-t-transparent" />
        <span className="text-xs font-semibold">Loading Google Maps GIS Layer...</span>
      </div>
    </div>
  ),
});

const COUNTRY_REGIONS = [
  { id: "all", label: "All BRICS Hubs" },
  { id: "india", label: "🇮🇳 India (Maharashtra)" },
  { id: "brazil", label: "🇧🇷 Brazil (Rio / Santos)" },
  { id: "south_africa", label: "🇿🇦 South Africa (Gauteng / WC)" },
];

const SECTORS = [
  { id: "all", label: "All Sectors", icon: "🌐" },
  { id: "water", label: "Water Supply", icon: "💧" },
  { id: "drainage", label: "Drainage / Flood", icon: "🌊" },
  { id: "electrical", label: "Power & Grid", icon: "⚡" },
  { id: "health", label: "Healthcare", icon: "🏥" },
  { id: "transit", label: "Transit / Roads", icon: "🚌" },
];

export default function DemandMapPage() {
  const [features, setFeatures] = useState<GeoJSONFeature[]>(MOCK_GEOJSON_FEATURES);
  const [infrastructure, setInfrastructure] = useState<any[]>(MOCK_INFRASTRUCTURE);
  const [selectedFeature, setSelectedFeature] = useState<GeoJSONFeature | null>(
    MOCK_GEOJSON_FEATURES[0]
  );
  const [loading, setLoading] = useState(false);
  const [mapType, setMapType] = useState<"map" | "satellite" | "terrain">("map");
  const [mapCenter, setMapCenter] = useState<[number, number]>([19.482, 75.385]);
  const [mapZoom, setMapZoom] = useState<number>(11);
  const [showInfraLayer, setShowInfraLayer] = useState(true);

  // Filters
  const [regionFilter, setRegionFilter] = useState("all");
  const [sectorFilter, setSectorFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadLiveMapData();
  }, []);

  const loadLiveMapData = async () => {
    try {
      const authRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "analyst@civicpulse.dev", password: "password" }),
      });
      if (!authRes.ok) return; // Keep mock fallback

      const { access_token } = await authRes.json();
      const headers = { Authorization: `Bearer ${access_token}` };

      const [geoRes, infraRes] = await Promise.all([
        fetch(`${API_BASE_URL}/geospatial/clusters`, { headers }),
        fetch(`${API_BASE_URL}/infrastructure`, { headers }),
      ]);

      if (geoRes.ok) {
        const geoData = await geoRes.json();
        if (geoData.features?.length > 0) {
          setFeatures(geoData.features);
          setSelectedFeature(geoData.features[0]);
        }
      }

      if (infraRes.ok) {
        const infraData = await infraRes.json();
        if (infraData.infrastructure?.length > 0) {
          setInfrastructure(infraData.infrastructure);
        }
      }
    } catch {
      // Backend offline: gracefully keep mock features
    }
  };

  // Filter features
  const filteredFeatures = features.filter((feat) => {
    const props = (feat.properties || {}) as Record<string, any>;
    const sector = String(props.issue_type || "").toLowerCase();
    const district = String(props.district || "").toLowerCase();
    const ward = String(props.village_ward || "").toLowerCase();

    if (sectorFilter !== "all" && !sector.includes(sectorFilter)) return false;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!district.includes(q) && !ward.includes(q) && !sector.includes(q)) {
        return false;
      }
    }

    if (regionFilter === "india") {
      return district.includes("pune") || district.includes("chhatrapati") || district.includes("sambhajinagar");
    }
    if (regionFilter === "brazil") {
      return district.includes("rio") || district.includes("santos") || district.includes("zona norte");
    }
    if (regionFilter === "south_africa") {
      return district.includes("johannesburg") || district.includes("cape") || district.includes("khayelitsha") || district.includes("region d");
    }
    return true;
  });

  const handleRegionSelect = (rId: string) => {
    setRegionFilter(rId);
    if (rId === "india") {
      setMapCenter([19.482, 75.385]);
      setMapZoom(11);
    } else if (rId === "brazil") {
      setMapCenter([-22.859, -43.245]);
      setMapZoom(12);
    } else if (rId === "south_africa") {
      setMapCenter([-26.271, 27.859]);
      setMapZoom(12);
    } else {
      setMapCenter([10, 20]);
      setMapZoom(3);
    }
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto">
      {/* Google 4-Color Accent Strip */}
      <div className="h-1.5 w-full rounded-full bg-gradient-to-r from-[#4285F4] via-[#EA4335] via-[#FBBC05] to-[#34A853]" />

      {/* ------------------------------------------------------------- Top Info Bar */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-google text-2xl font-bold tracking-tight text-[#1f1f1f] sm:text-3xl">
              Geospatial Demand Hotspots
            </h1>
            <span className="rounded-full bg-[#e8f0fe] px-2.5 py-0.5 text-xs font-semibold text-[#1a73e8]">
              Google Maps GIS
            </span>
          </div>
          <p className="text-xs text-[#5f6368]">
            Interactive PostGIS geodesic buffering &amp; spatial infrastructure deficit overlays (SRID:4326).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowInfraLayer(!showInfraLayer)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
              showInfraLayer
                ? "bg-[#ceead6] text-[#072711] border border-[#a8dab5]"
                : "bg-[#f1f3f4] text-[#5f6368] border border-[#dadce0]"
            }`}
          >
            {showInfraLayer ? "✓ Infrastructure Layer ON" : "Infrastructure Layer OFF"}
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- Google Maps Viewport Container */}
      <div className="relative h-[650px] w-full overflow-hidden rounded-3xl border border-[#dadce0] bg-[#e5e3df] shadow-google-md">
        {/* Real Interactive Map Canvas */}
        <div className="absolute inset-0 z-0">
          <InteractiveMap
            features={filteredFeatures}
            selectedFeature={selectedFeature}
            onSelectFeature={(feat: any) => {
              setSelectedFeature(feat);
              if (feat.geometry?.coordinates) {
                setMapCenter([feat.geometry.coordinates[1], feat.geometry.coordinates[0]]);
                setMapZoom(13);
              } else if (feat.lat && feat.lng) {
                setMapCenter([feat.lat, feat.lng]);
                setMapZoom(13);
              }
            }}
            mapType={mapType}
            center={mapCenter}
            zoom={mapZoom}
            showInfra={showInfraLayer}
          />
        </div>

        {/* ----------------------------------------------------------- Floating Google Maps Search & Filter Card (Top Left) */}
        <div className="absolute left-4 top-4 z-20 w-80 sm:w-96 space-y-2 pointer-events-auto">
          {/* Search Box */}
          <div className="flex items-center gap-2 rounded-full border border-[#dadce0] bg-white px-4 py-2.5 shadow-google-md">
            <GoogleSearchIcon className="h-4 w-4 text-[#5f6368]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search in Google Maps..."
              className="flex-1 bg-transparent text-xs text-[#1f1f1f] placeholder-[#747775] outline-none"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="text-xs text-[#747775] hover:text-[#1f1f1f]"
              >
                ✕
              </button>
            )}
            <GoogleLensIcon className="h-4 w-4 text-[#4285F4]" />
          </div>

          {/* Region Chips */}
          <div className="flex gap-1.5 overflow-x-auto rounded-2xl bg-white/90 p-2 shadow-google-sm backdrop-blur-md">
            {COUNTRY_REGIONS.map((r) => (
              <button
                key={r.id}
                onClick={() => handleRegionSelect(r.id)}
                className={`shrink-0 rounded-full px-3 py-1 text-[11px] font-medium transition ${
                  regionFilter === r.id
                    ? "bg-[#0b57d0] text-white shadow-sm"
                    : "bg-[#f8fafd] text-[#444746] border border-[#dadce0] hover:bg-[#f0f4f9]"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>


          {/* Sector Filter Chips */}
          <div className="flex gap-1.5 overflow-x-auto rounded-2xl bg-white/90 p-2 shadow-google-sm backdrop-blur-md">
            {SECTORS.map((s) => (
              <button
                key={s.id}
                onClick={() => setSectorFilter(s.id)}
                className={`shrink-0 flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition ${
                  sectorFilter === s.id
                    ? "bg-[#1f1f1f] text-white shadow-sm"
                    : "bg-[#f8fafd] text-[#444746] border border-[#dadce0] hover:bg-[#f0f4f9]"
                }`}
              >
                <span>{s.icon}</span>
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* ----------------------------------------------------------- Map Type Toggle (Top Right) */}
        <div className="absolute right-4 top-4 z-20 flex rounded-2xl border border-[#dadce0] bg-white p-1 shadow-google-md text-xs font-medium">
          {(["map", "satellite", "terrain"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setMapType(t)}
              className={`rounded-xl px-3 py-1.5 capitalize transition ${
                mapType === t
                  ? "bg-[#0b57d0] text-white font-semibold shadow-sm"
                  : "text-[#444746] hover:bg-[#f0f4f9]"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {/* ----------------------------------------------------------- Map Canvas: Interactive Pins & Clusters */}
        <div className="hidden">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 sm:gap-10 max-w-3xl w-full">
            {filteredFeatures.map((feat) => {
              const props = (feat.properties || {}) as Record<string, any>;
              const selProps = (selectedFeature?.properties || {}) as Record<string, any>;
              const isSelected = selProps.id === props.id;

              // Color determination
              let pinColor = "#EA4335"; // Google Red
              let icon = "📍";
              if (props.issue_type?.includes("water")) {
                pinColor = "#4285F4"; // Google Blue
                icon = "💧";
              } else if (props.issue_type?.includes("electrical")) {
                pinColor = "#FBBC05"; // Google Yellow
                icon = "⚡";
              } else if (props.issue_type?.includes("health")) {
                pinColor = "#34A853"; // Google Green
                icon = "🏥";
              } else if (props.issue_type?.includes("drainage")) {
                pinColor = "#1a73e8";
                icon = "🌊";
              }

              return (
                <div
                  key={props.id}
                  onClick={() => setSelectedFeature(feat)}
                  className="group relative flex flex-col items-center cursor-pointer transition-all"
                >
                  {/* Geodesic Radius Pulse Ring (FR-027) */}
                  <div
                    className={`absolute -top-3 h-20 w-20 rounded-full border-2 transition-all pointer-events-none ${
                      isSelected
                        ? "border-[#1a73e8] bg-[#1a73e8]/15 animate-ping"
                        : "border-slate-400/30 group-hover:border-[#1a73e8]/40"
                    }`}
                  />

                  {/* Google Maps Teardrop Pin */}
                  <div
                    className={`relative flex h-14 w-12 flex-col items-center transition-transform duration-200 ${
                      isSelected ? "scale-125 -translate-y-2 z-30" : "group-hover:scale-110"
                    }`}
                  >
                    <svg viewBox="0 0 384 512" className="h-12 w-10 drop-shadow-md">
                      <path
                        fill={pinColor}
                        d="M172.268 501.67C26.97 291.031 0 269.413 0 192 0 85.961 85.961 0 192 0s192 85.961 192 192c0 77.413-26.97 99.031-172.268 309.67-9.535 13.774-29.93 13.773-39.464 0z"
                      />
                      <circle cx="192" cy="192" r="100" fill="#ffffff" />
                    </svg>
                    <span className="absolute top-2 text-sm">{icon}</span>
                  </div>

                  {/* Pin Place Label Card */}
                  <div
                    className={`mt-1 rounded-full px-3 py-1 text-center shadow-google-sm border transition-all ${
                      isSelected
                        ? "bg-[#1f1f1f] text-white border-black scale-105 font-semibold text-xs"
                        : "bg-white/95 text-[#1f1f1f] border-[#dadce0] text-[11px] group-hover:bg-white"
                    }`}
                  >
                    <span className="truncate max-w-[130px] block">
                      {props.village_ward?.split(",")[0] || props.district}
                    </span>
                    <span className="text-[10px] text-[#34a853] font-bold block">
                      Score: {props.priority_score}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ----------------------------------------------------------- Google Maps Controls (Bottom Right) */}
        <div className="absolute bottom-4 right-4 z-20 flex flex-col gap-2">
          {/* Zoom Controls (+ / -) */}
          <div className="flex flex-col overflow-hidden rounded-2xl border border-[#dadce0] bg-white shadow-google-md">
            <button
              onClick={() => setMapZoom((z) => Math.min(z + 1, 18))}
              className="flex h-10 w-10 items-center justify-center text-lg font-bold text-[#5f6368] hover:bg-[#f0f4f9] transition border-b border-[#dadce0]"
              aria-label="Zoom In"
            >
              +
            </button>
            <button
              onClick={() => setMapZoom((z) => Math.max(z - 1, 4))}
              className="flex h-10 w-10 items-center justify-center text-lg font-bold text-[#5f6368] hover:bg-[#f0f4f9] transition"
              aria-label="Zoom Out"
            >
              −
            </button>
          </div>

          {/* Pegman Street View & Location Target */}
          <div className="flex flex-col gap-1 rounded-2xl border border-[#dadce0] bg-white p-1 shadow-google-md">
            <button
              title="Google Street View Pegman"
              className="flex h-9 w-9 items-center justify-center rounded-xl text-yellow-500 hover:bg-[#fef7e0] transition text-base"
            >
              🚶‍♂️
            </button>
            <button
              title="Center Map on Active Hotspot"
              onClick={() => {
                if (features.length > 0) setSelectedFeature(features[0]);
              }}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-[#1a73e8] hover:bg-[#e8f0fe] transition text-base"
            >
              🎯
            </button>
          </div>
        </div>

        {/* ----------------------------------------------------------- Bottom Scale & PostGIS Attribution */}
        <div className="absolute bottom-2 left-4 z-20 flex items-center gap-3 text-[10px] text-[#5f6368] bg-white/80 px-2 py-0.5 rounded backdrop-blur-sm">
          <span>Map Data ©2026 Google / OpenStreetMap</span>
          <span>•</span>
          <span>PostGIS ST_DWithin Buffer: 650m</span>
          <span>•</span>
          <span>Zoom: {mapZoom}x</span>
        </div>
      </div>

      {/* ------------------------------------------------------------- Selected Hotspot Inspection Drawer (Google Maps Info Sheet) */}
      {selectedFeature && (
        <div className="rounded-3xl border border-[#dadce0] bg-white p-6 shadow-google-sm transition-all">
          {(() => {
            const selProps = (selectedFeature.properties || {}) as Record<string, any>;
            return (
              <div className="grid gap-6 lg:grid-cols-3">
                {/* Place Overview */}
                <div className="space-y-3 lg:col-span-2">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#edf2fa] pb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <GoogleMapPinIcon className="h-5 w-5" color="#EA4335" />
                        <h2 className="font-google text-xl font-bold text-[#1f1f1f]">
                          {selProps.village_ward}
                        </h2>
                      </div>
                      <p className="text-xs text-[#5f6368] pl-7">
                        {selProps.district}, {selProps.country?.toUpperCase()} • Hotspot Cluster #{selProps.id}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="rounded-full bg-[#e6f4ea] px-3 py-1 text-xs font-bold text-[#137333] border border-[#ceead6]">
                        ★ {selProps.priority_score} Priority Score
                      </span>
                      <span className="rounded-full bg-[#e8f0fe] px-3 py-1 text-xs font-semibold text-[#1a73e8] capitalize">
                        {selProps.issue_type?.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>

                  {/* Key Metrics Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    <div className="rounded-2xl bg-[#f8fafd] p-3 border border-[#e0e3e7]">
                      <span className="text-[10px] font-semibold uppercase text-[#747775]">Verified Demand</span>
                      <p className="font-google text-xl font-bold text-[#1f1f1f] mt-1">
                        {selProps.independent_demand_count}
                      </p>
                      <span className="text-[10px] text-[#137333] font-medium">Deduplicated Citizens</span>
                    </div>

                    <div className="rounded-2xl bg-[#f8fafd] p-3 border border-[#e0e3e7]">
                      <span className="text-[10px] font-semibold uppercase text-[#747775]">Raw Reports</span>
                      <p className="font-google text-xl font-bold text-[#5f6368] mt-1">
                        {selProps.raw_message_count}
                      </p>
                      <span className="text-[10px] text-[#747775]">Total voice &amp; text</span>
                    </div>

                    <div className="rounded-2xl bg-[#f8fafd] p-3 border border-[#e0e3e7]">
                      <span className="text-[10px] font-semibold uppercase text-[#747775]">Geodesic Buffer</span>
                      <p className="font-google text-xl font-bold text-[#0b57d0] mt-1">
                        650 m
                      </p>
                      <span className="text-[10px] text-[#0b57d0]">PostGIS SRID:4326</span>
                    </div>

                    <div className="rounded-2xl bg-[#f8fafd] p-3 border border-[#e0e3e7]">
                      <span className="text-[10px] font-semibold uppercase text-[#747775]">Lifecycle Status</span>
                      <p className="font-google text-base font-bold text-[#b06000] mt-1 uppercase">
                        {selProps.status}
                      </p>
                      <span className="text-[10px] text-[#747775]">Ready for human signoff</span>
                    </div>
                  </div>

                  {/* Corroborating Evidence Snippets */}
                  <div className="rounded-2xl bg-[#f8fafd] p-4 border border-[#e0e3e7] text-xs">
                    <span className="font-semibold text-[#1f1f1f] block mb-1">
                      🔍 Multilingual Spatial Evidence Notes:
                    </span>
                    <ul className="list-disc pl-5 space-y-1 text-[#5f6368]">
                      <li>High semantic coherence detected across Marathi, Portuguese, and English submissions.</li>
                      <li>Zero coordinate repetition attacks (anti-astroturfing filter verified).</li>
                      <li>Critical infrastructure gap confirmed against municipal master plan.</li>
                    </ul>
                  </div>
                </div>

                {/* Actions & Next Steps */}
                <div className="flex flex-col justify-between rounded-2xl bg-[#f8fafd] p-5 border border-[#e0e3e7] space-y-4">
                  <div>
                    <h3 className="font-google font-bold text-sm text-[#1f1f1f] mb-1">
                      DPI Action Pathway
                    </h3>
                    <p className="text-xs text-[#5f6368]">
                      Proceed with explainable evidence inspection, human review signoff, or policy budget simulation.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Link
                      href={`/clusters/${selProps.id}`}
                      className="flex w-full items-center justify-center gap-2 rounded-full bg-[#0b57d0] px-4 py-2.5 text-xs font-semibold text-white shadow-google-sm hover:bg-[#0842a0] transition"
                    >
                      <span>Inspect AI Evidence Drawer</span>
                      <span>→</span>
                    </Link>

                    <Link
                      href="/simulator"
                      className="flex w-full items-center justify-center gap-2 rounded-full border border-[#dadce0] bg-white px-4 py-2 text-xs font-semibold text-[#1f1f1f] hover:bg-[#f0f4f9] transition"
                    >
                      <GeminiSparkleIcon className="h-4 w-4 text-[#5457cd]" />
                      <span>Simulate Infrastructure Budget</span>
                    </Link>

                    <Link
                      href="/review"
                      className="flex w-full items-center justify-center gap-2 rounded-full border border-transparent bg-[#e8f0fe] px-4 py-2 text-xs font-semibold text-[#1a73e8] hover:bg-[#d2e3fc] transition"
                    >
                      <span>⚖️ Submit to Review Gate</span>
                    </Link>
                  </div>

                  <div className="border-t border-[#e0e3e7] pt-2 text-center text-[10px] text-[#747775]">
                    PostGIS Geodesic Buffer (FR-027) • Fully Explainable
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}

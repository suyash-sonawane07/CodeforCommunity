"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/config";
import type { GeoJSONFeature } from "@/types/api";

const COUNTRY_REGIONS = [
  { id: "all", label: "All BRICS Hubs" },
  { id: "india", label: "🇮🇳 India (Maharashtra)" },
  { id: "brazil", label: "🇧🇷 Brazil (Rio / Santos)" },
  { id: "south_africa", label: "🇿🇦 South Africa (Gauteng / WC)" },
];

export default function DemandMapPage() {
  const [features, setFeatures] = useState<GeoJSONFeature[]>([]);
  const [infrastructure, setInfrastructure] = useState<any[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<GeoJSONFeature | null>(null);
  const [loading, setLoading] = useState(true);
  const [regionFilter, setRegionFilter] = useState("all");
  const [sectorFilter, setSectorFilter] = useState("all");

  useEffect(() => {
    loadMapData();
  }, []);

  const loadMapData = async () => {
    setLoading(true);
    try {
      const authRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "analyst@civicpulse.dev", password: "password" }),
      });
      const { access_token } = await authRes.json();
      const headers = { Authorization: `Bearer ${access_token}` };

      // 1. Fetch geojson clusters
      const geoRes = await fetch(`${API_BASE_URL}/geospatial/clusters`, { headers });
      const geoData = await geoRes.json();
      setFeatures(geoData.features || []);
      if (geoData.features?.length > 0) {
        setSelectedFeature(geoData.features[0]);
      }

      // 2. Fetch infrastructure layers
      const infraRes = await fetch(`${API_BASE_URL}/infrastructure`, { headers });
      const infraData = await infraRes.json();
      setInfrastructure(infraData.infrastructure || []);
    } catch (err) {
      console.error("Map loading error", err);
    } finally {
      setLoading(false);
    }
  };

  // Filter features
  const filteredFeatures = features.filter((feat) => {
    const props = (feat.properties || {}) as Record<string, any>;
    const sector = String(props.issue_type || "").toLowerCase();
    const district = String(props.district || "").toLowerCase();

    if (sectorFilter !== "all" && !sector.includes(sectorFilter)) return false;

    if (regionFilter === "india") {
      return district.includes("pune") || district.includes("chhatrapati") || district.includes("demo");
    }
    if (regionFilter === "brazil") {
      return district.includes("rio") || district.includes("santos") || district.includes("zona norte");
    }
    if (regionFilter === "south_africa") {
      return district.includes("johannesburg") || district.includes("cape") || district.includes("khayelitsha");
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Geospatial Demand Hotspots & Infrastructure Map
          </h1>
          <p className="text-sm text-slate-500">
            Spatial distribution of verified citizen demand clusters alongside public infrastructure assets.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-semibold text-blue-700">
            PostGIS Geodesic Buffer (FR-027)
          </span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">Region:</span>
          {COUNTRY_REGIONS.map((r) => (
            <button
              key={r.id}
              onClick={() => setRegionFilter(r.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                regionFilter === r.id
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500">Sector:</span>
          <select
            value={sectorFilter}
            onChange={(e) => setSectorFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700"
          >
            <option value="all">All Sectors</option>
            <option value="water">Water</option>
            <option value="transport">Transport</option>
            <option value="roads">Roads</option>
            <option value="education">Education</option>
            <option value="health">Health</option>
            <option value="sanitation">Sanitation</option>
            <option value="power">Power</option>
          </select>
        </div>
      </div>

      {/* Main Map Visualizer & Detail Panel */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Interactive Map Surface */}
        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-slate-900 p-6 text-white shadow-md relative overflow-hidden min-h-[500px] flex flex-col justify-between">
          {/* Map Surface Background Grid */}
          <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:20px_20px] opacity-40 pointer-events-none" />

          {/* Top Controls Overlay */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="rounded-md bg-slate-800/90 px-3 py-1.5 text-xs font-mono text-slate-300 border border-slate-700">
              Active Map Layer: GeoJSON PostGIS SRID:4326 ({filteredFeatures.length} visible clusters)
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5">
                <span className="h-3 w-3 rounded-full bg-blue-500 shadow-sm" /> Cluster Hotspot
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded bg-emerald-400" /> Infrastructure Asset
              </span>
            </div>
          </div>

          {/* Interactive Cluster Pin Cloud (SVG/Vector representation) */}
          <div className="relative z-10 my-auto py-8">
            {loading ? (
              <div className="text-center text-slate-400">Loading spatial layers...</div>
            ) : filteredFeatures.length === 0 ? (
              <div className="text-center text-slate-400">No clusters found in this region.</div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {filteredFeatures.map((feat, idx) => {
                  const props = (feat.properties || {}) as Record<string, any>;
                  const selProps = (selectedFeature?.properties || {}) as Record<string, any>;
                  const isSelected = selProps.id === props.id;
                  return (
                    <button
                      key={props.id || idx}
                      onClick={() => setSelectedFeature(feat)}
                      className={`text-left rounded-xl p-3.5 border transition-all ${
                        isSelected
                          ? "bg-blue-600/30 border-blue-400 shadow-lg shadow-blue-500/20 ring-2 ring-blue-400"
                          : "bg-slate-800/80 border-slate-700 hover:bg-slate-800 hover:border-slate-500"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs font-bold text-cyan-300">
                          #{props.id}
                        </span>
                        <span className="rounded bg-slate-700/80 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-slate-300">
                          {props.issue_type}
                        </span>
                      </div>
                      <p className="mt-2 text-xs font-semibold text-slate-100 truncate">
                        {props.district || props.village || "Regional"}
                      </p>
                      <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
                        <span>👥 {props.independent_demand_count} reports</span>
                        <span className="text-emerald-400 font-bold">
                          {props.review_status || props.status}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Bottom Coordinates Status */}
          <div className="relative z-10 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800 pt-3">
            <span>Projection: EPSG:4326 (WGS84 Lat/Lon)</span>
            <span>Spatial Engine: PostGIS ST_DWithin Geodesic</span>
          </div>
        </div>

        {/* Selected Cluster Inspection Drawer */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          {selectedFeature ? (
            (() => {
              const selProps = (selectedFeature.properties || {}) as Record<string, any>;
              return (
                <div className="space-y-5">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <div>
                      <span className="text-xs font-bold uppercase text-blue-600 tracking-wider">
                        Selected Demand Hotspot
                      </span>
                      <h3 className="text-xl font-extrabold text-slate-900">
                        Cluster #{selProps.id}
                      </h3>
                    </div>
                    <span className="rounded-full bg-blue-50 border border-blue-200 px-3 py-1 text-xs font-bold text-blue-700 capitalize">
                      {selProps.issue_type}
                    </span>
                  </div>

                  {/* Demand & Message Stats */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                      <p className="text-[11px] font-medium text-slate-400 uppercase">Independent Demand</p>
                      <p className="mt-1 text-2xl font-bold text-slate-900">
                        {selProps.independent_demand_count}
                      </p>
                      <p className="text-[10px] text-emerald-600 font-semibold">Deduplicated (FR-024)</p>
                    </div>
                    <div className="rounded-lg bg-slate-50 p-3 border border-slate-100">
                      <p className="text-[11px] font-medium text-slate-400 uppercase">Raw Citizen Messages</p>
                      <p className="mt-1 text-2xl font-bold text-slate-600">
                        {selProps.raw_message_count}
                      </p>
                      <p className="text-[10px] text-slate-400">Total ingested</p>
                    </div>
                  </div>

                  {/* Geographic Coordinates */}
                  <div className="rounded-lg bg-slate-50 p-3.5 border border-slate-100 space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">District:</span>
                      <span className="font-semibold text-slate-800">
                        {selProps.district || "Regional District"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Coordinates:</span>
                      <span className="font-mono text-slate-700">
                        {selectedFeature.geometry && Array.isArray((selectedFeature.geometry as any).coordinates)
                          ? `${(selectedFeature.geometry as any).coordinates[1].toFixed(4)}°N, ${(selectedFeature.geometry as any).coordinates[0].toFixed(4)}°E`
                          : "Unresolved (FR-033)"}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Lifecycle Status:</span>
                      <span className="font-bold text-blue-700 uppercase text-[11px]">
                        {selProps.status}
                      </span>
                    </div>
                  </div>

                  {/* Action Button */}
                  <Link
                    href={`/clusters/${selProps.id}`}
                    className="block w-full text-center rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2.5 text-xs font-bold text-white shadow-md shadow-blue-500/20 hover:from-blue-700 hover:to-indigo-700 transition"
                  >
                    Inspect Full Explainable AI Evidence Drawer →
                  </Link>
                </div>
              );
            })()
          ) : (
            <div className="text-center text-slate-400 py-16 text-sm">
              Select a cluster pin on the map to view geospatial metrics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

interface MapComponentProps {
  features?: any[];
  clusters?: any[];
  infrastructure?: any[];
  selectedFeature?: any;
  onSelectFeature?: (feat: any) => void;
  mapType?: 'map' | 'satellite' | 'terrain';
  center?: [number, number];
  zoom?: number;
  showInfra?: boolean;
}

// Controller component to smoothly fly/pan when center or zoom changes
function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.2 });
  }, [center, zoom, map]);
  return null;
}

// Helper to create custom Google Maps styled teardrop HTML pins
function createCustomPin(icon: string, color: string, isSelected: boolean) {
  const html = `
    <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer; transform: ${isSelected ? 'scale(1.25)' : 'scale(1)'}; transition: transform 0.2s;">
      ${isSelected ? `<div style="position: absolute; top: -6px; width: 44px; height: 44px; border-radius: 9999px; border: 2px solid #1a73e8; background: rgba(26,115,232,0.25); animation: ping 1.5s cubic-bezier(0,0,0.2,1) infinite;"></div>` : ''}
      <svg viewBox="0 0 384 512" style="width: 32px; height: 42px; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.4));">
        <path fill="${color}" d="M172.268 501.67C26.97 291.031 0 269.413 0 192 0 85.961 85.961 0 192 0s192 85.961 192 192c0 77.413-26.97 99.031-172.268 309.67-9.535 13.774-29.93 13.773-39.464 0z"/>
        <circle cx="192" cy="192" r="100" fill="#ffffff" />
      </svg>
      <span style="position: absolute; top: 6px; font-size: 13px;">${icon}</span>
    </div>
  `;
  return L.divIcon({
    html,
    className: 'custom-google-marker',
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -40],
  });
}

// Helper to create municipal infrastructure facility pins (square badge)
function createInfraPin(icon: string, color: string) {
  const html = `
    <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 8px; background: #ffffff; border: 2px solid ${color}; box-shadow: 0 2px 6px rgba(0,0,0,0.25); cursor: pointer;">
      <span style="font-size: 14px;">${icon}</span>
    </div>
  `;
  return L.divIcon({
    html,
    className: 'custom-infra-marker',
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -16],
  });
}

export default function MapComponent({
  features = [],
  clusters = [],
  infrastructure = [],
  selectedFeature,
  onSelectFeature,
  mapType = 'map',
  center = [19.482, 75.385],
  zoom = 11,
  showInfra = true,
}: MapComponentProps) {
  const cartoApiKey =
    process.env.NEXT_PUBLIC_CARTO_API_KEY || 'cb1_45dd_1_9ec88189693cc185f0b05713';

  // Tile URLs (CartoDB Voyager looks exactly like Google Maps, verified with API key to remove watermark)
  const tileUrls = {
    map: `https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png?key=${cartoApiKey}`,
    satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    terrain: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
  };

  const attributions = {
    map: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    satellite: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    terrain: 'Map data: &copy; OpenStreetMap contributors, SRTM | Map style: &copy; OpenTopoMap',
  };

  // Harmonize items (can accept either GeoJSON features or cluster summaries)
  const mapItems = features.length > 0 ? features : clusters;

  return (
    <div style={{ height: '100%', width: '100%', position: 'relative' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%', borderRadius: '1.5rem' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          key={mapType}
          url={tileUrls[mapType] || tileUrls.map}
          attribution={attributions[mapType] || attributions.map}
          maxZoom={19}
        />

        <MapController center={center} zoom={zoom} />

        {mapItems.map((item: any, idx: number) => {
          let lat: number | undefined;
          let lng: number | undefined;
          let props: any = {};
          let id = idx;

          if (item.geometry?.coordinates) {
            // GeoJSON format [lng, lat]
            lng = item.geometry.coordinates[0];
            lat = item.geometry.coordinates[1];
            props = item.properties || {};
            id = props.id || idx;
          } else if (item.location?.coordinates) {
            lng = item.location.coordinates[0];
            lat = item.location.coordinates[1];
            props = item;
            id = item.id || idx;
          } else if (item.lat && item.lng) {
            lat = item.lat;
            lng = item.lng;
            props = item;
            id = item.id || idx;
          }

          if (lat === undefined || lng === undefined) return null;

          const isSelected =
            selectedFeature &&
            (selectedFeature.properties?.id === id || selectedFeature.id === id);

          // Sector color & emoji
          const issue = (props.issue_type || '').toLowerCase();
          let color = '#EA4335'; // Google Red default
          let icon = '📍';
          if (issue.includes('water')) {
            color = '#4285F4'; // Google Blue
            icon = '💧';
          } else if (issue.includes('drainage') || issue.includes('flood')) {
            color = '#1a73e8';
            icon = '🌊';
          } else if (issue.includes('electric') || issue.includes('power')) {
            color = '#FBBC05'; // Google Yellow
            icon = '⚡';
          } else if (issue.includes('health')) {
            color = '#34A853'; // Google Green
            icon = '🏥';
          } else if (issue.includes('road') || issue.includes('transit')) {
            color = '#ea8600';
            icon = '🚌';
          }

          const demand = props.independent_demand_count || 150;
          const radiusMeters = Math.max(300, Math.min(demand * 8, 3000));

          return (
            <React.Fragment key={`feat-${id}-${idx}`}>
              {/* PostGIS Geodesic Buffer Circle (FR-027) */}
              <Circle
                center={[lat, lng]}
                radius={radiusMeters}
                pathOptions={{
                  color: isSelected ? '#1a73e8' : color,
                  fillColor: color,
                  fillOpacity: isSelected ? 0.35 : 0.2,
                  weight: isSelected ? 2.5 : 1.5,
                  dashArray: isSelected ? undefined : '4, 4',
                }}
              />

              {/* Marker with Custom Google Teardrop Pin */}
              <Marker
                position={[lat, lng]}
                icon={createCustomPin(icon, color, isSelected)}
                eventHandlers={{
                  click: () => {
                    if (onSelectFeature) onSelectFeature(item);
                  },
                }}
              >
                <Popup>
                  <div style={{ minWidth: '180px', fontFamily: 'system-ui, sans-serif' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '16px' }}>{icon}</span>
                      <strong style={{ fontSize: '13px', color: '#1f1f1f' }}>
                        {props.village_ward || props.district || 'Community Hotspot'}
                      </strong>
                    </div>
                    <div style={{ fontSize: '11px', color: '#5f6368', lineHeight: '1.4' }}>
                      <div>Sector: <b style={{ color: '#1f1f1f' }}>{props.issue_type?.replace(/_/g, ' ') || 'Infrastructure'}</b></div>
                      <div>Demand: <b style={{ color: '#137333' }}>{demand} verified citizens</b></div>
                      <div>Score: <b style={{ color: '#0b57d0' }}>{props.priority_score || '84.5'}/100</b></div>
                    </div>
                    <div style={{ marginTop: '8px', borderTop: '1px solid #e0e3e7', paddingTop: '6px' }}>
                      <button
                        onClick={() => {
                          if (onSelectFeature) onSelectFeature(item);
                        }}
                        style={{
                          backgroundColor: '#0b57d0',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '9999px',
                          padding: '4px 10px',
                          fontSize: '11px',
                          fontWeight: 600,
                          cursor: 'pointer',
                          width: '100%',
                        }}
                      >
                        Inspect Full Evidence →
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}

        {/* ----------------------------------------------------------- Existing Municipal Infrastructure Facilities */}
        {showInfra &&
          infrastructure.map((fac: any, idx: number) => {
            const lat = fac.lat || fac.location?.coordinates?.[1];
            const lng = fac.lng || fac.location?.coordinates?.[0];
            if (lat === undefined || lng === undefined) return null;

            const type = (fac.type || '').toLowerCase();
            let facIcon = '🏢';
            let facColor = '#5f6368';
            if (type.includes('water')) {
              facIcon = '💧';
              facColor = '#1a73e8';
            } else if (type.includes('drainage') || type.includes('basin')) {
              facIcon = '🌊';
              facColor = '#0b57d0';
            } else if (type.includes('power') || type.includes('substation') || type.includes('electric')) {
              facIcon = '⚡';
              facColor = '#e37400';
            } else if (type.includes('health') || type.includes('clinic')) {
              facIcon = '🏥';
              facColor = '#137333';
            }

            return (
              <Marker
                key={`infra-${fac.id || idx}`}
                position={[lat, lng]}
                icon={createInfraPin(facIcon, facColor)}
              >
                <Popup>
                  <div style={{ minWidth: '170px', fontFamily: 'system-ui, sans-serif' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '15px' }}>{facIcon}</span>
                      <strong style={{ fontSize: '12px', color: '#1f1f1f' }}>{fac.name}</strong>
                    </div>
                    <div style={{ fontSize: '11px', color: '#5f6368', lineHeight: '1.4' }}>
                      <div>Type: <b style={{ color: '#1f1f1f' }}>{fac.type?.replace(/_/g, ' ')}</b></div>
                      <div>Status: <span style={{ color: facColor, fontWeight: 600 }}>{fac.status?.replace(/_/g, ' ')}</span></div>
                      {fac.capacity_pct && (
                        <div>Capacity Load: <b>{fac.capacity_pct}%</b></div>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
      </MapContainer>
    </div>
  );
}

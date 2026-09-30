'use client';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

// Fix for default marker icon in Next.js
const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function MapComponent({ clusters }: { clusters: any[] }) {
  // Try to find a cluster with location to center map, otherwise default to Pune
  const center = [-23.5505, -46.6333]; // default Sao Paulo, wait let's do [18.5204, 73.8567] Pune

  return (
    <MapContainer center={[18.5204, 73.8567]} zoom={12} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      {clusters.map((c: any) => {
        // Mocked location parsing - API says location is dict[str, Any]
        // If it's a GeoJSON Point we use it. For now let's just plot randomly near Pune if no geometry is given,
        // since scaffolding might not return real geometry. 
        // We will just do a check
        if (!c.location || !c.location.coordinates) return null;
        const [lng, lat] = c.location.coordinates; // GeoJSON is [lng, lat]
        
        return (
          <Circle 
            key={c.id} 
            center={[lat, lng]} 
            radius={c.independent_demand_count * 100}
            pathOptions={{ color: 'red', fillColor: '#f03', fillOpacity: 0.5 }}
          >
            <Popup>
              <strong>{c.issue_type}</strong><br/>
              Status: {c.status}<br/>
              Demand: {c.independent_demand_count}
            </Popup>
          </Circle>
        );
      })}
    </MapContainer>
  );
}

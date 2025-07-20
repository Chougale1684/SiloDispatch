import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

export default function LiveMap({ driverLocation, stops }) {
  return (
    <div className="h-96 w-full">
      <MapContainer 
        center={driverLocation || [12.9716, 77.5946]} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {driverLocation && (
          <Marker position={driverLocation}>
            <Popup>Driver Location</Popup>
          </Marker>
        )}
        {stops?.map((stop, index) => (
          <Marker key={index} position={[stop.lat, stop.lng]}>
            <Popup>Stop #{index + 1}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

const mapProvider = process.env.REACT_APP_MAP_PROVIDER;
const apiKey = process.env.REACT_APP_MAP_API_KEY;
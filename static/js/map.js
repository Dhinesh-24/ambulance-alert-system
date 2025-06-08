const map = L.map('map').setView([13.0827, 80.2707], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Add ambulance marker
const ambulanceMarker = L.marker([13.0827, 80.2707]).addTo(map)
  .bindPopup('Ambulance Location').openPopup();

// Real-time simulated location (or use API if backend is ready)
let lat = 13.0827;
let lng = 80.2707;

setInterval(() => {
  lat += (Math.random() - 0.5) * 0.001;
  lng += (Math.random() - 0.5) * 0.001;

  ambulanceMarker.setLatLng([lat, lng]).update();
  ambulanceMarker.bindPopup(`Ambulance Location: ${lat.toFixed(5)}, ${lng.toFixed(5)}`).openPopup();
  map.panTo([lat, lng]);
}, 3000);

async function updateAmbulanceLocation() {
  const res = await fetch('/api/ambulance-location');
  const data = await res.json();

  ambulanceMarker.setLatLng([data.lat, data.lng]).update();
  ambulanceMarker.bindPopup(`Ambulance Location: ${data.lat}, ${data.lng}`).openPopup();
  map.panTo([data.lat, data.lng]);
}

updateAmbulanceLocation();
setInterval(updateAmbulanceLocation, 5000);
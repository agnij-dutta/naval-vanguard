// Initialize Leaflet map
var map = L.map('map').setView([20.0, 70.0], 5);

// Set up the tile layer for the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

// Fetch contacts from backend API and plot them on the map
fetch('/contacts')
    .then(response => response.json())
    .then(contacts => {
        contacts.forEach(contact => {
            const coordinates = JSON.parse(contact.coordinates);
            coordinates.forEach(coord => {
                L.marker([coord.lat, coord.lon]).addTo(map)
                    .bindPopup(`<b>${contact.name}</b><br>Type: ${contact.type}<br>Significance: ${contact.significance}`);
            });
        });
    });

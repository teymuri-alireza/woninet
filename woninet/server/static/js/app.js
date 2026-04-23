let found_devices = new Map()

function getLatencyClass(latency) {
    if (latency <= 50) return "latency-good";
    if (latency <= 150) return "latency-warn";
    return "latency-bad";
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function createDeviceCard(device) {
    const ip = escapeHtml(device.ip ?? "Unknown");
    const latency = device.latency ?? "N/A";
    const lastSeen = escapeHtml(device.last_seen ?? "Unknown");
    const latencyClass = typeof latency === "number" ? getLatencyClass(latency) : "latency-warn";

    const article = document.createElement("article");
    article.className = "device-card";
    article.dataset.ip = device.ip || ""; // store raw IP for lookup

    article.innerHTML = `
        <div class="device-ip">${ip}</div>
        <div class="device-meta">
            <div class="meta-row">
                <span class="meta-label">Latency</span>
                <span class="latency-pill ${latencyClass}">${latency} ms</span>
            </div>
            <div class="meta-row">
                <span class="meta-label">Last seen</span>
                <span class="last-seen">${lastSeen}</span>
            </div>
        </div>
    `;

    return article;
}

function updateDeviceCard(card, device) {
    const latency = device.latency ?? "N/A";
    const lastSeen = escapeHtml(device.last_seen ?? "Unknown");
    const latencyClass = typeof latency === "number" ? getLatencyClass(latency) : "latency-warn";

    const latencySpan = card.querySelector(".latency-pill");
    const lastSeenSpan = card.querySelector(".last-seen");

    if (latencySpan) {
        latencySpan.textContent = `${latency} ms`;
        latencySpan.className = `latency-pill ${latencyClass}`;
    }
    if (lastSeenSpan) {
        lastSeenSpan.textContent = lastSeen;
    }
}

function renderDevices(devicesResponse) {
    const container = document.getElementById("devices");

    // Remove loader once data is fetched
    const loader = document.getElementById("loader");
    if (loader) loader.remove();

    const devices = devicesResponse?.devices;
    if (!devices || devices.length === 0) {
        container.innerHTML = `<div class="empty-state">No devices found.</div>`;
        found_devices.clear();
        return;
    }
    
    // Render everything and populate found_devices
    if (found_devices.size === 0 && container.children.length === 0) {
        container.innerHTML = "";
        devices.forEach(device => {
            if (!device.ip) return;
            const card = createDeviceCard(device);
            container.appendChild(card);
            found_devices.set(device.ip, { device, element: card });
        });
        return;
    }

    // Update existing cards or add new ones
    devices.forEach(device => {
        if (!device.ip) return;
        const existing = found_devices.get(device.ip);
        if (existing) {
            updateDeviceCard(existing.element, device);
            existing.device = device;
        } else {
            const card = createDeviceCard(device);
            container.appendChild(card);
            found_devices.set(device.ip, { device, element: card });
        }
    });
}

async function loadDevices() {
    const container = document.getElementById("devices");

    try {
        const response = await fetch("/devices");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const devices = await response.json();
        renderDevices(devices);
    } catch (error) {
        // Only show error if we have nothing rendered yet
        if (found_devices.size === 0 && !container.hasChildNodes()) {
            container.innerHTML = `<div class="empty-state">Failed to load devices.</div>`;
        }
        console.error("Failed to load devices:", error);
    }
}

setInterval(loadDevices, 2000);
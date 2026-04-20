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

function renderDevices(devices) {
    const container = document.getElementById("devices");

    if (!devices || devices.length === 0) {
        container.innerHTML = `<div class="empty-state">No devices found.</div>`;
        return;
    }

    container.innerHTML = devices.devices.map(device => {
        const ip = escapeHtml(device.device_ip ?? "Unknown");
        const latency = device.value ?? "N/A";
        const lastSeen = escapeHtml(device.timestamp ?? "Unknown");
        const latencyClass = typeof latency === "number" ? getLatencyClass(latency) : "latency-warn";

        return `
            <article class="device-card">
                <div class="device-ip">${ip}</div>
                <div class="device-meta">
                    <div class="meta-row">
                        <span class="meta-label">Latency</span>
                        <span class="latency-pill ${latencyClass}">${latency} ms</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Last seen</span>
                        <span>${lastSeen}</span>
                    </div>
                </div>
            </article>
        `;
    }).join("");
}

async function loadDevices() {
    const container = document.getElementById("devices");

    try {
        const response = await fetch("/devices");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const devices = await response.json();
        renderDevices(devices);
    } catch (error) {
        container.innerHTML = `<div class="empty-state">Failed to load devices.</div>`;
        console.error("Failed to load devices:", error);
    }
}

loadDevices();

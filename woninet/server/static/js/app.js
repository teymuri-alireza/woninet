let lastData = { devices: [], gateway: null };

function getDeviceState(device) {
    const latency = device.latency ?? 0;
    const loss = device.packet_loss ?? 0;

    if (latency === 0)
        return "offline";

    if (latency > 100 || loss > 2)
        return "degraded";

    return "online";
}

function createDeviceRow(device) {
    const state = getDeviceState(device);
    const isUp = (device.latency ?? 0) !== 0;

    const latency = isUp ? `${device.latency} ms` : "--";
    const jitter = isUp ? `${(device.jitter ?? 0).toFixed(1)} ms` : "--";
    const loss = `${(device.packet_loss ?? 0).toFixed(1)}%`;

    return `
    <tr>
        <td><span class="status-badge ${state}">${state}</span></td>
        <td><strong>${device.ip}</strong></td>
        <td>${latency}</td>
        <td>${jitter}</td>
        <td>${loss}</td>
        <td class="cell-mono">${device.mac ?? "--"}</td>
        <td>${device.last_seen ?? "--"}</td>
        <td class="cell-action">
            <a class="device-link" href="/devices/${device.ip}" title="Device details">
                <i class="fa fa-ellipsis-v"></i>
            </a>
        </td>
    </tr>
    `;
}

function updateOverview(devices) {
    const total = devices.length;
    const reachable = devices.filter(d => (d.latency ?? 0) > 0);

    const avgLatency = reachable.length
        ? Math.round(reachable.reduce((sum, d) => sum + d.latency, 0) / reachable.length)
        : 0;

    const avgLoss = reachable.length
        ? (reachable.reduce((sum, d) => sum + (d.packet_loss ?? 0), 0) / reachable.length).toFixed(1)
        : 0;

    document.getElementById("total_devices").textContent = total;
    document.getElementById("online_devices").textContent = reachable.length;
    document.getElementById("avg_latency").textContent = `${avgLatency} ms`;
    document.getElementById("avg_packet_loss").textContent = `${avgLoss}%`;
}

function renderDevices(data) {
    const devices = data.devices || [];

    updateOverview(devices);

    const search = document.getElementById("search").value.toLowerCase();
    const filter = document.getElementById("filter_status").value;

    const filtered = devices.filter(device => {
        const matchesSearch =
            device.ip.toLowerCase().includes(search) ||
            (device.mac || "").toLowerCase().includes(search);

        const matchesFilter =
            filter === "all" || getDeviceState(device) === filter;

        return matchesSearch && matchesFilter;
    });

    document.getElementById("devices").innerHTML = filtered.length
        ? filtered.map(createDeviceRow).join("")
        : `<tr><td colspan="8" class="empty-row">No devices match the current filters.</td></tr>`;
}

async function loadDevices() {
    const statusDot = document.getElementById("status_dot");
    const statusText = document.getElementById("status_text");

    try {
        const response = await fetch("/api/devices");
        const data = await response.json();

        lastData = data;
        renderDevices(data);

        const gatewayEl = document.getElementById("gateway");
        if (gatewayEl) gatewayEl.textContent = data.gateway || "—";

        statusDot.classList.remove("disconnected");
        statusText.textContent = "Connected";

    } catch (error) {
        statusDot.classList.add("disconnected");
        statusText.textContent = "Disconnected";
        console.error(error);
    }
}

// Search and filter re-render from the last response instead of refetching.
document.getElementById("search")?.addEventListener("input", () => renderDevices(lastData));
document.getElementById("filter_status")?.addEventListener("change", () => renderDevices(lastData));

loadDevices();
setInterval(loadDevices, 5000);

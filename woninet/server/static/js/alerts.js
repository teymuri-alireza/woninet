let allAlerts = [];

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[ch]));
}

// Accepts a bare array, or an object wrapping the list.
function extractAlerts(data) {
    if (Array.isArray(data)) return data;
    return data?.alerts || data?.events || data?.recent_alert_events || [];
}

function createAlertCard(event) {
    const type = (event.event_type || "").toLowerCase();
    const eventClass = type === "trigger" ? "event-trigger" : "event-recover";
    const unit = (event.metric === "latency" || event.metric === "jitter") ? "ms" : "%";
    const value = Number.isFinite(Number(event.value)) ? Number(event.value).toFixed(2) : "--";
    const time = event.timestamp ? new Date(event.timestamp).toLocaleString() : "--";

    return `
    <div class="event ${eventClass}">
        <div class="event-main">
            <span class="event-type">${escapeHtml(type.toUpperCase())}</span>
            <span class="event-details">
                <strong>${escapeHtml(event.device_ip)}</strong>
                <span class="sep">|</span>
                ${escapeHtml(event.metric)}: ${value} ${unit}
            </span>
        </div>
        <span class="event-time">${escapeHtml(time)}</span>
    </div>
    `;
}

function renderAlerts() {
    const search = document.getElementById("alert_search").value.trim().toLowerCase();
    const type = document.getElementById("alert_type").value;

    const filtered = allAlerts.filter(event => {
        const matchesIp = (event.device_ip || "").toLowerCase().includes(search);
        const matchesType = type === "all" || (event.event_type || "").toLowerCase() === type;
        return matchesIp && matchesType;
    });

    document.getElementById("alert_count").textContent =
        `Showing ${filtered.length} of ${allAlerts.length} events`;

    document.getElementById("alerts").innerHTML = filtered.length
        ? filtered.map(createAlertCard).join("")
        : `<div class="no-alerts">No alert events match the current filters.</div>`;
}

async function loadAlerts() {
    const statusDot = document.getElementById("status_dot");
    const statusText = document.getElementById("status_text");

    try {
        const response = await fetch("/api/alerts");
        const data = await response.json();

        allAlerts = extractAlerts(data)
            .slice()
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        renderAlerts();

        statusDot.classList.remove("disconnected");
        statusText.textContent = "Connected";

    } catch (error) {
        statusDot.classList.add("disconnected");
        statusText.textContent = "Disconnected";
        console.error("Error loading alerts:", error);
    }
}

// Filters re-render from the last response instead of refetching.
document.getElementById("alert_search")?.addEventListener("input", renderAlerts);
document.getElementById("alert_type")?.addEventListener("change", renderAlerts);

loadAlerts();
setInterval(loadAlerts, 5000);

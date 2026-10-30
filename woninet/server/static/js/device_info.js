// Device info page. Device IP comes from the URL: /devices/<ip>
const ip = decodeURIComponent(location.pathname.split("/").filter(Boolean).pop() || "");
const $ = id => document.getElementById(id);

const RANGES = {
    day: [[7, "Last 7 days"], [30, "Last 30 days"], [90, "Last 90 days"], [180, "Last 180 days"], [365, "Last 365 days"]],
    hour: [[1, "Last 24 hours"], [2, "Last 2 days"], [3, "Last 3 days"], [7, "Last 7 days"]],
};
const DEFAULT_DAYS = { day: 90, hour: 3 };

const state = { granularity: "day", days: DEFAULT_DAYS.day };
let availabilityRequest = 0;
let lastRenderKey = "";

/* ---------- Helpers ---------- */
function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[ch]));
}

function getDeviceState(device) {
    const latency = device.latency ?? 0;
    const loss = device.packet_loss ?? 0;
    if (latency === 0) return "offline";
    if (latency > 100 || loss > 2) return "degraded";
    return "online";
}

function parseStart(value) {
    const [datePart, timePart = "00:00:00"] = value.split("T");
    const [y, m, d] = datePart.split("-").map(Number);
    const [h = 0, min = 0] = timePart.split(":").map(Number);
    return new Date(y, m - 1, d, h, min);
}

function level(bucket) {
    if (bucket.uptime === null || bucket.uptime === undefined) return "none";
    if (bucket.uptime >= 99) return "good";
    if (bucket.uptime >= 90) return "ok";
    return "bad";
}

function cellHtml(bucket, date, extraStyle = "") {
    const label = state.granularity === "hour"
        ? date.toLocaleString(undefined, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })
        : date.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
    const detail = bucket.checks
        ? `${bucket.uptime}% uptime (${bucket.up_checks} of ${bucket.checks} checks)`
        : "No checks recorded";
    const style = extraStyle ? ` style="${extraStyle}"` : "";
    return `<i class="cell lvl-${level(bucket)}" data-label="${escapeHtml(label)}" data-detail="${escapeHtml(detail)}"${style}></i>`;
}

function setConnected(connected) {
    $("status_dot").classList.toggle("disconnected", !connected);
    $("status_text").textContent = connected ? "Connected" : "Disconnected";
}

function showError(message) {
    const box = $("page_error");
    box.textContent = message;
    box.hidden = false;
}

function hideError() {
    $("page_error").hidden = true;
}

/* ---------- Live device metrics ---------- */
function renderDevice(device) {
    const badge = $("device_state");

    if (!device) {
        badge.className = "status-badge unknown";
        badge.textContent = "unknown";
        return;
    }

    const deviceState = getDeviceState(device);
    const isUp = (device.latency ?? 0) !== 0;

    badge.className = `status-badge ${deviceState}`;
    badge.textContent = deviceState;

    $("latency").textContent = isUp ? `${device.latency} ms` : "--";
    $("jitter").textContent = isUp ? `${(device.jitter ?? 0).toFixed(1)} ms` : "--";
    $("packet_loss").textContent = `${(device.packet_loss ?? 0).toFixed(1)}%`;

    $("detail_mac").textContent = device.mac ?? "--";
    $("detail_last_seen").textContent = device.last_seen
        ? new Date(device.last_seen).toLocaleString()
        : "--";
}

async function loadDevice() {
    try {
        const response = await fetch("/api/devices");
        const data = await response.json();
        setConnected(true);
        renderDevice((data.devices || []).find(device => device.ip === ip));
    } catch (error) {
        setConnected(false);
        console.error(error);
    }
}

/* ---------- Availability heatmap ---------- */
function renderDayHeatmap(buckets) {
    const first = parseStart(buckets[0].start);
    const offset = (first.getDay() + 6) % 7; // Monday = 0
    const cols = Math.ceil((offset + buckets.length) / 7);
    const size = buckets.length <= 31 ? 34 : buckets.length <= 100 ? 26 : 18;

    let months = [];
    let lastMonth = -1;
    const cells = buckets.map((bucket, i) => {
        const date = parseStart(bucket.start);
        if (date.getMonth() !== lastMonth) {
            lastMonth = date.getMonth();
            months.push({ col: Math.floor((offset + i) / 7) + 1, name: date.toLocaleDateString(undefined, { month: "short" }) });
        }
        return cellHtml(bucket, date, i === 0 ? `grid-row:${offset + 1}` : "");
    });
    // Drop a month label when the next one starts within 3 columns (they'd overlap).
    months = months.filter((m, i) => i === months.length - 1 || months[i + 1].col - m.col >= 3);

    const monthSpans = months.map(m => `<span style="grid-column:${m.col}">${escapeHtml(m.name)}</span>`).join("");
    const weekdays = ["Mon", "", "Wed", "", "Fri", "", ""].map(d => `<span>${d}</span>`).join("");

    return `
    <div class="heat-wrap" style="--cell:${size}px">
        <div class="heat-axis heat-day-axis">${weekdays}</div>
        <div class="heat-main">
            <div class="heat-top" style="grid-template-columns:repeat(${cols}, ${size}px);column-gap:3px">${monthSpans}</div>
            <div class="heat-grid heat-day">${cells.join("")}</div>
        </div>
    </div>`;
}

function renderHourHeatmap(buckets) {
    const rows = new Map();
    buckets.forEach(bucket => {
        const date = parseStart(bucket.start);
        const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
        if (!rows.has(key)) rows.set(key, { date, cells: Array(24).fill(null) });
        rows.get(key).cells[date.getHours()] = { bucket, date };
    });

    const list = [...rows.values()];
    const axis = list.map(row =>
        `<span>${escapeHtml(row.date.toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short" }))}</span>`
    ).join("");
    const hours = Array.from({ length: 24 }, (_, h) => `<span>${h % 6 === 0 ? String(h).padStart(2, "0") : ""}</span>`).join("");
    const cells = list.map(row =>
        row.cells.map(c => c ? cellHtml(c.bucket, c.date) : `<i class="cell blank"></i>`).join("")
    ).join("");

    return `
    <div class="heat-wrap">
        <div class="heat-axis heat-hour-axis">${axis}</div>
        <div class="heat-main">
            <div class="heat-top heat-hour-top">${hours}</div>
            <div class="heat-grid heat-hour">${cells}</div>
        </div>
    </div>`;
}

function renderAvailability(data) {
    const buckets = data.buckets || [];
    const summary = data.summary || {};
    const rangeText = $("range").selectedOptions[0]?.textContent.toLowerCase() ?? "";

    $("uptime_label").textContent = `Uptime (${rangeText})`;
    $("uptime").textContent = summary.uptime === null || summary.uptime === undefined
        ? "--"
        : `${summary.uptime.toFixed(2)}%`;
    $("detail_checks").textContent = (summary.checks ?? 0).toLocaleString();
    $("availability_meta").textContent = summary.checks
        ? `${summary.checks.toLocaleString()} checks recorded, ${rangeText}`
        : "No checks recorded in this range yet";

    const heatmap = $("heatmap");
    if (!buckets.length) {
        heatmap.innerHTML = `<div class="heat-empty">No availability data for this device.</div>`;
        return;
    }

    heatmap.innerHTML = data.granularity === "hour" ? renderHourHeatmap(buckets) : renderDayHeatmap(buckets);

    // Newest data is on the right; show it first after a range change.
    const key = `${state.granularity}:${state.days}`;
    if (key !== lastRenderKey) {
        lastRenderKey = key;
        heatmap.scrollLeft = heatmap.scrollWidth;
    }
}

async function loadAvailability() {
    const request = ++availabilityRequest;
    const url = `/api/devices/${encodeURIComponent(ip)}/availability?days=${state.days}&granularity=${state.granularity}`;

    try {
        const response = await fetch(url);
        if (request !== availabilityRequest) return; // a newer request replaced this one

        if (!response.ok) {
            showError(response.status === 404
                ? `No device with IP ${ip} was found.`
                : `Availability could not be loaded (HTTP ${response.status}).`);
            $("heatmap").innerHTML = `<div class="heat-empty">Availability data is unavailable.</div>`;
            return;
        }

        const data = await response.json();
        if (request !== availabilityRequest) return;

        hideError();
        setConnected(true);
        renderAvailability(data);
    } catch (error) {
        if (request === availabilityRequest) setConnected(false);
        console.error(error);
    }
}

/* ---------- Tooltip ---------- */
const tooltip = $("tooltip");

function showTooltip(event) {
    const cell = event.target.closest("[data-label]");
    if (!cell) {
        tooltip.hidden = true;
        return;
    }

    const title = document.createElement("strong");
    title.textContent = cell.dataset.label;
    tooltip.replaceChildren(title, document.createTextNode(cell.dataset.detail));
    tooltip.hidden = false;

    let x = event.clientX + 14;
    if (x + tooltip.offsetWidth > window.innerWidth - 8) x = event.clientX - tooltip.offsetWidth - 14;
    tooltip.style.left = `${Math.max(8, x)}px`;
    tooltip.style.top = `${event.clientY + 16}px`;
}

$("heatmap").addEventListener("mousemove", showTooltip);
$("heatmap").addEventListener("mouseleave", () => { tooltip.hidden = true; });

/* ---------- Controls ---------- */
function syncControls() {
    document.querySelectorAll(".segmented button").forEach(button => {
        const active = button.dataset.granularity === state.granularity;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", active);
    });

    $("range").innerHTML = RANGES[state.granularity]
        .map(([days, text]) => `<option value="${days}"${days === state.days ? " selected" : ""}>${text}</option>`)
        .join("");
}

document.querySelectorAll(".segmented button").forEach(button => {
    button.addEventListener("click", () => {
        if (button.dataset.granularity === state.granularity) return;
        state.granularity = button.dataset.granularity;
        state.days = DEFAULT_DAYS[state.granularity];
        syncControls();
        loadAvailability();
    });
});

$("range").addEventListener("change", event => {
    state.days = Number(event.target.value);
    loadAvailability();
});

/* ---------- Start ---------- */
$("device_ip").textContent = ip;
$("detail_ip").textContent = ip;
document.title = `woninet ${ip}`;

syncControls();
loadDevice();
loadAvailability();

setInterval(loadDevice, 5000);
setInterval(loadAvailability, 5000);

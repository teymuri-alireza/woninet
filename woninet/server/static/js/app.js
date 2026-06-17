let found_devices = new Map();
let events = [];

function addEvent(message) {

    const timestamp = new Date().toLocaleTimeString();

    events.unshift(`${timestamp} - ${message}`);

    if(events.length > 15)
        events.pop();

    document.getElementById("events").innerHTML =
        events.map(e => `<div class="event">${e}</div>`).join("");
}

function getDeviceState(device) {

    const latency = device.latency ?? 0;
    const loss = device.packet_loss ?? 0;

    if(latency === 0)
        return "offline";

    if(latency > 100 || loss > 2)
        return "degraded";

    return "online";
}

function createDeviceCard(device){

    const state = getDeviceState(device);

    return `
        <article class="device-card device-${state}">

            <div class="device-header">

                <div class="device-ip">
                    ${device.ip}
                </div>

                <div class="device-status">
                    ${state.toUpperCase()}
                </div>

            </div>

            <div class="metrics">

                <div class="metric">
                    <div class="metric-label">Latency</div>
                    <div class="metric-value">
                        ${device.latency || "OFFLINE"} ms
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">Packet Loss</div>
                    <div class="metric-value">
                        ${(device.packet_loss ?? 0).toFixed(1)}%
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">MAC</div>
                    <div class="metric-value">
                        ${device.mac}
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">Last Seen</div>
                    <div class="metric-value">
                        ${device.last_seen}
                    </div>
                </div>

            </div>

        </article>
    `;
}

function updateOverview(devices){

    const total = devices.length;

    const online =
        devices.filter(d => (d.latency ?? 0) > 0).length;

    const latencyDevices =
        devices.filter(d => (d.latency ?? 0) > 0);

    const avgLatency =
        latencyDevices.length
        ? Math.round(
            latencyDevices.reduce(
                (a,b)=>a+b.latency,0
            ) / latencyDevices.length
        )
        : 0;

    const validDevices = devices.filter(device => device.latency !== 0);
    const avgLoss = validDevices.length
        ? (
            validDevices.reduce(
                (sum, device) => sum + (device.packet_loss ?? 0), 0) / validDevices.length
        ).toFixed(1)
        : 0;

    document.getElementById(
        "total_devices"
    ).textContent = total;

    document.getElementById(
        "online_devices"
    ).textContent = online;

    document.getElementById(
        "avg_latency"
    ).textContent = `${avgLatency} ms`;

    document.getElementById(
        "avg_packet_loss"
    ).textContent = `${avgLoss}%`;

    // const health =
    //     Math.max(
    //         0,
    //         Math.round(
    //             (online / Math.max(total,1))*100 -
    //             avgLoss*5
    //         )
    //     );

    // document.getElementById(
    //     "health_score"
    // ).textContent = `${health}%`;

    // document.getElementById(
    //     "health_text"
    // ).textContent =
    //     health > 90
    //     ? "Excellent"
    //     : health > 70
    //     ? "Good"
    //     : "Degraded";
}

function renderDevices(data){

    const devices = data.devices || [];

    updateOverview(devices);

    const search =
        document.getElementById("search")
        .value
        .toLowerCase();

    const filter =
        document.getElementById("filter_status")
        .value;

    const filtered =
        devices.filter(device => {

            const state =
                getDeviceState(device);

            const matchesSearch =
                device.ip.toLowerCase().includes(search) ||
                (device.mac || "")
                .toLowerCase()
                .includes(search);

            const matchesFilter =
                filter === "all" ||
                state === filter;

            return matchesSearch &&
                   matchesFilter;
        });

    document.getElementById(
        "devices"
    ).innerHTML =
        filtered.map(createDeviceCard).join("");
}

async function loadDevices(){

    const statusDot =
        document.getElementById("status_dot");
    const statusText = document.getElementById("status_text");

    try{

        const response =
            await fetch("/devices/");

        const data =
            await response.json();

        renderDevices(data);

        statusDot.style.background =
            "#22c55e";
        statusText.textContent = "Connected";

    }catch(error){

        statusDot.style.background =
            "#ef4444";
        statusText.textContent = "Disconnected";

        console.error(error);
    }
}

document
.getElementById("search")
?.addEventListener(
    "input",
    loadDevices
);

document
.getElementById("filter_status")
?.addEventListener(
    "change",
    loadDevices
);

async function loadAlertEvents() {
    try {
        const response = await fetch("/stats/");
        const data = await response.json();

        const alertEvents = data.recent_alert_events || [];

        const alert_events = alertEvents.map(event => {
            const time = new Date(event.timestamp)
                .toLocaleString();
            
            const eventClass = event.event_type === "trigger" ? "event-trigger" : "event-recover";

            return `
                <div class="event ${eventClass}">
                    <strong>${event.event_type.toUpperCase()}</strong><br>
                    ${event.device_ip} | ${event.metric}: ${event.value.toFixed(2)} ms
                    <small>(${time})</small>
                </div>
            `;
        }).slice(0, 15);

        document.getElementById("events").innerHTML =
            alert_events.join("");

    } catch (error) {
        console.error("Error loading alert events:", error);
    }
}

loadDevices();
loadAlertEvents();

setInterval(loadDevices, 5000);
setInterval(loadAlertEvents, 5000);

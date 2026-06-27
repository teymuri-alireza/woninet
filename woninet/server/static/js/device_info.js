const deviceIP = document.getElementById("device-ip");
const latency = document.getElementById("device-latency");
const deviceMAC = document.getElementById("device-mac");
const packetLoss = document.getElementById("device-packet-loss");
const status = document.getElementById("device-status");
const lastSeen = document.getElementById("device-last-seen");
const alertSatteLatency = document.getElementById("alert-state-latency");
const alertStatePacketLoss = document.getElementById("alert-state-packet-loss");
const alertsContainer = document.getElementById("events");
const deviceCard = document.getElementById("device-card");
const lineGraph = document.getElementById("device-recent-events-line-graph");


function loadDeviceCardStyle(device_latency) {
    // Remove everything
    deviceCard.classList.remove("device-offline");
    deviceCard.classList.remove("device-degraded");
    deviceCard.classList.remove("device-online");
    // reassign style
    if (device_latency === 0) {
        deviceCard.classList.add("device-offline");
    } else if (device_latency >= 100) {
        deviceCard.classList.add("device-degraded");
    } else {
        deviceCard.classList.add("device-online");
    }
}


function renderAlertEvents(deviceAlertEvents) {
    alertsContainer.textContent = "";

    if (deviceAlertEvents.length > 0) {
        deviceAlertEvents.forEach(event => {
            const eventDiv = document.createElement("div");
            eventDiv.classList.add("event");
            eventDiv.classList.add(
                event.event_type === "recover" ? "event-recover" : "event-trigger"
            );

            const strong = document.createElement("strong");
            strong.textContent = event.event_type.toUpperCase();

            const br = document.createElement("br");

            const text = document.createTextNode(`${event.metric}: ${Number(event.value).toFixed(2)} `);

            const small = document.createElement("small");
            small.textContent = `(${event.timestamp})`;

            eventDiv.appendChild(strong);
            eventDiv.appendChild(br);
            eventDiv.appendChild(text);
            eventDiv.appendChild(small);

            alertsContainer.appendChild(eventDiv);
        });
    } else {
        const p = document.createElement("p");
        p.className = "no-alerts";
        p.textContent = "No alerts";
        alertsContainer.appendChild(p);
    }
}


async function loadDeviceInfo() {
    const ip = window.location.pathname.split("/").pop();
    deviceIP.textContent = ip;

    const response = await fetch(`/devices/${ip}/api`);
    const data = await response.json();
    const device = data.device || "";
    const deviceAlertState = data.device_alert_state || "";
    const deviceAlertEvents = data.device_recent_alert_events || [];

    device.latency === 0 ? latency.textContent = "OFFLINE" : latency.textContent = `${device.latency} ms`;
    deviceMAC.textContent = device.mac;
    packetLoss.textContent = `${device.packet_loss} %`;
    device.latency === 0 ? status.textContent = "OFFLINE" : status.textContent = "ONLINE";
    lastSeen.textContent = device.last_seen;

    alertSatteLatency.textContent = deviceAlertState.latency_ms;
    alertStatePacketLoss.textContent = deviceAlertState.packet_loss;

    // Send current date as query to prevent cache from not loading the new graph image
    lineGraph.src = `/charts/${ip}.png?v=${Date.now()}`

    loadDeviceCardStyle(device.latency);

    renderAlertEvents(deviceAlertEvents);
}

loadDeviceInfo();
setInterval(loadDeviceInfo, 5000);
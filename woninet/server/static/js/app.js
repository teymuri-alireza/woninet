async function loadDevices() {
    const response = await fetch("/devices");
    const devices = await response.json();

    const container = document.getElementById("devices");
    container.innerHTML = JSON.stringify(devices, null, 2);
}

loadDevices();
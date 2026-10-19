const FIELDS = ["max_workers", "arp_noise_limit"];

const form = document.getElementById("settings_form");
const saveBtn = document.getElementById("save_btn");
const resetBtn = document.getElementById("reset_btn");
const messageEl = document.getElementById("form_message");

let savedValues = {};   // values as last loaded from / saved to the server
let messageTimer = null;

function showMessage(text, type) {
    clearTimeout(messageTimer);
    messageEl.textContent = text;
    messageEl.className = `form-message ${type}`;
    messageEl.hidden = false;

    if (type === "success") {
        messageTimer = setTimeout(() => { messageEl.hidden = true; }, 4000);
    }
}

function setConnected(connected) {
    document.getElementById("status_dot").classList.toggle("disconnected", !connected);
    document.getElementById("status_text").textContent = connected ? "Connected" : "Disconnected";
}

function currentValues() {
    const values = {};
    FIELDS.forEach(name => { values[name] = form.elements[name].value.trim(); });
    return values;
}

function isDirty() {
    const now = currentValues();
    return FIELDS.some(name => now[name] !== String(savedValues[name]));
}

function updateButtons() {
    const dirty = isDirty();
    saveBtn.disabled = !dirty;
    resetBtn.disabled = !dirty;
}

function setFieldError(name, text) {
    const input = form.elements[name];
    document.getElementById(`${name}_error`).textContent = text;
    input.classList.toggle("invalid", Boolean(text));
}

function validate() {
    const rules = {
        max_workers: { min: 1, label: "Max Workers" },
        arp_noise_limit: { min: 0, label: "ARP Noise Limit" },
    };

    let valid = true;

    FIELDS.forEach(name => {
        const raw = form.elements[name].value.trim();
        const { min, label } = rules[name];
        const num = Number(raw);
        let error = "";

        if (raw === "") {
            error = `${label} is required.`;
        } else if (!Number.isInteger(num)) {
            error = `${label} must be a whole number.`;
        } else if (num < min) {
            error = `${label} must be at least ${min}.`;
        }

        setFieldError(name, error);
        if (error) valid = false;
    });

    return valid;
}

function populate(settings) {
    FIELDS.forEach(name => {
        form.elements[name].value = settings[name];
        form.elements[name].disabled = false;
        setFieldError(name, "");
    });
    savedValues = { ...settings };
    updateButtons();
}

async function loadSettings() {
    try {
        const response = await fetch("/api/settings");
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        populate(data.settings || {});
        setConnected(true);

    } catch (error) {
        setConnected(false);
        showMessage("Unable to load settings. Please try again later.", "error");
        console.error("Error loading settings:", error);
    }
}

async function saveSettings(event) {
    event.preventDefault();

    if (!validate()) return;

    // The endpoint reads Form fields, so send url-encoded form data.
    const body = new URLSearchParams(currentValues());

    saveBtn.disabled = true;
    resetBtn.disabled = true;

    try {
        const response = await fetch("/api/settings", { method: "POST", body });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        savedValues = currentValues();
        updateButtons();
        setConnected(true);
        showMessage("Settings saved successfully.", "success");

    } catch (error) {
        updateButtons();
        showMessage("Failed to save settings. Please try again.", "error");
        console.error("Error saving settings:", error);
    }
}

function resetForm() {
    populate(savedValues);
    messageEl.hidden = true;
}

FIELDS.forEach(name => {
    form.elements[name].addEventListener("input", () => {
        setFieldError(name, "");
        updateButtons();
    });
});

form.addEventListener("submit", saveSettings);
resetBtn.addEventListener("click", resetForm);

loadSettings();

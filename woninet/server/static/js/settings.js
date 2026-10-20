// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
// Name of the target IP field: must match the form input's `name` / `id`,
// the key returned by GET /api/settings, and the Form parameter in the API.
const TARGET_FIELD = "target_ip_list";

const INT_RULES = {
    max_workers:     { min: 1, label: "Max Workers" },
    arp_noise_limit: { min: 0, label: "ARP Noise Limit" },
};

// ---------------------------------------------------------------------------
// Elements and state
// ---------------------------------------------------------------------------
const form = document.getElementById("settings_form");
const saveBtn = document.getElementById("save_btn");
const resetBtn = document.getElementById("reset_btn");
const messageEl = document.getElementById("form_message");

// Every named input / textarea in the form is treated as a setting.
const FIELDS = Array.from(form.elements)
    .filter(el => el.name && ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName))
    .map(el => el.name);

let savedValues = {};   // normalized values as last loaded from / saved to the server
let messageTimer = null;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
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

// Splits a target string into trimmed entries, ignoring empty ones and
// optional surrounding quotes (e.g. "192.168.1.1-100" -> 192.168.1.1-100).
function parseTargets(raw) {
    return String(raw ?? "")
        .split(/[,\n]/)
        .map(entry => entry.trim().replace(/^["']+|["']+$/g, "").trim())
        .filter(Boolean);
}

// Canonical form used for comparison and for sending to the API.
function normalizeValue(name, raw) {
    if (name === TARGET_FIELD) {
        return parseTargets(raw).join(",");
    }
    return String(raw ?? "").trim();
}

function currentValues() {
    const values = {};
    FIELDS.forEach(name => {
        values[name] = normalizeValue(name, form.elements[name].value);
    });
    return values;
}

function isDirty() {
    const now = currentValues();
    return FIELDS.some(name => now[name] !== (savedValues[name] ?? ""));
}

function updateButtons() {
    const dirty = isDirty();
    saveBtn.disabled = !dirty;
    resetBtn.disabled = !dirty;
}

function setFieldError(name, text) {
    const input = form.elements[name];
    const errorEl = document.getElementById(`${name}_error`);
    if (errorEl) errorEl.textContent = text;
    input.classList.toggle("invalid", Boolean(text));
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------
const OCTET_MAX = 255;
const TARGET_PATTERN = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})(?:-(\d{1,3}))?$/;

// Accepts a single IPv4 address ("192.168.1.110") or a last-octet range
// ("192.168.1.1-100"). Returns an error string, or "" when valid.
function validateTarget(entry) {
    const match = entry.match(TARGET_PATTERN);

    if (!match) {
        return `"${entry}" is not a valid IP address or range.`;
    }

    const octets = match.slice(1, 5).map(Number);
    if (octets.some(octet => octet > OCTET_MAX)) {
        return `"${entry}" has an octet above ${OCTET_MAX}.`;
    }

    if (match[5] !== undefined) {
        const rangeEnd = Number(match[5]);

        if (rangeEnd > OCTET_MAX) {
            return `"${entry}" has a range end above ${OCTET_MAX}.`;
        }
        if (rangeEnd < octets[3]) {
            return `"${entry}" has a range end lower than its start.`;
        }
    }

    return "";
}

function validateField(name) {
    const raw = form.elements[name].value;
    let error = "";

    if (name === TARGET_FIELD) {
        const targets = parseTargets(raw);

        if (targets.length === 0) {
            error = "At least one target IP address is required.";
        } else {
            error = targets.map(validateTarget).find(Boolean) || "";
        }

    } else if (INT_RULES[name]) {
        const { min, label } = INT_RULES[name];
        const trimmed = raw.trim();
        const num = Number(trimmed);

        if (trimmed === "") {
            error = `${label} is required.`;
        } else if (!Number.isInteger(num)) {
            error = `${label} must be a whole number.`;
        } else if (num < min) {
            error = `${label} must be at least ${min}.`;
        }
    }

    setFieldError(name, error);
    return !error;
}

function validate() {
    // Run every check (no short-circuit) so all errors are displayed.
    return FIELDS.map(validateField).every(Boolean);
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------
function populate(settings) {
    FIELDS.forEach(name => {
        const value = settings[name];
        const input = form.elements[name];

        // The API may return the targets as a list or as a comma-separated string.
        input.value = Array.isArray(value)
            ? value.join(", ")
            : (value ?? "");

        input.disabled = false;
        setFieldError(name, "");
    });

    savedValues = currentValues();
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
    const values = currentValues();
    const body = new URLSearchParams(values);

    saveBtn.disabled = true;
    resetBtn.disabled = true;

    try {
        const response = await fetch("/api/settings", { method: "POST", body });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        // Show the cleaned-up value (e.g. stray quotes / spaces removed).
        FIELDS.forEach(name => {
            if (name === TARGET_FIELD) {
                form.elements[name].value = values[name].split(",").join(", ");
                console.log(form.elements[name].value);
            }
        });

        savedValues = values;
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

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------
FIELDS.forEach(name => {
    form.elements[name].addEventListener("input", () => {
        setFieldError(name, "");
        updateButtons();
    });
});

form.addEventListener("submit", saveSettings);
resetBtn.addEventListener("click", resetForm);

loadSettings();

// variables
const local_ip = document.getElementById("local_ip");
const ping_result = document.getElementById("ping_result");
const result_helper = document.getElementById("result_helper");
const scan_result_title = document.getElementById("scan_result_title");
const scan_ip_btn = document.getElementById("scan_ip_btn");
const settings_div = document.getElementById("settings_div");
const settings_btn = document.getElementById("settings_btn");
const settings_save_btn = document.getElementById("settings_save_btn");
const known_ip = document.getElementById("known_ip");
const log_output = document.getElementById("log_output");
const socket = document.getElementById("socket");

async function get_local_IP() {
    const url = "/api/localip";
    const response = await fetch(url);
    const data = await response.text();
    local_ip.textContent = data;
}

get_local_IP();

async function scan_ip_range() {
    await update_helper(1);
    const url = "/api/scan";
    const response = await fetch(url);
    const data = await response.text();
    // check the output for errors
    if (data.includes("Error")) {
        update_helper(2);
        return;
    }
    
    // if no result was found
    if (data.trim() == "") {
        update_helper(3)
        return
    }

    // prettify the result
    const data_split = data.split("ms");
    const remove_tailing_space = data_split.slice(0, -1);
    remove_tailing_space.forEach(element => {
        const div = document.createElement("div");
        div.textContent = element + " ms";
        ping_result.appendChild(div);
    });
    await update_helper(0)
}

async function update_helper(code) {
    // Text changing in the scan_ip_range function
    // didn't work, so this function was created for
    // this purpose
    if (code == 1) {
        result_helper.textContent = "Scanning..."
    }
    else if (code == 2) {
        result_helper.textContent = "Error occured. Check logs.txt for more info.";
    }
    else if (code == 3) {
        result_helper.textContent = "No result was found.";
    }
    else if (code == 0) {
        result_helper.textContent = "Scan finished.";
    }
}

async function open_config_settings() {
    // hide the scan UI and show the settings
    ping_result.classList.add("hidden");
    settings_div.classList.remove("hidden");
    settings_btn.classList.add("hidden");
    settings_save_btn.classList.remove("hidden");
    scan_ip_btn.classList.add("hidden");
    scan_result_title.textContent = "Configuration Settings:"

    // fetch current settings from the server and show in the settings menu
    const url = "/api/fetch-settings";
    const response = await fetch(url);
    const data = await response.text();
    const data_parsed = JSON.parse(data);
    
    const known_ip_list = data_parsed.known_ip;
    const log_output_value = data_parsed.log_output;
    const socket_value = data_parsed.socket;

    known_ip.textContent = known_ip_list;
    log_output.textContent = log_output_value;
    socket.textContent = socket_value;
}

async function save_config_settings(event) {
    event.preventDefault();

    // get inputs values
    const known_ip_list_input = document.getElementById("known_ip_list_input").value;
    const log_output_input = document.getElementById("log_output_input").value;
    const socket_value_input = document.getElementById("socket_value_input").value;
    
    // send a POST request to update the settings
    const url = "/api/upload-settings";
    const response = await fetch(url,{
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ known_ip_list_input, log_output_input, socket_value_input })
    });
    
    const settings_update_status = document.getElementById("settings_update_status");
    if (response.ok) {
        settings_update_status.textContent = "Settings Updated Successfully."
    } 
    else {
        settings_update_status.textContent = "Updating Settings Failed."
        settings_update_status.style.color = "tomato";
    }

    // show the scan UI and hide the settings
    ping_result.classList.remove("hidden");
    settings_div.classList.add("hidden");
    settings_btn.classList.remove("hidden");
    settings_save_btn.classList.add("hidden");
    scan_ip_btn.classList.remove("hidden");
    scan_result_title.textContent = "Scan Results:"
}
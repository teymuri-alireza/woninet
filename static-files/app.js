// variables
const local_ip = document.getElementById("local_ip");
const ping_result = document.getElementById("ping_result");
const result_helper = document.getElementById("result_helper");
const scan_result_title = document.getElementById("scan_result_title");
const scan_ip_btn = document.getElementById("scan_ip_btn");

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

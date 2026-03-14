async function get_local_IP() {
    const local_ip = document.getElementById("local_ip");
    const url = "/api/localip";
    const response = await fetch(url);
    const data = await response.text();
    local_ip.textContent = data;
}

get_local_IP();

async function scan_ip_range() {
    await update_helper(1);
    const ping_result = document.getElementById("ping_result");
    const url = "/api/scan";
    const response = await fetch(url);
    const data = await response.text();
    // check the output for errors
    if (data.includes("Error")) {
        update_helper(2);
        return;
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
    // Text updating in the scan_ip_range function
    // didn't work, so another function was created for
    // this purpose
    const result_helper = document.getElementById("result_helper");
    if (code == 1) {
        result_helper.textContent = "Scanning..."
    }
    else if (code == 2) {
        result_helper.textContent = "Error occured. Check logs.txt for more info.";
    }
    else if (code == 0) {
        result_helper.textContent = "Scan finished.";
    }
}

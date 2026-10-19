import json


def update_config_json(config_json_path: str, max_workers: int | None, arp_noise_limit: float | None) -> None:
    """
    Update and the supplied configuration values and write in the configuration file.

    Args:
        config_json_path: Path where the configuration JSON will be written.
        max_workers (int | None): Maximum number of worker threads, or
            `None` to leave the current value unchanged.
        arp_noise_limit (float | None): ARP noise limit, or `None` to
            leave the current value unchanged.
    """
    with open(config_json_path, "r") as file:
        config_file = json.load(file)

    if max_workers is not None:
        config_file["monitoring"]["max_workers"] = int(max_workers)
    if arp_noise_limit is not None:
        config_file["monitoring"]["arp_noise_limit"] = float(arp_noise_limit)

    with open(config_json_path, "w") as file:
        json.dump(config_file, file, indent=4)

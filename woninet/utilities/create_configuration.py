import json


def create_config_json(config_json_path: str) -> None:
    """
    Create a default configuration JSON file.

    Args:
        config_json_path: Path where the configuration JSON will be written.

    The function writes a default configuration template containing monitoring
    settings, database file name, target IP list, and alert rules.
    """
    # fmt: off
    template = {
        "monitoring": {
            "arp_noise_limit": 300.0,
            "max_workers": 4
        },
        "database": "woninet.db",
        "target_ip_list": [],
        "alert_rules":[
            {
                "metric": "latency",
                "threshold": 100,
                "consecutive_checks": 3
            },
            {
                "metric": "packet_loss",
                "threshold": 0.0,
                "consecutive_checks": 1
            }
        ]
    }
    # fmt: on

    with open(config_json_path, "w") as file:
        json.dump(template, file, indent=4)

# pymonitor

A local network inspecter and monitoring system written in python3.

**Note: This script requires sudo privileges.**

# Features

- Detailed logs both on stdout and file output (logs.txt).
- Supports both CLI mode and server mode.

# Future Plans

- Define known IP addresses list to alert if new IP was found.

# Known Issues

- Ping takes 2 minutes for all IP addresses, use threads.
- Add a warning to warn the user if the log file exceeded a certain size; The warning should be sent to the front-end.

# How To Run

1. Clone the repo.
2. Create a python virtual envirenment and activate it.
3. Type these commands in the terminal:

```shell
pip3 install -r requirements.txt
sudo python3 main.py --help
```

# Contribution

Contributions are welcome. If you have a new feature in mind or have found a bug, please consider opening a pull request or an issue.
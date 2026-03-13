# pymonitor

A local network inspecter and monitoring system written in python3.

**Note: This script may require sudo privileges (for opening a server with http.server).**

**Note: This project is under maintenance.**

# Features

- Detailed logs both on stdout and file output (logs.txt).

# Known Issues

- Ping takes 2 minutes for all IP addresses, use threads.

# How To Run

1. Clone the repo.
2. Create a python vitual envirenment and activate it.
3. Type these commands in the terminal:

```shell
pip3 install -r requirements.txt
sudo python3 main.py
```

# Contribution

Contributions are welcome. If you have a new feature in mind or have found a bug, please consider opening a pull request or an issue.
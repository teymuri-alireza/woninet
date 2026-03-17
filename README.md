# pymonitor

A local network inspecter and monitoring system written in python3.

**Note: This script requires sudo privileges.**

# Features

- Detailed logs both on stdout and file output (logs.txt).
- Supports both CLI mode and server mode.
- Configuration settings for IP list and log output.
- Simple build.sh file for easier set up/

# Known Issues

- Ping takes 2 minutes for all IP addresses, use threads.
- Add a warning to warn the user if the log file exceeded a certain size; The warning should be sent to the front-end.

# How To Run

1. Clone the repo.

## Run from the repo

2. Create a python virtual envirenment and activate it.
3. Type these commands in the terminal:

```shell
pip3 install -r requirements.txt
sudo python3 main.py --help
```

## Use build.sh

Use `sudo ./build.sh`. This script copy files into
`/usr/local/lib/.pymonitor` and create a command at `/usr/local/bin/pymonitor`.

**Note: `Build.sh` only works if required modules are installed globally. To activate the `build.sh` in a pyhton envirenment, you may want to edit `/usr/local/bin/pymonitor` file to use `/path/to/venv/bin/python3` isntead of `python3`**

```shell
sudo pymonitor -h
```

# Contribution

Contributions are welcome. If you have a new feature in mind or have found a bug, please consider opening a pull request or an issue.
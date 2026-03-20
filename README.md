# pymonitor

A local network inspecter and monitoring system written in python3.

**Note: This script requires sudo privileges.**

# Features

- Uses threads for faster scans.
- Supports both CLI mode and server mode.
- Detailed logs both on stdout and file output (logs.txt).
- Configuration settings for IP list, log output and socket address.
- Simple build.sh file for easier set up.

# Future Plans

- Add -w arg for showing warnings.
- Add index.html for documents and keep the changelog.

# Known Issues

- Add a warning to warn the user if the log file exceeded a certain size.
- Add timer for scan button in html file to show error if got no result after a specific time.
- Display help and version from arguments without root access.

# How To Run

- Clone the repo.

## Run using virtual

- Create a python virtual envirenment and activate it.
- Type these commands in the terminal:

```shell
pip3 install -r requirements.txt
sudo python3 main.py -V
```

## Use build.sh

- Use `sudo ./build.sh`. This script copy files into
`/usr/local/lib/.pymonitor` and create a command at `/usr/local/bin/pymonitor`.

**Note: `Build.sh` only works if required modules are installed globally. To activate the `build.sh` in a pyhton envirenment, you may want to edit `/usr/local/bin/pymonitor` file to use `/path/to/venv/bin/python3` isntead of `python3`**

```shell
sudo pymonitor --version
```

# Documentaion

if you have any question or confusion you check the [documentation](./documentation.md) guide.

# Contribution

Contributions are welcome. If you have a new feature in mind or have found a bug, please consider opening a pull request or an issue.

## What to contribute

You can make changes or open an issue in any part of the code. Such as:

- Scan logic
- server handling and monitoring
- CLI options
- Configuration settings
- Arguments and options
- Directory paths
- Texting and typo
- Wrong grammar or unjust documents
- etc
# pymonitor documentation

Read this file if you have any question or confusion about this program.

# Installation

## A. build.sh

This file create a directory at `/usr/local/lib/pymonitor` and copy main.py and utilities inside. Then create a command at `/usr/local/bin/pymonitor` which contains the script below:

```shell
#!/bin/sh

exec python3 /usr/local/lib/pymonitor/main.py \$@
```

## B. No Build

You can use the script without building with `sudo python3 main.py`

# Usage

Using the following command

```shell
sudo pymonitor
```
You can start monitoring the local network.

**Note**: Some of the options from version 0.8.0 are merged together in the version 2.0.0, such as monitoring and ping scan; And some options are removed, such as nmap scan and settings.

# Version

pymonitor uses Semantic version rules; Therefore after every breaking changes in the code logic there'll be a MAJOR bump. New functionality
and updates will bump one MINOR. Some changes in the UI and fixes will bump one PATCH.
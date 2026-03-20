# pymonitor documentation

Read this file if you have any question or confusion about this program.

# Installation

## A. build.sh

This section explaines the process that the `build.sh` script takes to build pymonitor:

**Note:** In the process of copying files, if any old file is found,
the script gives the following error: `Found files in {path}, use ./uninstall first`.

1. A directory will be created at `/usr/local/lib/.pymonitor` which will be used as the library and includes the files required to run the script.

2. Then a binary file will be created at `/usr/local/bin/pymonitor` which has the following content inside:

```shell
#!/bin/sh

exec python3 /usr/local/lib/.pymonitor/main.py $@
```

**Note:** this script is using python3 and will use the globally installed
moduels. If you're using a virtual envirenment, it's good practice to
change `python3` to `path/to/venv/bin/python3` to be able to use the
installed moduels.

3. In the end, using `chmod +x /usr/local/bin/pymonitor` the command will
be executable.

4. Finally you can verify the installtion using `sudo pymonitor --version`

## B. No Build

You can still use the script without building with `sudo python3 main.py`
but the library files will be created at `/usr/local/lib/.pymonitor`. Files such as:

- settings.json
- ip_list.txt
- ping_result.txt
- history.txt

# Usage

You can read the help from `pymonitor -h` to see the accepted arguments.
Also the description for each argument is written here:

## 1. **-s , --socket** 

- *Set socket for private IP determination; for the current scan only. (default: 8.8.8.8)*

pymonitor uses an IP address as a socket for private IP determination;
The default value is the famous `8.8.8.8` but you can change it using
```shell
sudo pymonitor -s 1.1.1.1
```

**Note:** This will change the socket IP for the current scan only, and the socket will be fetched from the settings for later scans. To change this value
permanently, check the `-c` argument.

## 2. **--serve** 

- *Serve the server instead of CLI mode*

pymonitor's default mode is the cli mode. If you'd rather see the
HTML file and run a server instead, use this option.

## 3. **-p , --port** 

- *Set port for the server. (default: 8000)*

Using this options you can set the port for your server. Notice this option
only make sense if used with --serve.

## 4. **-c , --config** 

- *Modify the configuration file and quit.*

You can access the configuration settings and change the following values
in the `settings.json` file:

- *Managing known IP list:* You can add or remove known IP addresses. Only the unknown IP addresses will be shown in the result.

- *Change socket value permanently:* As explained above, you can
change the value of socket in the `settings.json` with this option.

- *Show current settings*

**Note:** The config options is available form both CLI and server mode.

# Uninstallation

Using `sudo ./uninstall.sh`, you can remove any directory at `/usr/local/lib/.pymonitor` or any file at `/usr/local/bin/pymonitor`
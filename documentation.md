# pymonitor documentation

Read this file if you have any question or confusion about this program.

# Installation

## A. build.sh

In this section the process that the `build.sh` script takes to build the
scipt is explaind:

1. Any old directory or file will be removed first. There won't be any error if no old directory or file is found.

2. A directory will be created at `/usr/local/lib/.pymonitor` which will be used as the library and includes the files required to run the script.

3. Then a binary file will be created at `/usr/local/bin/pymonitor` which has the following content inside:

```shell
#!/bin/sh

exec python3 /usr/local/lib/.pymonitor/main.py $@
```

**Note:** this script is using python3 and will use the globally installed
moduels. If you're using a virtual envirenment, it's good practice to
change `python3` to `path/to/venv/bin/python3` to be able to use the
installed moduels.

4. In the end, using `chmod +x /usr/local/bin/pymonitor` the command will
be executable.

5. Finally you can verify the installtion using `sudo pymonitor --version`

## B. No Build

You can still use the script without building with `sudo python3 main.py`
but there might be 2 issues. First the library files will be created at `/usr/local/lib/.pymonitor`. Such as:

- ip_list.txt
- ping_result.txt
- history.txt
- logs.txt

And the index.html for serve option will be searched at `/usr/local/lib/.pymonitor/static-files/`

**Note:** We're aware that it's disturbing and will try to fix it in the next updates.

# Usage

You can read the help from `pymonitor -h` to see the accepted arguments.
We'll write the description for each argument here:

## 1. **-s , --socket** 

- *Set socket for private IP determination; for the current scan only. (default: 8.8.8.8)*

This script uses an IP address as a socket for private IP determination;
The default value is the famous `8.8.8.8` but you can change it using
```shell
sudo pymonitor -s 1.1.1.1
```

**Note:** This will change the socket IP for the current scan, and the socket will be fetch from the settings in later scans. To change this value
permanently, check the `-c` argument.

## 2. **--serve** 

- *Serve the server instead of CLI mode*

The default mode for this script is the cli mode. If you'd rather see the
HTML file and work with buttons and this kind of UI, use this option.

## 3. **-p , --port** 

- *Set port for the server. (default: 8000)*

Using this options you can set the port for your server. Notice this option
only make sense if used with --serve.

## 4. **-c , --config** 

- *Modify the configuration file and quit.*

You can access the configuration settings and change the following values
in the `settings.json` file:

- *Managing known IP list:* You can add or remove known IP addresses. Only the unknown IP addresses will be shown in the result.

- *Managing log output:* You can choose how you would see the logs. Options
`1` is for `stdout only`, `2` is for `file only` and `3` is for `stdout and
file`. Number `3` is the default value.

**Note:** Logs are an important part of the script. you should choose wisely.

- *Change socket value permanently:* As explained in the above, you can
change the value of socket in the `settings.json` with this option.

- *Show current settings*

**Note:** The config options is only available form the CLI interface.

# Uninstallation

using `sudo ./uninstall.sh` you can remove any directory at `/usr/local/lib/.pymonitor` or any file at `/usr/local/bin/pymonitor`
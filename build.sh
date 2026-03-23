#!/bin/bash

echo "This script moves the required files into /usr/local/lib/pymonitor"
echo "And create a command at /usr/local/bin/pymonitor"

if [[ $USER != "root" ]]; then
    echo "$0 requires root access."
    exit 1
fi

echo

# define variables for paths
LIB_PATH=/usr/local/lib
TOOL_PATH="${LIB_PATH}/.pymonitor"

# create directory
if [ ! -d $TOOL_PATH ]; then
    echo "Creating .pymonitor at $TOOL_PATH"
    mkdir $TOOL_PATH
else
    echo "Found the script's directory at $TOOL_PATH"
fi

# copy major files, if they don't exist
if [ ! -f "$TOOL_PATH/main.py" ] && [ ! -f "$TOOL_PATH/scan.py" ] && [ ! -f "$TOOL_PATH/serve.py" ]; then
    echo "copying main.py scan.py serve.py"
    cp main.py scan.py serve.py $TOOL_PATH/
else
    echo "Found files in $TOOL_PATH, use ./uninstall first."
    exit 1
fi

# copy the utilities directory and files, if they don't exist
if [ ! -d "$TOOL_PATH/utilities" ] && [ ! -f "$TOOL_PATH/utilities/arguments.py" ] && [ ! -f "$TOOL_PATH/utilities/logger.py" ] && [ ! -f "$TOOL_PATH/utilities/version.py" ]; then
    echo "copying utilities files"
    mkdir $TOOL_PATH/utilities
    cp utilities/* $TOOL_PATH/utilities/
else
    echo "Found files in $TOOL_PATH/utilities, use ./uninstall first."
    exit 1
fi

# copy the static files for server, if they don't exist
if [ ! -d "$TOOL_PATH/static-files" ] && [ ! -f "$TOOL_PATH/static-files/index.html" ] && [ ! -f "$TOOL_PATH/static-files/app.js" ] && [ ! -f "$TOOL_PATH/static-files/style.css" ]; then
    echo "copying static files"
    mkdir $TOOL_PATH/static-files
    cp static-files/* $TOOL_PATH/static-files
else
    echo "Found files in $TOOL_PATH/static-files, use ./uninstall first."
    exit 1
fi

echo "Adding command in /usr/local/bin/"

echo -e "#!/bin/sh\n\nexec python3 /usr/local/lib/pymonitor/main.py \$@" > /usr/local/bin/pymonitor

chmod +x /usr/local/bin/pymonitor

echo "done. verify with: pymonitor -h"
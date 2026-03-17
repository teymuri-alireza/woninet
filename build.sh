#!/bin/bash

echo "This script move required files into /usr/local/lib/.pymonitor"
echo "And create a command at /usr/local/bin/pymonitor"

if [[ $USER != "root" ]]; then
    echo "$0 requires root access."
    exit 1
fi

LIB_PATH=/usr/local/lib
TOOL_PATH="${LIB_PATH}/.pymonitor"

if [ ! -d $TOOL_PATH ]; then
    echo "Creating .pymonitor at $TOOL_PATH"
    mkdir $TOOL_PATH
else
    echo "Found the script's directory at $TOOL_PATH"
fi

if [ ! -f "$TOOL_PATH/main.py" ]; then
    echo "Copying files into $TOOL_PATH"
    cp main.py scan.py serve.py $TOOL_PATH/
    mkdir $TOOL_PATH/utilities
    cp utilities/* $TOOL_PATH/utilities/
else
    echo "Found files in $TOOL_PATH"
fi

echo "Adding command in /usr/local/bin/"

echo -e "#!/bin/sh\n\nexec python3 /usr/local/lib/.pymonitor/main.py \$@" > /usr/local/bin/pymonitor

chmod +x /usr/local/bin/pymonitor

echo "done. verify with: pymonitor -h"
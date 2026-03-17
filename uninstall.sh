#!/bin/bash

echo "This script removes all pymonitor files."

if [[ $USER != "root" ]]; then
    echo "$0 requires root access."
    exit 1
fi

if [ -d "/usr/local/lib/.pymonitor" ]; then
    echo "Removing library files at /usr/local/lib/.pymonitor"
    rm -rf /usr/local/lib/.pymonitor/
else
    echo "Library directory not found: /usr/local/lib/.pymonitor"
fi

if [ -f "/usr/local/bin/pymonitor" ]; then
    echo "Removing binary file at /usr/local/bin/pymonitor"
    rm /usr/local/bin/pymonitor
else
    echo "Binary file not found: /usr/local/bin/pymonitor"
fi
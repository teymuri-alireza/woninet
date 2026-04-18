#!/bin/bash

if [[ $USER != "root" ]]; then
    echo "$0 requires root access."
    exit 1
fi

# define variables for paths
LIB_PATH=/usr/local/lib/woninet
BIN_PATH=/usr/local/bin/

# create directory
if [ ! -d $LIB_PATH ]; then
    echo "Creating woninet at $LIB_PATH"
    mkdir $LIB_PATH
else
    echo "$LIB_PATH exists. Remove $LIB_PATH and $BIN_PATH/woninet then try again."
    exit 1
fi

# copy main.py
if [ ! -f "$LIB_PATH/main.py" ]; then
    echo "copying main.py"
    cp main.py $LIB_PATH/
else
    echo "Found main.py in $LIB_PATH, Remove $LIB_PATH and $BIN_PATH/woninet then try again."
    exit 1
fi

# copy the utilities directory and files
if [ ! -d "$LIB_PATH/utilities" ] && [ ! -f "$LIB_PATH/utilities/arguments.py" ] && [ ! -f "$LIB_PATH/utilities/logger.py" ] && [ ! -f "$LIB_PATH/utilities/version.py" ]; then
    echo "copying utilities files"
    mkdir $LIB_PATH/utilities
    cp utilities/* $LIB_PATH/utilities/
else
    echo "Found files in $LIB_PATH/utilities, Remove $LIB_PATH and $BIN_PATH/woninet then try again."
    exit 1
fi

# # copy the static files for server, if they don't exist
# if [ ! -d "$LIB_PATH/static-files" ] && [ ! -f "$LIB_PATH/static-files/index.html" ] && [ ! -f "$LIB_PATH/static-files/app.js" ] && [ ! -f "$LIB_PATH/static-files/style.css" ]; then
#     echo "copying static files"
#     mkdir $LIB_PATH/static-files
#     cp static-files/* $LIB_PATH/static-files
# else
#     echo "Found files in $LIB_PATH/static-files, use ./uninstall first."
#     exit 1
# fi

echo "Adding command in $BIN_PATH"

echo -e "#!/bin/sh\n\nexec python3 /usr/local/lib/woninet/main.py \$@" > $BIN_PATH/woninet

chmod +x $BIN_PATH/woninet

echo "done. verify with: woninet -V"
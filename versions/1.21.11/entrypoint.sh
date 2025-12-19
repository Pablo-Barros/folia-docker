#!/bin/bash

# Change to the data directory where server files should be
cd /data

# Handle EULA agreement
if [ "${MINECRAFT_EULA}" = "true" ]; then
    echo "eula=true" > eula.txt
fi

while [ true ]; do
    java -Xms${MIN_RAM} -Xmx${MAX_RAM} ${JAVA_FLAGS} -jar /endkind/server.jar ${FOLIA_FLAGS}

    echo Server restarting...
    echo Press CTRL + C to stop.
done
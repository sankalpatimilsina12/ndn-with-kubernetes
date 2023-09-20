#!/bin/bash

# Start the nfd service in the background
nfd --config $CONFIG > $LOG_FILE 2>&1 &

# Wait for nfd to start
sleep 5

# Execute the provided command (or fallback to /bin/bash if none provided)
exec "$@"

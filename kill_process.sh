#!/bin/bash

# Check if the script was provided with at least one argument (the process name to kill)
if [ $# -eq 0 ]; then
    echo "Usage: $0 <process_name>"
    exit 1
fi

# Store the process name provided as an argument
process_name="$1"

# Use pgrep to find the process ID(s) matching the provided name
process_ids=$(pgrep -f "$process_name")

# Check if any processes were found
if [ -z "$process_ids" ]; then
    echo "No processes found matching '$process_name'."
else
    echo "Killing process(es) with name '$process_name':"
    # Loop through each process ID and kill it
    for pid in $process_ids; do
        echo "Killing process $pid"
        kill -9 $pid
    done
fi
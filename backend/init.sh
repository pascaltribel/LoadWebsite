#!/bin/bash
# init.sh

# Exit on error
set -e

ls data

# Run database initialization script
python csv_to_db.py

# Run simulator to populate initial data
# Note: The simulator runs in a loop, so we'll run it in the background
# and then kill it after a few seconds to ensure some data is populated.
python simulator.py &
SIMULATOR_PID=$!

# Wait for a few seconds to allow the simulator to populate some data
sleep 15

# Kill the simulator process
kill $SIMULATOR_PID

echo "Database initialized and populated with initial data." 
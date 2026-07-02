#!/bin/zsh
# Prod-like runner for the Plotter App using gunicorn.
#
# This is the command you should be able to run both locally and when you SSH
# into your Render box (adjusting the port if needed).
#
# Local (for LAN testing):
#   ./start_gunicorn.sh
#
# On remote box (typical):
#   pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 PlotterApp:app
#
# On Render the platform usually provides $PORT and you set the Start Command
# or use a Procfile with:
#   web: pipenv run gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 PlotterApp:app

cd "$(dirname "$0")"

echo "Starting with gunicorn (prod-like, binds 0.0.0.0:5000)"
echo "Command: pipenv run gunicorn --bind 0.0.0.0:5000 --workers 1 --threads 4 PlotterApp:app"
echo ""
echo "After it starts, run ./whitelist_current.sh (while it's listening) to make sure"
echo "macOS firewall allows the exact binaries for LAN access."
echo ""

pipenv run gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app

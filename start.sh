# This file is executed as-is on Render (prod).
# It is the canonical way the app is started on the box after deploy/SSH.
#
# Production-grade gunicorn for The Internet Party platform.
#
# Locally for dev (mac firewall friendly + persistent network access):
#   ./start_local_with_node_relay.sh
# (Uses Node relay on 5000 + gunicorn internal. Firewall ON, no whitelist needed.)

export DATA_FOLDER=${DATA_FOLDER:-/data}

# Production-grade app server (gunicorn)
# Binds to $PORT if set by Render (falls back to 5000).
PORT=${PORT:-5000}
pipenv run gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app > grapher.log 2>&1 &

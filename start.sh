# PRODUCTION ONLY.
# This file is executed as-is on Render (prod) as the service start command.
#
# Production-grade gunicorn for The Internet Party platform.
# Runs in the FOREGROUND (required: Render supervises this process; if it
# backgrounds and the shell exits, the service is considered crashed).
# Logs go to stdout/stderr so they appear in the Render log stream.
#
# DO NOT USE LOCALLY on macOS.
# For local dev (mac firewall friendly + persistent network access) use:
#   ./start_local_with_node_relay.sh
# (Uses Node relay on 5000 + gunicorn internal. Firewall ON, no whitelist needed.)
#
# If you SSH to a box and want it detached, run: nohup ./start.sh &
#
# Tunables (all optional):
#   PORT              - bind port (Render sets this)
#   WEB_CONCURRENCY   - gunicorn workers   (default 2)
#   GUNICORN_THREADS  - threads per worker (default 8; requests are RTDB I/O-bound)
#   GUNICORN_TIMEOUT  - worker timeout sec (default 60)
#   SECRET_KEY        - Flask session key  (recommended; stable fallback exists)
#   DATA_FOLDER       - directory containing the Firebase admin JSON

export DATA_FOLDER=${DATA_FOLDER:-/data/}

# Helpful visibility in Render logs (especially during first deploys)
echo "DATA_FOLDER=$DATA_FOLDER"
CERT_PATH="${DATA_FOLDER%/}/theinternetparty-5b902-firebase-adminsdk-qlzzx-3864b82b40.json"
echo "Looking for Firebase cert at: $CERT_PATH"

PORT=${PORT:-5000}
WORKERS=${WEB_CONCURRENCY:-2}
THREADS=${GUNICORN_THREADS:-8}
TIMEOUT=${GUNICORN_TIMEOUT:-60}

exec pipenv run gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers $WORKERS \
  --threads $THREADS \
  --worker-class gthread \
  --timeout $TIMEOUT \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app

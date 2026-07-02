# This file is executed as-is on Render (prod).
# It is the canonical way the app is started on the box after deploy/SSH.
#
# NOTE: The old raw "python PlotterApp.py" was the Flask dev server (NOT production grade).
# We switched the app part to gunicorn below for real production use.
# The monitor is still backgrounded the same way.
#
# Locally for dev (mac firewall friendly + persistent network access):
#   ./start_local_with_node_relay.sh
# (Uses Node relay on 5000 + gunicorn internal. Firewall ON, no whitelist needed.)

export DATA_FOLDER=${DATA_FOLDER:-/data}

./kill_process.sh PresidentMonitor.py
python PresidentMonitor.py -s al,ak,az,ar,ca,co,ct,de,fl,ga,hi,id,il,in,ia,ks,ky,la,me,md,ma,mi,mn,ms,mo,mt,ne,nv,nh,nj,nm,ny,nc,nd,oh,ok,or,pa,ri,sc,sd,tn,tx,ut,vt,va,wa,wv,wi,wy > monitor.log &

# Production-grade app server (gunicorn instead of dev server)
# Binds to $PORT if set by Render (falls back to 5000).
# Matches what you would run after SSH on the box.
PORT=${PORT:-5000}
pipenv run gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --access-logfile - \
  --error-logfile - \
  PlotterApp:app > grapher.log 2>&1 &

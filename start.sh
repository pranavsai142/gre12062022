./kill_process.sh PresidentMonitor.py
python PresidentMonitor.py -s co,ga,il,az,pa,ri > monitor.log &
python PlotterApp.py > grapher.log
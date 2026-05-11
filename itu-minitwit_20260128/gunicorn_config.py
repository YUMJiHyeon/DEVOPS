import os
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

def when_ready(_server):
    GunicornInternalPrometheusMetrics.start_http_server_when_ready(9090)

def child_exit(_server, worker):
    GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)
bind = "0.0.0.0:5000"
workers = 4
timeout = 120

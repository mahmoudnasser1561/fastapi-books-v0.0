from prometheus_client import Gauge, start_http_server
import json
import time
import os

# Prometheus metrics
requests_per_sec = Gauge("ab_requests_per_sec", "Requests per second from AB")
time_per_request = Gauge("ab_time_per_request_ms", "Average time per request (ms)")
transfer_rate = Gauge("ab_transfer_rate_kb", "Transfer rate (KB/s)")
failed_requests = Gauge("ab_failed_requests", "Number of failed requests")
complete_requests = Gauge("ab_complete_requests", "Number of completed requests")

def load_latest_result():
    try:
        with open("/app/ab_results/ab_summary.json") as f: 
            data = json.load(f)
        if not data:
            return None
        return sorted(data, key=lambda x: x["file"], reverse=True)[0]
    except Exception as e:
        print(f"Error loading results: {e}")
        return None

def update_metrics():
    result = load_latest_result()
    if not result:
        print("No results found yet.")
        return
    requests_per_sec.set(result.get("requests_per_sec", 0))
    time_per_request.set(result.get("time_per_request", 0))
    transfer_rate.set(result.get("transfer_rate", 0))
    failed_requests.set(result.get("failed_requests", 0))
    complete_requests.set(result.get("complete_requests", 0))

if __name__ == "__main__":
    start_http_server(9100) 
    print("AB Metrics Exporter running on port 9100")
    while True:
        update_metrics()
        time.sleep(15)
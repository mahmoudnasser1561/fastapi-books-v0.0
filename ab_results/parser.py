import re
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = BASE_DIR
OUTPUT_JSON = os.path.join(BASE_DIR, "ab_summary.json")

def parse_ab_output(text):
    data = {}
    patterns = {
        "requests_per_sec": r"Requests per second:\s+([\d\.]+)",
        "time_per_request": r"Time per request:\s+([\d\.]+)\s+\[ms\]\s+\(mean\)",
        "transfer_rate": r"Transfer rate:\s+([\d\.]+)\s+\[Kbytes/sec\]",
        "complete_requests": r"Complete requests:\s+(\d+)",
        "failed_requests": r"Failed requests:\s+(\d+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            data[key] = float(match.group(1))
    return data

def main():
    summaries = []
    for file in os.listdir(RESULTS_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(RESULTS_DIR, file)) as f:
                text = f.read()
                summary = parse_ab_output(text)
                summary["file"] = file
                summaries.append(summary)

    with open(OUTPUT_JSON, "w") as out:
        json.dump(summaries, out, indent=2)

    print(f"Parsed {len(summaries)} AB result files → {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

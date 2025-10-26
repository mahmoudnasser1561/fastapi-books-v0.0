import requests
from collections import Counter

URL = "http://localhost:8080/"
N = 100

results = Counter()
for i in range(N):
    try:
        r = requests.get(URL, timeout=2)
        backend = r.headers.get("x-served-by", "unknown")
        results[backend] += 1
    except Exception as e:
        print(f"Request {i+1} failed: {e}")


print(f"\nSent {N} requests total.\n")
for server, count in results.items():
    print(f"{server}: {count} responses")


print("\nSummary:")
print(results)
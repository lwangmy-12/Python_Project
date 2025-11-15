import requests

print("Testing docs...")
print(requests.get("http://127.0.0.1:8000/docs").status_code)

print("Testing example routes...")

print("/api/bridge/000000000000001 ->",
      requests.get("http://127.0.0.1:8000/api/bridge/000000000000001").status_code)

print("/api/bridges/year/2025 ->",
      requests.get("http://127.0.0.1:8000/api/bridges/year/2025").status_code)

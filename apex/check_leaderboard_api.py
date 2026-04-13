import requests

# Try common leaderboard API endpoints
urls = [
    "https://lablab.ai/api/hackathon/leaderboard",
    "https://lablab.ai/api/leaderboard",
    "https://api.lablab.ai/leaderboard",
    "https://api.lablab.ai/hackathon/leaderboard",
]

headers = {"User-Agent": "Mozilla/5.0"}

print("=" * 80)
print("STEP 1: Checking hackathon leaderboard API")
print("=" * 80)

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"{url}: {r.status_code}")
        if r.status_code == 200:
            print(r.text[:500])
    except Exception as e:
        print(f"{url}: {e}")

print("\n" + "=" * 80)

"""
universe_collect.py — Collect ALL Egyptian Exchange (EGX) stocks from EODHD.
No price filter. Exchange code: CA (Cairo).
"""
import os, csv, time, requests

HERE = os.path.dirname(os.path.abspath(__file__))

def load_key():
    key = os.environ.get("EODHD_API_KEY", "")
    if key:
        return key
    env_path = os.path.join(HERE, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("EODHD_API_KEY"):
                    return line.strip().split("=", 1)[1]
    raise RuntimeError("EODHD_API_KEY not found")

KEY = load_key()

def collect_universe(out_path=None):
    if out_path is None:
        out_path = os.path.join(HERE, "universe.csv")

    url = "https://eodhd.com/api/screener"
    all_tickers = []
    offset = 0
    limit  = 100

    print("Fetching EGX universe (no price filter)...")
    while True:
        params = {
            "api_token": KEY,
            "fmt": "json",
            "filters": '[["exchange","=","EGX"]]',
            "limit": limit,
            "offset": offset,
            "sort": "market_capitalization.desc"
        }
        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code != 200:
                print(f"  Screener error {r.status_code} at offset {offset}")
                break
            data = r.json().get("data", [])
            if not data:
                break
            all_tickers.extend(data)
            print(f"  Fetched {len(all_tickers)} stocks so far...")
            if len(data) < limit:
                break
            offset += limit
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error at offset {offset}: {e}")
            break

    print(f"Total EGX stocks found: {len(all_tickers)}")

    # Write CSV
    fieldnames = ["code", "name", "exchange", "currency_symbol",
                  "adjusted_close", "market_capitalization", "sector",
                  "industry", "avgvol_200d", "earnings_share", "dividend_yield"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(all_tickers)

    print(f"Saved to {out_path}")
    return all_tickers

if __name__ == "__main__":
    collect_universe()

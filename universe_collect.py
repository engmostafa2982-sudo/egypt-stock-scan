"""
universe_collect.py — Collect ALL Egyptian Exchange (EGX) stocks from EODHD.
Uses the exchange-symbol-list endpoint (reliable, no price filter needed).
Exchange code: EGX
"""
import os, csv, requests

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

    print("Fetching EGX universe from exchange-symbol-list...")
    url = "https://eodhd.com/api/exchange-symbol-list/EGX"
    try:
        r = requests.get(url, params={"api_token": KEY, "fmt": "json"}, timeout=30)
        if r.status_code != 200:
            print(f"  Error {r.status_code}: {r.text[:200]}")
            return []
        data = r.json()
        if not isinstance(data, list):
            print(f"  Unexpected response: {str(data)[:200]}")
            return []
    except Exception as e:
        print(f"  Request failed: {e}")
        return []

    # Filter to common stocks only
    stocks = [d for d in data if d.get('Type', '').lower() in ('common stock', 'stock', '')]
    if not stocks:
        stocks = data  # fallback: include all types

    print(f"Total EGX stocks found: {len(stocks)}")

    # Write CSV with columns expected by score_engine.py
    fieldnames = ["code", "name", "exchange", "currency_symbol",
                  "adjusted_close", "market_capitalization", "sector",
                  "industry", "avgvol_200d", "earnings_share", "dividend_yield"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for d in stocks:
            w.writerow({
                "code":                 d.get("Code", ""),
                "name":                 d.get("Name", ""),
                "exchange":             d.get("Exchange", "EGX"),
                "currency_symbol":      d.get("Currency", "EGP"),
                "adjusted_close":       "",
                "market_capitalization": "",
                "sector":               "",
                "industry":             "",
                "avgvol_200d":          "",
                "earnings_share":       "",
                "dividend_yield":       "",
            })

    print(f"Saved {len(stocks)} stocks to {out_path}")
    return stocks

if __name__ == "__main__":
    collect_universe()

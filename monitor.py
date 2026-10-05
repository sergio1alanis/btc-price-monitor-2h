import os
import statistics
from datetime import datetime, timezone

import requests

TIMEOUT = 15


def fetch_json(url, params=None):
    r = requests.get(url, params=params, timeout=TIMEOUT, headers={"User-Agent": "btc-price-monitor-2h/1.0"})
    r.raise_for_status()
    return r.json()


def sources():
    return [
        ("CoinGecko", "https://api.coingecko.com/api/v3/simple/price", {"ids": "bitcoin", "vs_currencies": "usd"}, lambda d: float(d["bitcoin"]["usd"])),
        ("Coinbase", "https://api.coinbase.com/v2/prices/BTC-USD/spot", None, lambda d: float(d["data"]["amount"])),
        ("Kraken", "https://api.kraken.com/0/public/Ticker", {"pair": "XBTUSD"}, lambda d: float(d["result"]["XXBTZUSD"]["c"][0])),
        ("Binance", "https://api.binance.com/api/v3/ticker/price", {"symbol": "BTCUSDT"}, lambda d: float(d["price"])),
        ("Bitstamp", "https://www.bitstamp.net/api/v2/ticker/btcusd/", None, lambda d: float(d["last"])),
        ("CryptoCompare", "https://min-api.cryptocompare.com/data/price", {"fsym": "BTC", "tsyms": "USD"}, lambda d: float(d["USD"])),
    ]


def main():
    valid = []
    failed = []
    for name, url, params, parser in sources():
        try:
            data = fetch_json(url, params)
            price = parser(data)
            if price > 0:
                valid.append((name, price))
            else:
                raise ValueError("non-positive price")
        except Exception as exc:
            failed.append((name, str(exc)))

    primary = [x for x in valid if x[0] in {"CoinGecko", "Coinbase", "Kraken", "Binance"}]
    backups = [x for x in valid if x[0] in {"Bitstamp", "CryptoCompare"}]
    # Prefer all four primary sources; if a primary fails, fill the missing slots with backups.
    selected = primary[:]
    for item in backups:
        if len(selected) >= 4:
            break
        selected.append(item)

    if len(selected) < 4:
        raise RuntimeError(f"Only {len(selected)} valid sources available; at least 4 are required. Failures: {failed}")

    prices = [p for _, p in selected]
    median = statistics.median(prices)
    low, high = min(prices), max(prices)
    spread_pct = ((high - low) / median) * 100
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "Bitcoin — reporte automático",
        f"Hora: {now}",
        f"Precio de referencia (mediana): ${median:,.2f} USD",
        f"Rango: ${low:,.2f} – ${high:,.2f} USD",
        f"Dispersión máxima: {spread_pct:.3f}%",
        "",
        "Fuentes utilizadas:",
    ]
    for name, price in selected:
        marker = " (respaldo)" if name in {"Bitstamp", "CryptoCompare"} else ""
        lines.append(f"- {name}{marker}: ${price:,.2f} USD")
    if failed:
        lines += ["", "Fuentes con fallo:"]
        lines += [f"- {name}: {error[:140]}" for name, error in failed]
    lines += ["", "Próxima ejecución programada: aproximadamente en 2 horas."]
    message = "\n".join(lines)

    # Composio sends are intentionally kept in the GitHub job through its API only when configured.
    # The actual notification layer is implemented in notify.py.
    from notify import send_notifications
    send_notifications(message)
    print(message)


if __name__ == "__main__":
    main()

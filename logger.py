import csv
from datetime import datetime

def log_trade(symbol, entry_price, stop_price, leverage, risk_ratio, profit=0, filename="risk_log.csv"):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            entry_price,
            stop_price,
            leverage,
            risk_ratio,
            profit
        ])

def log_paper_trade(symbol, entry_price, stop_price, leverage, risk_ratio, profit):
    import csv
    from datetime import datetime
    FILE = "paper_trade_log.csv"

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol,
            entry_price,
            stop_price,
            leverage,
            risk_ratio,
            profit
        ])
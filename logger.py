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
import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()

def get_open_positions():
    client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))
    positions = client.futures_position_information()
    return [
        {
            "symbol": p["symbol"],
            "entryPrice": float(p["entryPrice"]),
            "positionAmt": float(p["positionAmt"]),
            "leverage": int(p["leverage"])
        }
        for p in positions if abs(float(p["positionAmt"])) > 0
    ]
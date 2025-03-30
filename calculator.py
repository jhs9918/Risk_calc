def calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price):
    max_loss = total_asset * risk_ratio
    position_size = float(position_amt) * float(entry_price)
    stop_loss_pct = max_loss / (position_size * float(leverage))
    stop_loss_price = float(entry_price) * (1 - stop_loss_pct)

    return {
        "손절 가격": round(stop_loss_price, 2),
        "손절 기준 손실률 (%)": round(stop_loss_pct * 100, 2),
        "최대 손실 금액": int(max_loss)
    }
def calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price, direction="LONG"):
    risk_dollar = total_asset * risk_ratio
    price_diff = risk_dollar / (position_amt * leverage)

    if direction == "LONG":
        stop_price = entry_price - price_diff
    else:  # SHORT
        stop_price = entry_price + price_diff

    return {"손절 가격": round(stop_price, 6)}

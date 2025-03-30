import streamlit as st
import json
import os
import base64
from calculator import calculate_stop_loss_price
from asset_manager import get_paper_asset, update_paper_asset

# ✅ 최신 Binance USDT 선물 티커 (2025년 3월 기준, 수동 리스트)
futures_symbols = sorted([
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT",
    "TRXUSDT", "BCHUSDT", "XLMUSDT", "LINKUSDT", "ETCUSDT", "ATOMUSDT", "XMRUSDT", "ALGOUSDT", "VETUSDT", "ICPUSDT",
    "FILUSDT", "MKRUSDT", "AVAXUSDT", "AXSUSDT", "SANDUSDT", "EGLDUSDT", "AAVEUSDT", "KSMUSDT", "NEARUSDT", "GRTUSDT",
    "FTMUSDT", "1INCHUSDT", "CAKEUSDT", "HBARUSDT", "ENJUSDT", "MANAUSDT", "XTZUSDT", "ZECUSDT", "DASHUSDT", "COMPUSDT",
    "SNXUSDT", "YFIUSDT", "LRCUSDT", "ZENUSDT", "BATUSDT", "DGBUSDT", "ONTUSDT", "QTUMUSDT", "IOSTUSDT", "OMGUSDT",
    "NANOUSDT", "ICXUSDT", "STORJUSDT", "ZRXUSDT", "KNCUSDT", "SCUSDT", "ANKRUSDT", "CRVUSDT", "SUSHIUSDT", "BALUSDT",
    "CHZUSDT", "WAVESUSDT", "BANDUSDT", "RUNEUSDT", "LUNAUSDT", "COTIUSDT", "RSRUSDT", "OCEANUSDT", "REEFUSDT", "TWTUSDT",
    "ALPHAUSDT", "RLCUSDT", "DENTUSDT", "HOTUSDT", "MTLUSDT", "WRXUSDT", "STMXUSDT", "CELRUSDT", "ARPAUSDT", "CTSIUSDT",
    "PERLUSDT", "MDTUSDT", "DUSKUSDT", "CVCUSDT", "TOMOUSDT", "MITHUSDT", "WANUSDT", "FUNUSDT", "DOCKUSDT", "NKNUSDT",
    "BEAMUSDT", "VITEUSDT", "STPTUSDT", "MBLUSDT", "OGNUSDT", "DREPUSDT", "BELUSDT", "WINGUSDT", "SWRVUSDT", "CREAMUSDT",
    "UNIUSDT"
])

POSITIONS_FILE = "saved_positions.json"

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            return json.load(f)
    return []

def save_positions(data):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Streamlit 설정
st.set_page_config(page_title="📘 가상 리스크 계산기", layout="wide")
st.title("📘 Hadol’s 가상 리스크 계산기 (Paper Trading)")

total_asset = get_paper_asset()
st.sidebar.markdown(f"💰 **총 자산: ${total_asset:,.2f}**")

positions = load_positions()
selected_id = st.sidebar.selectbox("📂 저장된 계약 선택", ["새 계약 입력"] + [p["id"] for p in positions])

if selected_id == "새 계약 입력":
    st.subheader("🆕 새 계약 입력")
    symbol = st.selectbox("종목 선택 (자동완성)", options=futures_symbols, index=futures_symbols.index("BTCUSDT") if "BTCUSDT" in futures_symbols else 0)

    entry_price = st.number_input("진입 가격 ($)", value=27000.0, format="%.6f")
    leverage = st.number_input("레버리지", 1, 125, 10)
    direction = st.radio("포지션 방향", ["LONG", "SHORT"])
    position_usd = st.number_input("포지션 금액 ($)", value=500.0, format="%.2f")
    position_amt = position_usd / entry_price

    risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
    risk_result = calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price)
    suggested_stop = risk_result["손절 가격"]

    stop_price_method = st.radio("손절가 방식", ["자동", "직접"])
    if stop_price_method == "자동":
        stop_price = suggested_stop
    else:
        stop_price = st.number_input("직접 손절 가격 입력 ($)", value=suggested_stop, format="%.6f")
        loss_amt = (entry_price - stop_price) * position_amt if direction == "LONG" else (stop_price - entry_price) * position_amt
        risk_pct = (loss_amt / total_asset) * 100 if total_asset > 0 else 0
        st.info(f"⚠️ 손실 예상: ${loss_amt:.2f} → 자산 대비 {risk_pct:.2f}%")

    if st.button("💾 계약 저장"):
        new_id = f"{symbol}_{entry_price}_{position_usd}_{direction}"
        new_position = {
            "id": new_id,
            "symbol": symbol,
            "entry_price": entry_price,
            "leverage": leverage,
            "position_usd": position_usd,
            "position_amt": position_amt,
            "stop_price": stop_price,
            "direction": direction,
            "realized_profit": 0,
            "status": "open"
        }
        positions.append(new_position)
        save_positions(positions)
        st.success(f"✅ 계약 저장 완료: {new_id}")

# 이하: 기존 계약 열람 및 손절/익절/삭제 기능 동일 (생략 가능)

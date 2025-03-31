import streamlit as st
import json
import os
from calculator import calculate_stop_loss_price
from asset_manager import get_paper_asset, update_paper_asset
from github_uploader import commit_to_github

# ✅ 최신 Binance USDT 선물 티커 수동 리스트 (2025년 3월 기준)
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
    "BEAMUSDT", "VITEUSDT", "STPTUSDT", "MBLUSDT", "OGNUSDT", "DREPUSDT"
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

st.set_page_config(page_title="📘 가상 리스크 계산기", layout="wide")
st.title("📘 Hadol’s 가상 리스크 계산기 (Paper Trading)")

total_asset = get_paper_asset()
st.sidebar.markdown(f"💰 **총 자산: ${total_asset:,.2f}**")

positions = load_positions()
selected_id = st.sidebar.selectbox("📂 저장된 계약 선택", ["새 계약 입력"] + [p["id"] for p in positions])

# ---------------- 새 계약 입력 ----------------
if selected_id == "새 계약 입력":
    st.subheader("🆕 새 계약 입력")
    symbol = st.selectbox("종목 선택 (자동완성)", options=futures_symbols, 
                          index=futures_symbols.index("BTCUSDT") if "BTCUSDT" in futures_symbols else 0)
    entry_price = st.number_input("진입 가격 ($)", value=27000.0, format="%.6f")
    leverage = st.number_input("레버리지", 1, 125, 10)
    direction = st.radio("포지션 방향", ["LONG", "SHORT"])
    position_usd = st.number_input("포지션 금액 ($)", value=500.0, format="%.2f")
    position_amt = position_usd / entry_price

    risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
    risk_result = calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price, direction)
    suggested_stop = risk_result["손절 가격"]

    stop_price_method = st.radio("손절가 방식", ["자동", "직접"])
    if stop_price_method == "자동":
        stop_price = suggested_stop
    else:
        stop_price = st.number_input("직접 손절 가격 입력 ($)", value=suggested_stop, format="%.6f")
        if direction == "LONG":
            price_diff = entry_price - stop_price
        else:
            price_diff = stop_price - entry_price
        loss_amt = abs(price_diff * position_amt * leverage)
        risk_pct = (loss_amt / total_asset) * 100 if total_asset > 0 else 0
        st.info(f"⚠️ 예상 손실: ${loss_amt:,.2f} → 자산 대비 {risk_pct:.2f}%")

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

# ---------------- 기존 계약 조작 ----------------
else:
    selected = next(p for p in positions if p["id"] == selected_id)
    st.subheader(f"📄 계약: {selected['symbol']} ({selected.get('direction', 'LONG')})")
    st.write(f"💵 진입가: ${selected['entry_price']}, 레버리지: {selected['leverage']}배")
    st.write(f"📉 손절가: ${selected['stop_price']:.6f}, 포지션 금액: ${selected['position_usd']:.2f}")
    st.write(f"📌 상태: **{selected['status']}**")

    new_stop = st.number_input("✏️ 손절가 수정", value=selected["stop_price"], format="%.6f")
    if new_stop != selected["stop_price"]:
        selected["stop_price"] = new_stop
        save_positions(positions)
        st.success("🔁 손절가 수정 완료")

    st.subheader("✅ 익절 처리")
    pct = st.slider("청산 비율 (%)", 1, 100, 50)
    exit_price = st.number_input("익절 가격 ($)", value=selected["entry_price"], format="%.6f")

    if selected.get("direction", "LONG") == "LONG":
        total_profit_amt = (exit_price - selected["entry_price"]) * selected["position_amt"]
    else:
        total_profit_amt = (selected["entry_price"] - exit_price) * selected["position_amt"]

    profit_amt = total_profit_amt * (pct / 100)
    profit_pct = (abs(profit_amt) / total_asset) * 100 if total_asset > 0 else 0
    st.info(f"💹 이 익절가는 총 자산의 약 {profit_pct:.2f}% 수익에 해당합니다.")

    if st.button("💸 익절"):
        closed_fraction = pct / 100.0
        profit = total_profit_amt * closed_fraction
        # 부분 익절: 남은 포지션 계산
        if pct < 100:
            selected["position_amt"] = selected["position_amt"] * (1 - closed_fraction)
            selected["position_usd"] = selected["position_usd"] * (1 - closed_fraction)
            selected["status"] = "partial"
        else:
            selected["position_amt"] = 0
            selected["position_usd"] = 0
            selected["status"] = "closed"

        selected["realized_profit"] += profit
        new_asset = update_paper_asset(profit)
        save_positions(positions)
        st.success(f"🎉 익절 완료! 수익: ${profit:,.2f}, 총 자산: ${new_asset:,.2f}")
        if pct < 100:
            st.info(f"남은 포지션: {selected['position_amt']:.6f} 계약, 포지션 금액: ${selected['position_usd']:.2f}")
        save_positions(positions)
        commit_to_github()

    if st.button("🛑 손절 처리"):
        loss = -1 * selected["position_usd"]
        selected["realized_profit"] = loss
        selected["status"] = "stopped"
        new_asset = update_paper_asset(loss)
        save_positions(positions)
        st.error(f"💥 손절 완료! 손실: ${-loss:,.2f}, 총 자산: ${new_asset:,.2f}")
        save_positions(positions)
        commit_to_github()
    if st.button("🗑️ 계약 삭제"):
        positions = [p for p in positions if p["id"] != selected_id]
        save_positions(positions)
        st.success(f"🧹 계약 '{selected_id}' 삭제 완료!")
        st.experimental_rerun()

# ---------------- 백업 다운로드 ----------------
if os.path.exists(POSITIONS_FILE):
    with open(POSITIONS_FILE, "rb") as f:
        st.download_button("📥 계약 JSON 백업 다운로드", f, "saved_positions.json", mime="application/json")
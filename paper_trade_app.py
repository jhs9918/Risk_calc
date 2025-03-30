# paper_trade_app.py (가상매매 확장: 계약 저장, 손절/익절 처리 + JSON 다운로드)
import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from calculator import calculate_stop_loss_price
from asset_manager import get_paper_asset, update_paper_asset

POSITIONS_FILE = "saved_positions.json"

st.set_page_config(
    page_title="Hadol’s 가상 리스크 계산기",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📘 Hadol’s 가상 리스크 계산기 (Paper Trading)")

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            return json.load(f)
    return []

def save_positions(data):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

total_asset = get_paper_asset()
st.sidebar.subheader(f"💰 가상 총 자산: ${total_asset:,}")

positions = load_positions()
position_options = [f"{p['symbol']} | {p['id']}" for p in positions if p["status"] == "open"]
selected_pos = st.sidebar.selectbox("📄 계약 선택", options=["새 계약 생성"] + position_options)

if selected_pos == "새 계약 생성":
    st.subheader("📝 새 계약 생성")
    symbol = st.text_input("종목 티커", value="BTCUSDT")
    entry_price = st.number_input("진입 가격 ($)", value=27000.0)
    leverage = st.number_input("레버리지", min_value=1, max_value=125, value=10)
    position_usd = st.number_input("포지션 금액 ($)", value=500.0)
    position_amt = position_usd / entry_price if entry_price > 0 else 0
    risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
    stop_result = calculate_stop_loss_price(total_asset, position_amt, leverage, risk_ratio, entry_price)
    stop_price = stop_result["손절 가격"]

    if st.button("💾 계약 저장"):
        new_contract = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "symbol": symbol,
            "entry_price": entry_price,
            "leverage": leverage,
            "position_usd": position_usd,
            "position_amt": position_amt,
            "stop_price": stop_price,
            "status": "open",
            "realized_profit": 0.0,
            "partial_closes": []
        }
        positions.append(new_contract)
        save_positions(positions)
        st.success("계약이 저장되었습니다. 사이드바에서 선택할 수 있어요.")
else:
    selected_id = selected_pos.split("|")[1].strip()
    contract = next(p for p in positions if p["id"] == selected_id)

    st.subheader(f"📄 계약 정보: {contract['symbol']} ({contract['id']})")
    st.write(f"진입가: ${contract['entry_price']}, 레버리지: {contract['leverage']}배, 포지션 금액: ${contract['position_usd']}")

    # 손절가 수정
    new_stop = st.number_input("🔧 손절 가격 수정 ($)", value=contract["stop_price"])
    if new_stop != contract["stop_price"]:
        contract["stop_price"] = new_stop
        save_positions(positions)
        st.info("손절 가격이 수정되었습니다.")

    # 익절 처리
    with st.expander("📈 익절 처리"):
        pct = st.slider("익절 비율 (%)", 1, 100, 50)
        exit_price = st.number_input("익절한 가격 ($)", value=contract["entry_price"] * 1.03)
        if st.button("익절 반영"):
            portion = pct / 100
            profit = (exit_price - contract["entry_price"]) * contract["position_amt"] * portion
            contract["partial_closes"].append({"pct": pct, "price": exit_price, "profit": profit})
            contract["realized_profit"] += profit
            updated_asset = update_paper_asset(profit)
            save_positions(positions)
            st.success(f"익절로 ${profit:.2f} 이익을 실현했습니다. 자산: ${updated_asset:,.2f}")

    # 손절 처리
    with st.expander("📉 손절 처리"):
        if st.button("이 계약 손절 처리"):
            loss = (contract["stop_price"] - contract["entry_price"]) * contract["position_amt"]
            contract["status"] = "stopped"
            contract["realized_profit"] = loss
            updated_asset = update_paper_asset(loss)
            save_positions(positions)
            st.error(f"손절 처리 완료. 손실: ${loss:.2f}, 자산: ${updated_asset:,.2f}")

# 계약 전체 테이블 출력
with st.expander("📋 전체 계약 내역"):
    if positions:
        df = pd.DataFrame(positions)
        st.dataframe(df[["id", "symbol", "entry_price", "stop_price", "position_usd", "realized_profit", "status"]])
    else:
        st.info("저장된 계약이 없습니다.")

# JSON 다운로드 버튼
if os.path.exists(POSITIONS_FILE):
    with open(POSITIONS_FILE, "rb") as f:
        st.download_button(
            label="📥 계약 JSON 백업 다운로드",
            data=f,
            file_name="saved_positions.json",
            mime="application/json"
        )
# app.py (달러 버전)
import streamlit as st
from calculator import calculate_stop_loss_price
from logger import log_trade
from asset_manager import get_total_asset, update_total_asset
from binance_client import get_open_positions

st.set_page_config(
    page_title="투자 리스크 계산기",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Noto Sans KR', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.title("Hadol_s Risk Manager")

total_asset = get_total_asset()
st.sidebar.subheader(f"💰 총 자산: ${total_asset:,}")

positions = get_open_positions()
symbols = [p["symbol"] for p in positions]
selected = st.selectbox("포지션 선택", options=symbols)

selected_position = next(p for p in positions if p["symbol"] == selected)
entry_price = selected_position["entryPrice"]
leverage = selected_position["leverage"]

st.write(f"진입 가격: ${entry_price}, 레버리지: {leverage}배")

risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
risk_result = calculate_stop_loss_price(
    total_asset, selected_position["positionAmt"], leverage, risk_ratio, entry_price
)
suggested_stop = risk_result["손절 가격"]

use_auto = st.radio("리스크 기준 손절가 사용?", ["예", "아니오"])

if use_auto == "아니오":
    manual_type = st.radio("직접 입력 방식", ["퍼센트", "가격"])
    if manual_type == "퍼센트":
        pct = st.number_input("손절 퍼센트 (%)", value=3.0)
        stop_price = entry_price * (1 - pct / 100)
    else:
        stop_price = st.number_input("직접 손절 가격 입력 ($)", value=suggested_stop)
else:
    stop_price = suggested_stop

st.write(f"최종 손절 가격: ${stop_price:.2f}")

col1, col2, col3 = st.columns(3)
col1.metric("손절 가격", f"${stop_price:,.2f}")
col2.metric("리스크 비율", f"{risk_ratio*100:.2f}%")
col3.metric("총 자산", f"${total_asset:,}")

with st.expander("익절 처리"):
    profit = st.number_input("익절 금액 ($)", value=0.0)
    if profit > 0:
        percent_closed = st.slider("청산 비율 (%)", 1, 100, 50)
        realized = profit * (percent_closed / 100)
        new_asset = update_total_asset(realized)
        st.success(f"자산이 ${realized:,.2f} 증가하여 총 자산은 ${new_asset:,.2f}가 되었습니다.")
        trailing_stop = st.number_input("추적 손절 가격 ($)", value=stop_price)
        stop_price = trailing_stop

if st.button("기록 저장"):
    log_trade(
        symbol=selected,
        entry_price=entry_price,
        stop_price=stop_price,
        leverage=leverage,
        risk_ratio=risk_ratio,
        profit=profit
    )
    st.success("기록 저장 완료!")

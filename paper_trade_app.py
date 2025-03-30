# paper_trade_app.py (가상매매 전용 - 총 자산 파일 분리 + 포지션 금액 입력)
import streamlit as st
import os
import pandas as pd
from calculator import calculate_stop_loss_price
from logger import log_paper_trade
from asset_manager import get_paper_asset, update_paper_asset

st.set_page_config(
    page_title="Hadol’s 가상 리스크 계산기",
    page_icon="📘",
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

st.title("📘 Hadol’s 가상 리스크 계산기 (Paper Trading)")

total_asset = get_paper_asset()
st.sidebar.subheader(f"💰 가상 총 자산: ${total_asset:,}")

# 사용자 입력 기반 가상 포지션 설정
symbol = st.text_input("종목 티커 입력", value="BTCUSDT")
entry_price = st.number_input("진입 가격 ($)", value=27000.0)
leverage = st.number_input("레버리지", min_value=1, max_value=125, value=10)
position_usd = st.number_input("포지션 금액 ($)", value=500.0)
position_amt = position_usd / entry_price if entry_price > 0 else 0

risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
risk_result = calculate_stop_loss_price(
    total_asset, position_amt, leverage, risk_ratio, entry_price
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
col3.metric("가상 총 자산", f"${total_asset:,}")

with st.expander("익절 처리"):
    profit = st.number_input("익절 금액 ($)", value=0.0)
    if profit > 0:
        percent_closed = st.slider("청산 비율 (%)", 1, 100, 50)
        realized = profit * (percent_closed / 100)
        new_asset = update_paper_asset(realized)
        st.success(f"가상 자산이 ${realized:,.2f} 증가하여 총 자산은 ${new_asset:,.2f}가 되었습니다.")
        trailing_stop = st.number_input("추적 손절 가격 ($)", value=stop_price)
        stop_price = trailing_stop

if st.button("기록 저장"):
    log_paper_trade(
        symbol=symbol,
        entry_price=entry_price,
        stop_price=stop_price,
        leverage=leverage,
        risk_ratio=risk_ratio,
        profit=profit
    )
    st.success("가상 거래 기록 저장 완료!")

# 📥 기록 다운로드 및 미리보기
if os.path.exists("paper_trade_log.csv"):
    with open("paper_trade_log.csv", "r") as f:
        csv_data = f.read()

    st.download_button(
        label="📥 가상 거래 기록 다운로드 (CSV)",
        data=csv_data,
        file_name="paper_trade_log.csv",
        mime="text/csv"
    )

    df = pd.read_csv("paper_trade_log.csv", header=None)
    df.columns = ["날짜", "종목", "진입가", "손절가", "레버리지", "리스크비율", "이익"]
    st.subheader("📄 최근 가상 거래 내역")
    st.dataframe(df.tail(10))

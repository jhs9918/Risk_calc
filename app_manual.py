# app_manual.py
import streamlit as st
from calculator import calculate_stop_loss_price
from logger import log_trade
from asset_manager import get_total_asset, update_total_asset

st.set_page_config(
    page_title="💹 실전 리스크 계산기 (수동 입력)",
    page_icon="📊",
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

st.title("📊 실전 리스크 계산기 (수동 입력, 단위: $)")

# 현재 총 자산 표시
total_asset = get_total_asset()
st.sidebar.subheader(f"💰 총 자산: ${total_asset:,}")

# 수동 포지션 입력
symbol = st.text_input("종목 티커", value="BTCUSDT")
entry_price = st.number_input("진입 가격 ($)", min_value=0.0, format="%.6f", value=27000.0)
position_amt = st.number_input("포지션 금액 ($)", min_value=0.0, value=500.0)
leverage = st.number_input("레버리지", min_value=1, max_value=125, value=10)
direction = st.radio("포지션 방향", ["LONG", "SHORT"])

# 리스크 비율 및 손절가 계산
risk_ratio = st.slider("리스크 비율 (%)", 0.1, 10.0, 2.0) / 100
risk_result = calculate_stop_loss_price(
    total_asset, position_amt / entry_price, leverage, risk_ratio, entry_price
)
suggested_stop = risk_result["손절 가격"]

# 손절가 입력 방식 선택
stop_price_method = st.radio("손절가 입력 방식", ["자동", "수동"])
if stop_price_method == "자동":
    stop_price = suggested_stop
else:
    stop_price = st.number_input("직접 손절 가격 입력 ($)", min_value=0.0, format="%.6f", value=suggested_stop)
    # 손실 계산
    price_diff = entry_price - stop_price if direction == "LONG" else stop_price - entry_price
    loss_amt = price_diff * (position_amt / entry_price) * leverage
    risk_pct = (loss_amt / total_asset) * 100 if total_asset > 0 else 0
    sign = "-" if loss_amt > 0 else ""
    st.info(f"⚠️ 손실 예상: {sign}${abs(loss_amt):,.2f} → 자산 대비 {sign}{abs(risk_pct):.2f}%")

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("손절 가격", f"${stop_price:,.2f}")
col2.metric("리스크 비율", f"{risk_ratio*100:.2f}%")
col3.metric("총 자산", f"${total_asset:,}")

# 익절 처리
with st.expander("익절 처리"):
    profit = st.number_input("익절 금액 ($)", value=0.0)
    if profit > 0:
        percent_closed = st.slider("청산 비율 (%)", 1, 100, 50)
        realized = profit * (percent_closed / 100)
        new_asset = update_total_asset(realized)
        st.success(f"총 자산이 ${realized:,.2f} 증가하여 ${new_asset:,.2f}가 되었습니다.")
        remaining_pct = 100 - percent_closed
        st.info(f"📈 남은 포지션: {remaining_pct}%")

# 기록 저장
if st.button("기록 저장"):
    log_trade(
        symbol=symbol,
        entry_price=entry_price,
        stop_price=stop_price,
        leverage=leverage,
        risk_ratio=risk_ratio,
        profit=profit
    )
    st.success("✅ 기록 저장 완료!")
